import asyncio
import math
import time
from typing import Any, Literal

from iot_collector.prometheus_api import PrometheusClient
from iot_collector.schemas.history import HistoryPoint, HistoryResponse

HistoryRange = Literal["1h", "6h", "24h", "7d"]

RANGE_SECONDS: dict[HistoryRange, int] = {
    "1h": 60 * 60,
    "6h": 6 * 60 * 60,
    "24h": 24 * 60 * 60,
    "7d": 7 * 24 * 60 * 60,
}

# Prometheus is usually scraped every 15s; asking for a smaller step only
# duplicates samples and makes range queries unnecessarily expensive.
MIN_STEP_SECONDS = 15

TEMPERATURE_METRIC = "room_temperature_celsius"
HUMIDITY_METRIC = "room_humidity_percent"


def compute_step(range_seconds: int, points: int) -> int:
    """Return a Prometheus step that yields approximately ``points`` samples."""

    return max(MIN_STEP_SECONDS, math.ceil(range_seconds / max(points, 1)))


def escape_label_value(value: str) -> str:
    """Escape a value used inside a PromQL double-quoted label matcher."""

    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def build_metric_query(metric: str, device_id: str) -> str:
    """Build an exact-match selector for a metric and device."""

    return f'{metric}{{room="{escape_label_value(device_id)}"}}'


def parse_matrix(result: list[dict[str, Any]]) -> list[HistoryPoint]:
    """Convert a Prometheus matrix into sorted, finite history points."""

    values_by_timestamp: dict[int, float] = {}

    for series in result:
        if not isinstance(series, dict):
            continue

        values = series.get("values")
        if not isinstance(values, list):
            continue

        for sample in values:
            if not isinstance(sample, (list, tuple)) or len(sample) != 2:
                continue

            try:
                timestamp = int(float(sample[0]))
                value = float(sample[1])
            except (TypeError, ValueError):
                continue

            if not math.isfinite(value):
                continue

            values_by_timestamp[timestamp] = value

    return [
        HistoryPoint(timestamp=timestamp, value=values_by_timestamp[timestamp])
        for timestamp in sorted(values_by_timestamp)
    ]


async def collect_history(
    client: PrometheusClient,
    device_id: str,
    range_name: HistoryRange,
    points: int,
    now: float | None = None,
) -> HistoryResponse:
    """Query Prometheus for the temperature and humidity series."""

    range_seconds = RANGE_SECONDS[range_name]
    end = int(time.time() if now is None else now)
    start = end - range_seconds
    step = compute_step(range_seconds, points)

    temperature_result, humidity_result = await asyncio.gather(
        client.query_range(
            build_metric_query(TEMPERATURE_METRIC, device_id),
            start,
            end,
            step,
        ),
        client.query_range(
            build_metric_query(HUMIDITY_METRIC, device_id),
            start,
            end,
            step,
        ),
    )

    return HistoryResponse(
        device_id=device_id,
        range=range_name,
        temperature=parse_matrix(temperature_result),
        humidity=parse_matrix(humidity_result),
    )
