import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from iot_collector.api.dependencies import get_sensor_manager
from iot_collector.api.routes.sensors import router as sensors_router
from iot_collector.metrics import Metrics
from iot_collector.sensor_manager import SensorManager


@pytest.fixture
def sensor_manager():
    metrics = Metrics()

    return SensorManager(
        metrics=metrics,
        stale_timeout=180,
    )


@pytest.fixture
def client(sensor_manager):
    app = FastAPI()
    app.include_router(sensors_router)

    app.dependency_overrides[get_sensor_manager] = lambda: sensor_manager

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
