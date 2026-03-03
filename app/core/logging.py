"""구조화된 로깅 설정"""
import logging
import sys

import structlog
from pythonjsonlogger import jsonlogger

from app.core.config import settings


def setup_logging() -> None:
    """로깅 설정"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 표준 로깅 설정
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.LOG_LEVEL,
    )

    # JSON 로거 설정
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(jsonlogger.JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.addHandler(json_handler)
    root_logger.setLevel(settings.LOG_LEVEL)


def get_logger(name: str) -> structlog.BoundLogger:
    """로거 인스턴스 반환"""
    return structlog.get_logger(name)
