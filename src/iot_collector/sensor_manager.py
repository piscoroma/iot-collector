from datetime import UTC, datetime

from iot_collector.domain.sensor_state import SensorState
from iot_collector.metrics import Metrics
from iot_collector.schemas.sensor_reading import SensorReading


class SensorManager:
    """Manage the in-memory state of connected sensors."""

    def __init__(self, metrics: Metrics, stale_timeout: int = 180):

        self._metrics = metrics
        self._sensors: dict[str, SensorState] = {}
        self._stale_timeout = stale_timeout

    def update(self, reading: SensorReading) -> SensorState:
        """Update the state of a sensor with a new reading."""

        state = SensorState(
            reading=reading,
            last_seen=datetime.now(UTC),
        )

        self._sensors[reading.device_id] = state

        self._metrics.update(state)

        return state

    def get_sensor(self, device_id: str) -> SensorState | None:
        """Return the current state of a sensor."""

        return self._sensors.get(device_id)

    def get_all_sensors(self) -> dict[str, SensorState]:
        """Return the current state of all sensors."""

        return self._sensors.copy()

    def is_stale(
        self,
        device_id: str,
        now: datetime | None = None,
    ) -> bool:
        """Check whether a sensor has stopped sending updates."""

        state = self.get_sensor(device_id)

        if state is None:
            return True

        current_time = now or datetime.now(UTC)
        elapsed = (current_time - state.last_seen).total_seconds()

        return elapsed > self._stale_timeout
