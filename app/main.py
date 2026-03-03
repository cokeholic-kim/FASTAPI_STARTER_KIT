"""FastAPI 애플리케이션 메인 파일"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.middlewares.error_handler import error_handler_middleware
from app.controllers import health

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI Starter Kit",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 에러 핸들러 미들웨어
app.middleware("http")(error_handler_middleware)

# 라우트 등록
app.include_router(health.router, tags=["health"])


@app.on_event("startup")
async def startup_event() -> None:
    """애플리케이션 시작 이벤트"""
    pass


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """애플리케이션 종료 이벤트"""
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
