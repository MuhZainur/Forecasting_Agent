from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from app.chat_service import process_chat
from app.memory import memory
from app.gemini_client import gemini_client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Stock Analysis Chat AI",
    description="Hybrid chat system with JSON context and Vision analysis",
    version="2.0"
)

# CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    ticker: str
    message: str
    technical_data: Optional[Dict[str, Any]] = None
    forecast_screenshot: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    mode: str
    processing_time: float

@app.get("/")
async def root():
    return {
        "service": "Stock Analysis Chat AI",
        "version": "2.0",
        "status": "online"
    }

@app.get("/health")
async def health():
    stats = memory.get_stats()
    return {
        "status": "healthy",
        "memory_stats": stats
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with hybrid processing"""
    logger.info(f"Chat request for {request.ticker}: {request.message[:50]}...")
    
    result = await process_chat(
        ticker=request.ticker,
        message=request.message,
        technical_data=request.technical_data,
        forecast_screenshot=request.forecast_screenshot
    )
    
    return ChatResponse(**result)

@app.delete("/memory/{ticker}")
async def clear_memory(ticker: str):
    """Clear conversation memory for a ticker"""
    memory.clear(ticker)
    return {"message": f"Memory cleared for {ticker}"}

@app.get("/news/{ticker}")
async def get_market_news(ticker: str):
    """Trigger Agent Search to get latest market news"""
    news_report = await gemini_client.generate_market_report(ticker)
    return {"ticker": ticker, "news": news_report}


@app.on_event("startup")
async def startup_event():
    logger.info("Stock Analysis Chat AI starting up...")
    logger.info("Hybrid mode: JSON for technical, Vision for forecast")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Stock Analysis Chat AI shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005, log_level="info")
