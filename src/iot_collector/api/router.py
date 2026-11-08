from fastapi import APIRouter

from iot_collector.api.routes import health, ingestion, metrics, sensors

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(ingestion.router, tags=["ingestion"])
api_router.include_router(sensors.router, tags=["sensors"])
api_router.include_router(metrics.router)
