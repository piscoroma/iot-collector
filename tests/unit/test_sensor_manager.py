from datetime import UTC, timedelta

from tests.factories import create_reading

from iot_collector.metrics import Metrics
from iot_collector.sensor_manager import SensorManager


def test_update_sensor():
    sensor_manager = SensorManager(metrics=Metrics())

    state = sensor_manager.update(create_reading())

    assert state.reading.device_id == "camera"
    assert state.reading.temperature == 21.5
    assert state.reading.humidity == 55.2
    assert state.last_seen.tzinfo == UTC


def test_update_existing_sensor():
    sensor_manager = SensorManager(metrics=Metrics())

    sensor_manager.update(create_reading())

    updated_reading = create_reading()
    updated_reading = updated_reading.model_copy(
        update={
            "sequence": 2,
            "temperature": 22.0,
        }
    )

    sensor_manager.update(updated_reading)

    state = sensor_manager.get_sensor("camera")

    assert state.reading.sequence == 2
    assert state.reading.temperature == 22.0


def test_get_sensor_not_found():
    sensor_manager = SensorManager(metrics=Metrics())

    assert sensor_manager.get_sensor("unknown") is None


def test_get_all_sensors():
    sensor_manager = SensorManager(metrics=Metrics())

    sensor_manager.update(create_reading("camera"))
    sensor_manager.update(create_reading("bagno"))

    sensors = sensor_manager.get_all_sensors()

    assert len(sensors) == 2
    assert "camera" in sensors
    assert "bagno" in sensors


def test_sensor_not_found_is_stale():
    sensor_manager = SensorManager(metrics=Metrics())

    assert sensor_manager.is_stale("unknown") is True


def test_sensor_becomes_stale():
    sensor_manager = SensorManager(
        metrics=Metrics(),
        stale_timeout=180,
    )

    state = sensor_manager.update(create_reading())

    now = state.last_seen + timedelta(seconds=181)

    assert sensor_manager.is_stale("camera", now=now) is True


def test_sensor_is_not_stale():
    sensor_manager = SensorManager(
        metrics=Metrics(),
        stale_timeout=180,
    )

    state = sensor_manager.update(create_reading())

    now = state.last_seen + timedelta(seconds=60)

    assert sensor_manager.is_stale("camera", now=now) is False


def test_sensor_is_not_stale_at_timeout():
    sensor_manager = SensorManager(
        metrics=Metrics(),
        stale_timeout=180,
    )

    state = sensor_manager.update(create_reading())

    now = state.last_seen + timedelta(seconds=180)

    assert sensor_manager.is_stale("camera", now=now) is False
