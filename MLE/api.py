
import os
import io
import pickle
import torch
import torch.nn as nn
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- PERFORMANCE TUNING ---
# Critical for high-concurrency: Prevent PyTorch from using all cores per request
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["TORCH_NUM_THREADS"] = "1"

# --- MODEL LOADER UTILS ---
class CPU_Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == 'torch.storage' and name == '_load_from_bytes':
            return lambda b: torch.load(io.BytesIO(b), map_location='cpu')
        else:
            return super().find_class(module, name)

def get_model_path(ticker: str):
    return os.path.join("../DS/models", f"{ticker}_nbeats.pkl")

# --- SCHEMAS ---
class PredictionRequest(BaseModel):
    ticker: str = Field(..., example="NVDA", description="Stock ticker symbol")
    # For future: could add horizon or data input here
    # For now, we'll assume we fetch the latest 60 days via yfinance or similar
    # But for a pure inference API, let's accept the input data (insample_y)
    data: List[float] = Field(..., min_items=60, max_items=60, description="Last 60 days of Close prices")

class PredictionResponse(BaseModel):
    ticker: str
    forecast: List[float]
    model_version: str = "N-BEATS-FP32"

# --- APP SETUP ---
app = FastAPI(
    title="Stock Forecasting API",
    description="Production-grade API for stock price forecasting using N-BEATS",
    version="1.0.0"
)

# CORS - Allow all origins for microservices communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model cache (lazy loading)
model_cache = {}

def load_model_for_ticker(ticker: str):
    if ticker in model_cache:
        return model_cache[ticker]
    
    path = get_model_path(ticker)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model for {ticker} not found at {path}")
    
    logger.info(f"Loading model for {ticker}...")
    with open(path, 'rb') as f:
        model_data = CPU_Unpickler(f).load()
    
    # Extract model from NeuralForecast wrapper if needed
    if isinstance(model_data, dict):
        model = model_data.get('model') or model_data
    else:
        model = model_data
        
    if hasattr(model, 'models'):
        core_model = model.models[0]
    else:
        core_model = model
        
    core_model.eval()
    core_model.to('cpu')
    model_cache[ticker] = core_model
    return core_model

# --- PROMETHEUS SETUP ---
from prometheus_middleware import PrometheusMiddleware, metrics_endpoint, PREDICTION_COUNTER

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics_endpoint)

# --- ENDPOINTS ---
@app.get("/")
async def root():
    return {"message": "Stock Forecasting API is online", "docs": "/docs", "metrics": "/metrics"}

@app.get("/health")
async def health():
    return {"status": "healthy", "loaded_models": list(model_cache.keys())}
    
# --- CACHE SETUP ---
from cache import PredictionCache
cache = PredictionCache()

# --- ASYNC HELPERS ---
from starlette.concurrency import run_in_threadpool

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    ticker = request.ticker.upper()
    
    # 1. Check Cache
    cached_forecast = cache.get_forecast(ticker, request.data)
    if cached_forecast:
        PREDICTION_COUNTER.labels(ticker=ticker, model_version="cached").inc()
        return PredictionResponse(
            ticker=ticker,
            forecast=cached_forecast,
            model_version="N-BEATS-FP32-CACHED"
        )
        
    try:
        # Load model (can be blocking IO, run in threadpool if it becomes slow, 
        # but for now caching handles it. N-BEATS load is fast-ish once in memory?)
        # Actually load_model_for_ticker is blocking too if it hits disk.
        # But let's verify if we need to offload that.
        # model_cache is global dict, so it's fast.
        model = load_model_for_ticker(ticker)
    except FileNotFoundError:
        PREDICTION_COUNTER.labels(ticker=ticker, model_version="error_not_found").inc()
        raise HTTPException(status_code=404, detail=f"Model for ticker {ticker} not found")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        PREDICTION_COUNTER.labels(ticker=ticker, model_version="error_load").inc()
        raise HTTPException(status_code=500, detail="Internal error loading model")
    
    try:
        # Prepare input
        # N-BEATS expects (Batch, Seq, 1) and (Batch, Seq, 1) for mask
        insample_y = torch.tensor(request.data).float().view(1, 60, 1)
        insample_mask = torch.ones(1, 60, 1)
        
        batch = {
            'insample_y': insample_y,
            'insample_mask': insample_mask
        }
        
        # OFF-LOAD CPU BOUND INFERENCE TO THREADPOOL
        # This prevents blocking the main Async Event Loop
        with torch.no_grad():
            forecast = await run_in_threadpool(model, batch) # Returns (1, Horizon)
        
        forecast_list = forecast.squeeze().tolist()
        
        # 2. Set Cache
        cache.set_forecast(ticker, request.data, forecast_list)
        
        PREDICTION_COUNTER.labels(ticker=ticker, model_version="N-BEATS-FP32").inc()
            
        return PredictionResponse(
            ticker=ticker,
            forecast=forecast_list
        )
        
    except Exception as e:
        logger.error(f"Prediction failed for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

if __name__ == "__main__":
    import uvicorn
    # Use port 8002 to avoid conflicts
    uvicorn.run(app, host="0.0.0.0", port=8002)
