from datetime import UTC, datetime

from prometheus_client import generate_latest
from tests.factories import create_reading

from iot_collector.domain.sensor_state import SensorState
from iot_collector.metrics import Metrics


def get_metric_value(output: str, metric_name: str, room: str) -> float:
    for line in output.splitlines():
        if line.startswith(f'{metric_name}{{room="{room}"}} '):
            return float(line.split()[-1])

    raise AssertionError(
        f"Metric {metric_name} for room {room} not found"
    )

def test_update_metrics():
    metrics = Metrics()

    state = SensorState(
        reading=create_reading(),
        last_seen=datetime(2026, 1, 1, tzinfo=UTC),
    )

    metrics.update(state)

    output = generate_latest(metrics.registry).decode("utf-8")

    assert 'room_temperature_celsius{room="camera"} 21.5' in output
    assert 'room_humidity_percent{room="camera"} 55.2' in output
    assert 'room_packet_sequence{room="camera"} 1.0' in output
    expected_timestamp = datetime(
        2026, 1, 1, tzinfo=UTC
    ).timestamp()
    assert get_metric_value(
        output,
        "room_last_seen_timestamp_seconds",
        "camera",
    ) == expected_timestamp


def test_update_existing_room_metrics():
    metrics = Metrics()

    first_state = SensorState(
        reading=create_reading(),
        last_seen=datetime(2026, 1, 1, tzinfo=UTC),
    )

    updated_state = SensorState(
        reading=create_reading(
            sequence=2,
            temperature=23.0,
            humidity=60.0,
        ),
        last_seen=datetime(2026, 1, 1, 0, 1, tzinfo=UTC),
    )

    metrics.update(first_state)
    metrics.update(updated_state)

    output = generate_latest(metrics.registry).decode("utf-8")

    assert 'room_temperature_celsius{room="camera"} 23.0' in output
    assert 'room_humidity_percent{room="camera"} 60.0' in output
    assert 'room_packet_sequence{room="camera"} 2.0' in output
    expected_timestamp = datetime(
        2026, 1, 1, 0, 1, tzinfo=UTC
    ).timestamp()
    assert get_metric_value(
        output,
        "room_last_seen_timestamp_seconds",
        "camera",
    ) == expected_timestamp


def test_update_multiple_rooms_metrics():
    metrics = Metrics()

    camera_state = SensorState(
        reading=create_reading(device_id="camera"),
        last_seen=datetime(2026, 1, 1, tzinfo=UTC),
    )

    bagno_state = SensorState(
        reading=create_reading(
            device_id="bagno",
            temperature=22.0,
            humidity=65.0,
        ),
        last_seen=datetime(2026, 1, 1, 0, 1, tzinfo=UTC),
    )

    metrics.update(camera_state)
    metrics.update(bagno_state)

    output = generate_latest(metrics.registry).decode("utf-8")

    assert 'room_temperature_celsius{room="camera"} 21.5' in output
    assert 'room_temperature_celsius{room="bagno"} 22.0' in output

    assert 'room_humidity_percent{room="camera"} 55.2' in output
    assert 'room_humidity_percent{room="bagno"} 65.0' in output
