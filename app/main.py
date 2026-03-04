from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.core.config import settings
from app.core.logging import setup_logging
from app.middlewares.error_handler import error_handler_middleware
from app.middlewares.request_logging import request_logging_middleware
from app.middlewares.metrics import metrics_middleware
from app.controllers import health, observability, users
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI Starter Kit",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(request_logging_middleware)
app.middleware("http")(error_handler_middleware)

if settings.PROMETHEUS_ENABLED:
    app.middleware("http")(metrics_middleware)

    @app.get("/metrics")
    async def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

app.include_router(health)
app.include_router(users)
app.include_router(observability)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
