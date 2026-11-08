from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from iot_collector.api.dependencies import get_sensor_manager
from iot_collector.schemas.sensor_response import SensorResponse
from iot_collector.sensor_manager import SensorManager

router = APIRouter(prefix="/sensors")


@router.get("", response_model=list[SensorResponse])
async def get_sensors(
    sensor_manager: Annotated[
        SensorManager,
        Depends(get_sensor_manager),
    ],
):
    sensors = sensor_manager.get_all_sensors()

    return [
        SensorResponse(
            device_id=device_id,
            sequence=state.reading.sequence,
            temperature=state.reading.temperature,
            humidity=state.reading.humidity,
            last_seen=state.last_seen,
            is_stale=sensor_manager.is_stale(device_id),
        )
        for device_id, state in sensors.items()
    ]


@router.get("/{device_id}", response_model=SensorResponse)
async def get_sensor(
    device_id: str,
    sensor_manager: Annotated[
        SensorManager,
        Depends(get_sensor_manager),
    ],
):
    state = sensor_manager.get_sensor(device_id)

    if state is None:
        raise HTTPException(
            status_code=404,
            detail=f"Sensor '{device_id}' not found",
        )

    return SensorResponse(
        device_id=device_id,
        sequence=state.reading.sequence,
        temperature=state.reading.temperature,
        humidity=state.reading.humidity,
        last_seen=state.last_seen,
        is_stale=sensor_manager.is_stale(device_id),
    )
