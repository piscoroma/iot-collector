from prometheus_client import CollectorRegistry, Gauge

from iot_collector.domain.sensor_state import SensorState


class Metrics:
    """Manage Prometheus metrics for sensor readings."""

    def __init__(self, registry: CollectorRegistry | None = None):
        self.registry = registry or CollectorRegistry()

        self.temperature = Gauge(
            "room_temperature_celsius",
            "Current room temperature in Celsius",
            ["room"],
            registry=self.registry,
        )

        self.humidity = Gauge(
            "room_humidity_percent",
            "Current room relative humidity percentage",
            ["room"],
            registry=self.registry,
        )

        self.last_seen = Gauge(
            "room_last_seen_timestamp_seconds",
            "Unix timestamp of the last sensor update",
            ["room"],
            registry=self.registry,
        )

        self.packet_sequence = Gauge(
            "room_packet_sequence",
            "Last received packet sequence number",
            ["room"],
            registry=self.registry,
        )

    def update(self, state: SensorState) -> None:
        """Update Prometheus metrics with the latest sensor state."""

        room = state.reading.device_id

        self.temperature.labels(room=room).set(state.reading.temperature)

        self.humidity.labels(room=room).set(state.reading.humidity)

        self.last_seen.labels(room=room).set(state.last_seen.timestamp())

        self.packet_sequence.labels(room=room).set(state.reading.sequence)
