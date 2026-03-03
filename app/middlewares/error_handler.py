"""에러 핸들링 미들웨어"""
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.schemas.response import ErrorResponse

logger = get_logger(__name__)


async def error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """에러 핸들링 미들웨어"""
    try:
        response = await call_next(request)
        return response
    except AppException as exc:
        logger.error(
            "애플리케이션 예외",
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.message,
        )
        return ErrorResponse(
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        ).to_response()
    except Exception as exc:
        logger.exception("예상 외 예외", exc_info=exc)
        return ErrorResponse(
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR",
            message="서버 오류가 발생했습니다",
        ).to_response()
