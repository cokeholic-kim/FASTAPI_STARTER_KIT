"""커스텀 예외 클래스"""
from typing import Any, Dict, Optional


class AppException(Exception):
    """기본 애플리케이션 예외"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(AppException):
    """검증 예외"""

    def __init__(
        self,
        message: str = "검증 실패",
        error_code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_code=error_code,
            details=details,
        )


class NotFound(AppException):
    """리소스 없음 예외"""

    def __init__(
        self,
        message: str = "리소스를 찾을 수 없습니다",
        error_code: str = "NOT_FOUND",
    ) -> None:
        super().__init__(
            message=message,
            status_code=404,
            error_code=error_code,
        )


class UnauthorizedException(AppException):
    """인증 없음 예외"""

    def __init__(
        self,
        message: str = "인증이 필요합니다",
        error_code: str = "UNAUTHORIZED",
    ) -> None:
        super().__init__(
            message=message,
            status_code=401,
            error_code=error_code,
        )


class ForbiddenException(AppException):
    """권한 없음 예외"""

    def __init__(
        self,
        message: str = "접근 권한이 없습니다",
        error_code: str = "FORBIDDEN",
    ) -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code=error_code,
        )


class DuplicateException(AppException):
    """중복 예외"""

    def __init__(
        self,
        message: str = "이미 존재하는 리소스입니다",
        error_code: str = "DUPLICATE",
    ) -> None:
        super().__init__(
            message=message,
            status_code=409,
            error_code=error_code,
        )
