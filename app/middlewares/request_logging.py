import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response

from app.utils.observability import bind_correlation_context, clear_correlation_context, sanitize_query

logger = structlog.get_logger(__name__)


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    """Request/response logging middleware with request_id and latency."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    bind_correlation_context(
        request_id=request_id,
        source="http",
        method=request.method,
        path=str(request.url.path),
    )

    start = time.perf_counter()
    response = None

    try:
        response = await call_next(request)
    finally:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        status_code = response.status_code if response is not None else 500
        client_host = request.client.host if request.client else None

        if response is not None:
            response.headers["X-Request-ID"] = request_id

        query_string = sanitize_query(str(request.url.query)) if request.url.query else None

        if status_code >= 500:
            logger.error(
                "http.request",
                status_code=status_code,
                duration_ms=duration_ms,
                method=request.method,
                path=str(request.url.path),
                query=query_string,
                client_host=client_host,
            )
        elif status_code >= 400:
            logger.warning(
                "http.request",
                status_code=status_code,
                duration_ms=duration_ms,
                method=request.method,
                path=str(request.url.path),
                query=query_string,
                client_host=client_host,
            )
        else:
            logger.info(
                "http.request",
                status_code=status_code,
                duration_ms=duration_ms,
                method=request.method,
                path=str(request.url.path),
                query=query_string,
                client_host=client_host,
            )

        clear_correlation_context()

    return response
