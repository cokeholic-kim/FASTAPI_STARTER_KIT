"""Observability helpers for logging and correlation IDs."""

from collections.abc import Mapping
import re
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict, Generator, Optional
from urllib.parse import parse_qsl, urlencode

import structlog.contextvars


SENSITIVE_FIELDS = {
    "password",
    "passwd",
    "pwd",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "api_key",
    "secret",
    "secret_key",
    "password_hash",
    "email",
}

_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


def new_correlation_id() -> str:
    return str(uuid.uuid4())


def bind_correlation_context(**fields: Any) -> None:
    normalized = dict(fields)
    correlation_id = normalized.get("correlation_id")
    if not correlation_id:
        normalized["correlation_id"] = new_correlation_id()
        correlation_id = normalized["correlation_id"]

    _correlation_id.set(correlation_id)
    normalized.setdefault("request_id", correlation_id)
    normalized.setdefault("trace_id", correlation_id)
    structlog.contextvars.bind_contextvars(**normalized)


def clear_correlation_context() -> None:
    structlog.contextvars.clear_contextvars()


def get_correlation_context() -> Dict[str, Any]:
    return dict(structlog.contextvars.get_contextvars())


@contextmanager
def correlation_context(
    request_id: str,
    *,
    source: str = "request",
    **fields: Any,
) -> Generator[None, None, None]:
    payload = {"request_id": request_id, "correlation_id": request_id, "source": source}
    payload.update(fields)
    bind_correlation_context(**payload)
    try:
        yield
    finally:
        clear_correlation_context()


def batch_context(
    job_name: str,
    *,
    correlation_id: Optional[str] = None,
    **fields: Any,
) -> Generator[None, None, None]:
    corr_id = correlation_id or new_correlation_id()
    payload = {"correlation_id": corr_id, "job_name": job_name, "source": "batch"}
    payload.update(fields)
    bind_correlation_context(**payload)
    try:
        yield
    finally:
        clear_correlation_context()


def _mask_email(value: str) -> str:
    local, _, domain = value.partition("@")
    if not domain:
        return "***"
    if len(local) <= 2:
        return "***@" + domain
    return f"{local[:2]}***@***"


_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _mask_token(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}***{value[-4:]}"


def sanitize_value(value: Any, field_name: Optional[str] = None) -> Any:
    if isinstance(value, Mapping):
        return {k: sanitize_value(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [sanitize_value(item) for item in value]
    if isinstance(value, str):
        if field_name and field_name.lower() in SENSITIVE_FIELDS:
            return "***"
        if _EMAIL_PATTERN.match(value):
            return _mask_email(value)
        if len(value) > 32 and "." in value and "-" in value:
            return _mask_token(value)
        return value
    if isinstance(value, (bytes, bytearray)):
        return "***"
    return value


def sanitize_query(query: str) -> str:
    if not query:
        return ""
    params = parse_qsl(query, keep_blank_values=True)
    sanitized = [(key, sanitize_value(value, key)) for key, value in params]
    return urlencode(sanitized, doseq=True)


def sanitize_event_dict(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    return sanitize_value(event_dict)
