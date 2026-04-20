import logging
import time
from collections.abc import Callable

from fastapi import Request, Response

logger = logging.getLogger("heart.api")


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    logger.info("%s %s %s %sms", request.method, request.url.path, response.status_code, elapsed_ms)
    return response
