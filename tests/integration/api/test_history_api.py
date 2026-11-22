import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from iot_collector.api.dependencies import get_prometheus_client
from iot_collector.api.routes.history import router
from iot_collector.prometheus_api import PrometheusError


class FakePrometheusClient:
    async def query_range(self, query, start, end, step):
        if "temperature" in query:
            return [{"values": [[1000, "21.2"], [1060, "21.3"]]}]

        return [{"values": [[1000, "54.8"], [1060, "55.0"]]}]


class EmptyPrometheusClient:
    async def query_range(self, query, start, end, step):
        return []


class FailingPrometheusClient:
    async def query_range(self, query, start, end, step):
        raise PrometheusError("upstream down")


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_prometheus_client] = FakePrometheusClient

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_get_history(client):
    response = client.get(
        "/history",
        params={"device_id": "camera", "range": "6h", "points": 60},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["device_id"] == "camera"
    assert data["range"] == "6h"
    assert data["temperature"] == [
        {"timestamp": 1000, "value": 21.2},
        {"timestamp": 1060, "value": 21.3},
    ]
    assert data["humidity"] == [
        {"timestamp": 1000, "value": 54.8},
        {"timestamp": 1060, "value": 55.0},
    ]


def test_get_history_rejects_invalid_range(client):
    response = client.get(
        "/history",
        params={"device_id": "camera", "range": "5h"},
    )

    assert response.status_code == 422


def test_get_history_rejects_invalid_points(client):
    response = client.get(
        "/history",
        params={"device_id": "camera", "range": "1h", "points": 0},
    )

    assert response.status_code == 422


def test_get_history_returns_empty_series_for_unknown_device(client):
    client.app.dependency_overrides[get_prometheus_client] = EmptyPrometheusClient

    response = client.get(
        "/history",
        params={"device_id": "unknown", "range": "1h"},
    )

    assert response.status_code == 200
    assert response.json()["temperature"] == []
    assert response.json()["humidity"] == []


def test_get_history_returns_503_when_prometheus_fails(client):
    client.app.dependency_overrides[get_prometheus_client] = FailingPrometheusClient

    response = client.get(
        "/history",
        params={"device_id": "camera", "range": "1h"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "History backend unavailable"
