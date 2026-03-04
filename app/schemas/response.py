"""Common API response schemas."""
from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response envelope."""

    success: bool = Field(default=True, description="요청 성공 여부")
    message: str = Field(default="성공", description="메시지")
    data: Optional[T] = Field(default=None, description="응답 데이터")

    def to_response(self, status_code: int = 200) -> JSONResponse:
        """Build JSONResponse from model dump."""
        return JSONResponse(
            status_code=status_code,
            content=self.model_dump(exclude_none=True, mode="json"),
        )


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    success: bool = Field(default=False, description="요청 성공 여부")
    error_code: str = Field(description="에러 코드")
    message: str = Field(description="에러 메시지")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="추가 상세 정보",
    )

    def to_response(self, status_code: int = 500) -> JSONResponse:
        """Build JSONResponse from model dump."""
        return JSONResponse(
            status_code=status_code,
            content=self.model_dump(exclude_none=True, mode="json"),
        )

