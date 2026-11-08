from dataclasses import dataclass
from datetime import datetime

from iot_collector.schemas.sensor_reading import SensorReading


@dataclass(frozen=True)
class SensorState:
    """Current state of a sensor."""

    reading: SensorReading
    last_seen: datetime
