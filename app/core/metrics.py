import re
from time import perf_counter

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

HTTP_REQUESTS = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status_code"]
)
HTTP_DURATION = Histogram(
    "http_request_duration_seconds", "HTTP request duration", ["method", "path"]
)
_TASK_ID_PATH = re.compile(r"^/api/tasks/\d+$")


def metric_path(path: str) -> str:
    if _TASK_ID_PATH.match(path):
        return "/api/tasks/{id}"
    return (
        path if path in {"/", "/health/live", "/health/ready", "/metrics"} else path.split("?")[0]
    )


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        started = perf_counter()
        response = await call_next(request)
        path = metric_path(request.url.path)
        duration = perf_counter() - started
        HTTP_REQUESTS.labels(request.method, path, str(response.status_code)).inc()
        HTTP_DURATION.labels(request.method, path).observe(duration)
        return response
