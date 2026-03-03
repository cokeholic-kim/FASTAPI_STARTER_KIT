"""헬스 체크 컨트롤러"""
from fastapi import APIRouter

from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> SuccessResponse[dict]:
    """헬스 체크 엔드포인트"""
    return SuccessResponse(
        message="애플리케이션이 정상 작동 중입니다",
        data={"status": "healthy"},
    ).to_response(status_code=200)
