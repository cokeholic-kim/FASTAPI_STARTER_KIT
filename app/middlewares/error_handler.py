from typing import Callable

from fastapi import Request, Response

from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.schemas.response import ErrorResponse
from app.utils.observability import sanitize_value

logger = get_logger(__name__)


async def error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """HTTP exception middleware."""
    try:
        response = await call_next(request)
        return response
    except AppException as exc:
        logger.error(
            "AppException occurred",
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.message,
            details=sanitize_value(exc.details),
        )
        return ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            details=sanitize_value(exc.details),
        ).to_response(status_code=exc.status_code)
    except Exception as exc:
        logger.exception("Unhandled exception occurred", exc_info=exc)
        return ErrorResponse(
            error_code="INTERNAL_SERVER_ERROR",
            message="Internal server error occurred",
        ).to_response(status_code=500)
