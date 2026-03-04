import logging
import sys

import structlog
import structlog.contextvars
from pythonjsonlogger.json import JsonFormatter

from app.core.config import settings
from app.utils.observability import sanitize_event_dict


def setup_logging() -> None:
    """Configure application logging."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.contextvars.merge_contextvars,
            sanitize_event_dict,
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

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.LOG_LEVEL,
    )

    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    if not any(isinstance(handler, logging.StreamHandler) for handler in root_logger.handlers):
        root_logger.addHandler(json_handler)
    root_logger.setLevel(settings.LOG_LEVEL)


def get_logger(name: str) -> structlog.BoundLogger:
    """Return a structured logger."""
    return structlog.get_logger(name)
