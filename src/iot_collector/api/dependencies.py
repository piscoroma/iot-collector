from fastapi import Request

from iot_collector.prometheus_api import PrometheusClient
from iot_collector.sensor_manager import SensorManager


def get_sensor_manager(request: Request) -> SensorManager:
    return request.app.state.sensor_manager


def get_prometheus_client(request: Request) -> PrometheusClient:
    return request.app.state.prometheus
