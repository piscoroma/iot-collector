import logging
import time

from fastapi import Request

logger = logging.getLogger("iot_collector.http")

EXCLUDED_PATHS = {
    "/metrics",
    "/health",
}


async def request_logging_middleware(request: Request, call_next):
    if request.url.path in EXCLUDED_PATHS:
        return await call_next(request)

    start_time = time.perf_counter()
    device_id = None

    if request.method == "POST" and request.url.path == "/ingestion":
        try:
            body = await request.json()
            device_id = body.get("device_id")
        except (ValueError, AttributeError):
            pass

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

    if device_id:
        logger.info(
            "%s %s device_id=%s - %d (%.2f ms)",
            request.method,
            request.url.path,
            device_id,
            response.status_code,
            duration,
        )
    else:
        logger.info(
            "%s %s - %d (%.2f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

    return response