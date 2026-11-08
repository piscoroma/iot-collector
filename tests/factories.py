from iot_collector.schemas.sensor_reading import SensorReading


def create_reading(
    device_id: str = "camera",
    sequence: int = 1,
    temperature: float = 21.5,
    humidity: float = 55.2,
) -> SensorReading:
    return SensorReading(
        device_id=device_id,
        sequence=sequence,
        temperature=temperature,
        humidity=humidity,
    )
