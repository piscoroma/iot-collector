from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from iot_collector.api.request_log_mw import request_logging_middleware
from iot_collector.api.router import api_router
from iot_collector.core.config import get_settings
from iot_collector.core.logging import setup_logging
from iot_collector.metrics import Metrics
from iot_collector.sensor_manager import SensorManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    settings = get_settings()
    metrics = Metrics()
    sensor_manager = SensorManager(
        metrics=metrics,
        stale_timeout=settings.sensor_stale_timeout,
    )
    app.state.metrics = metrics
    app.state.sensor_manager = sensor_manager

    yield

    # clean resources


app = FastAPI(
    title="IOT collector",
    version="0.1.0",
    lifespan=lifespan,
)

app.middleware("http")(request_logging_middleware)

app.include_router(api_router)


def main() -> None:
    settings = get_settings()

    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
        log_level=settings.log_level.lower(),
        access_log=False,
    )


if __name__ == "__main__":
    main()
