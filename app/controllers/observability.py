from fastapi import APIRouter

from app.middlewares.metrics import get_request_metrics_snapshot
from app.schemas.response import SuccessResponse
from app.schemas.observability import RequestMetadataResponse

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/health", status_code=200)
async def observability_health() -> SuccessResponse[dict]:
    return SuccessResponse(
        message="observability service is ready",
        data={"status": "ready"},
    ).to_response(status_code=200)


@router.get("/request-metadata", status_code=200)
async def request_metadata() -> SuccessResponse[RequestMetadataResponse]:
    payload = RequestMetadataResponse(**get_request_metrics_snapshot())
    return SuccessResponse(
        message="request metadata snapshot",
        data=payload,
    ).to_response(status_code=200)
