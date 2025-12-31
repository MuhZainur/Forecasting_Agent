
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging

logger = logging.getLogger(__name__)

# --- METRICS DEFINITION ---
REQUEST_TOTAL = Counter(
    "api_requests_total", 
    "Total number of requests", 
    ["method", "endpoint", "status"]
)

LATENCY = Histogram(
    "api_latency_seconds", 
    "Request latency in seconds", 
    ["endpoint"]
)

PREDICTION_COUNTER = Counter(
    "prediction_requests_total",
    "Total prediction requests by ticker",
    ["ticker", "model_version"]
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.perf_counter()
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            process_time = time.perf_counter() - start_time
            
            # Record metrics
            endpoint = request.url.path
            method = request.method
            
            REQUEST_TOTAL.labels(method=method, endpoint=endpoint, status=status_code).inc()
            LATENCY.labels(endpoint=endpoint).observe(process_time)
            
        return response

def metrics_endpoint(request):
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
