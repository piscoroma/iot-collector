import asyncio

from iot_collector.history import (
    build_metric_query,
    collect_history,
    compute_step,
    escape_label_value,
    parse_matrix,
)


def test_compute_step_for_supported_ranges():
    assert compute_step(3600, 60) == 60
    assert compute_step(6 * 3600, 60) == 360
    assert compute_step(24 * 3600, 60) == 1440
    assert compute_step(7 * 24 * 3600, 60) == 10080


def test_compute_step_respects_minimum_and_single_point():
    assert compute_step(3600, 1000) == 15
    assert compute_step(3600, 1) == 3600


def test_escape_label_value():
    assert escape_label_value('cam"era') == 'cam\\"era'
    assert escape_label_value("cam\\era") == "cam\\\\era"
    assert escape_label_value("cam\nera") == "cam\\nera"


def test_build_metric_query():
    assert (
        build_metric_query("room_temperature_celsius", 'cam"era')
        == 'room_temperature_celsius{room="cam\\"era"}'
    )


def test_parse_matrix_merges_series_and_skips_invalid_values():
    result = [
        {
            "values": [
                [1000.9, "21.2"],
                [1060, "21.3"],
                [1120, "NaN"],
            ]
        },
        {
            "values": [
                [1000, "22.0"],
                [1180, "+Inf"],
                ["bad", "1.0"],
            ]
        },
    ]

    points = parse_matrix(result)

    assert [(point.timestamp, point.value) for point in points] == [
        (1000, 22.0),
        (1060, 21.3),
    ]


class FakePrometheusClient:
    def __init__(self):
        self.calls = []

    async def query_range(self, query, start, end, step):
        self.calls.append(
            {
                "query": query,
                "start": start,
                "end": end,
                "step": step,
            }
        )

        if "temperature" in query:
            return [{"values": [[1000, "21.2"], [1060, "21.3"]]}]

        return [{"values": [[1000, "54.8"], [1060, "55.0"]]}]


def test_collect_history_queries_both_metrics_with_same_window():
    client = FakePrometheusClient()

    response = asyncio.run(
        collect_history(
            client=client,
            device_id='cam"era',
            range_name="6h",
            points=60,
            now=1000000,
        )
    )

    assert response.device_id == 'cam"era'
    assert response.range == "6h"
    assert [point.value for point in response.temperature] == [21.2, 21.3]
    assert [point.value for point in response.humidity] == [54.8, 55.0]

    assert len(client.calls) == 2
    assert {call["query"] for call in client.calls} == {
        'room_temperature_celsius{room="cam\\"era"}',
        'room_humidity_percent{room="cam\\"era"}',
    }
    assert all(call["start"] == 978400 for call in client.calls)
    assert all(call["end"] == 1000000 for call in client.calls)
    assert all(call["step"] == 360 for call in client.calls)
