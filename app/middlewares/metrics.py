from collections import Counter as InMemoryCounter
from threading import RLock
from time import perf_counter
from typing import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Gauge, Histogram


_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests.",
    ["method", "path", "status_code"],
)

_request_latency_seconds = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency in seconds.",
    ["method", "path"],
)

_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of requests in progress.",
    ["method", "path"],
)

_request_stats_lock = RLock()
_request_count_by_path = InMemoryCounter()
_request_count_by_status = InMemoryCounter()
_request_failures_by_path = InMemoryCounter()

_METRICS_EXCLUDED_PATHS = (
    "/metrics",
    "/observability/health",
    "/observability/request-metadata",
)


def _request_path(request: Request) -> str:
    route = request.scope.get("route")
    if route is not None:
        route_path = getattr(route, "path", None)
        if isinstance(route_path, str):
            return route_path
    return request.url.path


def _is_internal_metrics_path(path: str) -> bool:
    if path.startswith("/observability"):
        return True
    return path in _METRICS_EXCLUDED_PATHS


def get_request_metrics_snapshot() -> dict:
    with _request_stats_lock:
        return {
            "total_requests": sum(_request_count_by_status.values()),
            "path_total": dict(_request_count_by_path),
            "status_total": dict(_request_count_by_status),
            "failure_total": dict(_request_failures_by_path),
        }


async def metrics_middleware(request: Request, call_next: Callable) -> Response:
    """Collect Prometheus metrics for every HTTP request."""
    method = request.method
    path = _request_path(request)

    if _is_internal_metrics_path(path):
        return await call_next(request)

    label = dict(method=method, path=path)

    _requests_in_progress.labels(**label).inc()
    start = perf_counter()

    status_code = 500
    response = None
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration = perf_counter() - start
        duration_label = dict(method=method, path=path)
        status_label = dict(method=method, path=path, status_code=str(status_code))

        _request_latency_seconds.labels(**duration_label).observe(duration)
        _requests_total.labels(**status_label).inc()
        _requests_in_progress.labels(**label).dec()

        with _request_stats_lock:
            _request_count_by_path[path] += 1
            _request_count_by_status[str(status_code)] += 1
            if status_code >= 500:
                _request_failures_by_path[path] += 1
