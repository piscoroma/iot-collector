import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from iot_collector.api.dependencies import get_sensor_manager
from iot_collector.schemas.sensor_reading import SensorReading
from iot_collector.sensor_manager import SensorManager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ingestion")
async def ingest_sensor_data(
    reading: SensorReading,
    sensor_manager: Annotated[SensorManager, Depends(get_sensor_manager)],
):
    sensor_manager.update(reading)

    return {"status": "accepted"}
