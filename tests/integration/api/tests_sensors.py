from iot_collector.schemas.sensor_reading import SensorReading


def test_get_sensors_empty(client):
    response = client.get("/sensors")

    assert response.status_code == 200
    assert response.json() == []


def test_get_sensors(client, sensor_manager):
    sensor_manager.update(
        SensorReading(
            device_id="camera",
            sequence=1,
            temperature=21.5,
            humidity=55.2,
        )
    )

    sensor_manager.update(
        SensorReading(
            device_id="bagno",
            sequence=2,
            temperature=22.1,
            humidity=61.4,
        )
    )

    response = client.get("/sensors")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    camera = next(sensor for sensor in data if sensor["device_id"] == "camera")

    assert camera["sequence"] == 1
    assert camera["temperature"] == 21.5
    assert camera["humidity"] == 55.2
    assert camera["is_stale"] is False
    assert camera["last_seen"] is not None


def test_get_sensor(client, sensor_manager):
    sensor_manager.update(
        SensorReading(
            device_id="camera",
            sequence=1,
            temperature=21.5,
            humidity=55.2,
        )
    )

    response = client.get("/sensors/camera")

    assert response.status_code == 200

    data = response.json()

    assert data["device_id"] == "camera"
    assert data["sequence"] == 1
    assert data["temperature"] == 21.5
    assert data["humidity"] == 55.2
    assert data["is_stale"] is False


def test_get_sensor_not_found(client):
    response = client.get("/sensors/unknown")

    assert response.status_code == 404
    assert response.json()["detail"] == ("Sensor 'unknown' not found")
