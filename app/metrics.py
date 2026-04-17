import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

ERROR_COUNT = Counter(
    "http_errors_total",
    "Total HTTP error responses",
    ["method", "endpoint", "status_code"]
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        path = request.url.path

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        status_code = str(response.status_code)

        REQUEST_COUNT.labels(method=method, endpoint=path, status_code=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)

        if response.status_code >= 400:
            ERROR_COUNT.labels(method=method, endpoint=path, status_code=status_code).inc()

        return response


def metrics_endpoint():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
