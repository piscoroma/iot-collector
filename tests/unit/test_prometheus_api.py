import asyncio

import httpx2
import pytest

from iot_collector.prometheus_api import PrometheusClient, PrometheusError


def run_query(client, query="room_temperature_celsius"):
    async def run():
        try:
            return await client.query_range(
                query=query,
                start=1000,
                end=2000,
                step=60,
            )
        finally:
            await client.aclose()

    return asyncio.run(run())


def test_query_range_sends_expected_request():
    def handler(request):
        assert request.url.path == "/api/v1/query_range"
        assert request.url.params["query"] == "room_temperature_celsius"
        assert request.url.params["start"] == "1000"
        assert request.url.params["end"] == "2000"
        assert request.url.params["step"] == "60"

        return httpx2.Response(
            200,
            json={
                "status": "success",
                "data": {
                    "resultType": "matrix",
                    "result": [{"values": [[1000, "21.2"]]}],
                },
            },
        )

    client = PrometheusClient(
        "http://prometheus:9090/",
        transport=httpx2.MockTransport(handler),
    )

    result = run_query(client)

    assert result == [{"values": [[1000, "21.2"]]}]


def test_query_range_raises_on_error_payload():
    def handler(request):
        return httpx2.Response(
            200,
            json={"status": "error", "error": "bad query"},
        )

    client = PrometheusClient(
        "http://prometheus:9090",
        transport=httpx2.MockTransport(handler),
    )

    with pytest.raises(PrometheusError, match="bad query"):
        run_query(client)


def test_query_range_raises_on_http_error():
    def handler(request):
        return httpx2.Response(500, text="boom")

    client = PrometheusClient(
        "http://prometheus:9090",
        transport=httpx2.MockTransport(handler),
    )

    with pytest.raises(PrometheusError):
        run_query(client)


def test_query_range_raises_on_unexpected_payload():
    def handler(request):
        return httpx2.Response(200, json=["not", "an", "object"])

    client = PrometheusClient(
        "http://prometheus:9090",
        transport=httpx2.MockTransport(handler),
    )

    with pytest.raises(PrometheusError, match="Unexpected Prometheus response"):
        run_query(client)


def test_query_range_raises_on_unexpected_result_type():
    def handler(request):
        return httpx2.Response(
            200,
            json={
                "status": "success",
                "data": {"resultType": "vector", "result": []},
            },
        )

    client = PrometheusClient(
        "http://prometheus:9090",
        transport=httpx2.MockTransport(handler),
    )

    with pytest.raises(PrometheusError, match="Unexpected Prometheus response"):
        run_query(client)
