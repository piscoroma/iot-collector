import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from iot_collector.api.dependencies import get_prometheus_client
from iot_collector.history import HistoryRange, collect_history
from iot_collector.prometheus_api import PrometheusClient, PrometheusError
from iot_collector.schemas.history import HistoryResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    device_id: Annotated[str, Query(min_length=1, max_length=128)],
    range: Annotated[HistoryRange, Query()],
    prometheus: Annotated[PrometheusClient, Depends(get_prometheus_client)],
    points: Annotated[int, Query(ge=1, le=500)] = 60,
):
    try:
        return await collect_history(
            client=prometheus,
            device_id=device_id,
            range_name=range,
            points=points,
        )
    except PrometheusError as exc:
        logger.exception(
            "Prometheus history query failed for device_id=%s",
            device_id,
        )
        raise HTTPException(
            status_code=503,
            detail="History backend unavailable",
        ) from exc
