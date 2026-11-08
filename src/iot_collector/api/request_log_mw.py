import logging
import time

from fastapi import Request

logger = logging.getLogger("iot_collector.http")

EXCLUDED_PATHS = {
    "/metrics",
}


async def request_logging_middleware(request: Request, call_next):
    if request.url.path in EXCLUDED_PATHS:
        return await call_next(request)

    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration = (time.perf_counter() - start_time) * 1000

        logger.exception(
            "%s %s failed after %.2f ms",
            request.method,
            request.url.path,
            duration,
        )
        raise

    duration = (time.perf_counter() - start_time) * 1000

    logger.info(
        "%s %s - %d (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )

    return response