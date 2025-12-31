import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import tiktoken

logger = logging.getLogger("observability")
logger.setLevel(logging.INFO)

# Tokenizer for rough estimation (using cl100k_base for Gemini/GPT-4 approx)
enc = tiktoken.get_encoding("cl100k_base")

class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        process_time = time.time() - start_time
        
        # Log Metrics
        # Note: We can't easily read body here without consuming stream, 
        # so for exact token counts we usually log inside the router/agent.
        # But we can log latency and status code globally.
        
        logger.info(
            f"METHOD={request.method} PATH={request.url.path} "
            f"STATUS={response.status_code} LATENCY={process_time:.4f}s"
        )
        
        # Add latency header for frontend debugging
        response.headers["X-Process-Time"] = str(process_time)
        return response
