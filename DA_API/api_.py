"""
DataAgent API - Technical Analysis Microservice
Port: 8003
Returns JSON data for interactive Plotly charts
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import yfinance as yf
import pandas as pd
import numpy as np
import logging
import requests
from datetime import timedelta, datetime

import os

MLE_API_URL = os.getenv("MLE_API_URL", "http://localhost:8002/predict")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DataAgent API",
    description="Technical Analysis & Chart Data Service",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# SCHEMAS
# =====================================================

class AnalyzeRequest(BaseModel):
    ticker: str
    period: str = "1y"

class ChartData(BaseModel):
    dates: List[str]
    open: Optional[List[float]] = None
    high: Optional[List[float]] = None
    low: Optional[List[float]] = None
    close: List[float]
    volume: Optional[List[float]] = None

class RSIData(BaseModel):
    dates: List[str]
    values: List[float]
    current: float
    signal: str

class MACDData(BaseModel):
    dates: List[str]
    macd_line: List[float]
    signal_line: List[float]
    histogram: List[float]
    signal: str

class BollingerData(BaseModel):
    dates: List[str]
    upper: List[float]
    middle: List[float]
    lower: List[float]
    close: List[float]

class MAData(BaseModel):
    dates: List[str]
    close: List[float]
    ma20: List[float]
    ma50: List[float]
    ma200: List[float]

class AnalyzeResponse(BaseModel):
    ticker: str
    success: bool
    technical_summary: Optional[str] = None
    error: Optional[str] = None
    statistics: Optional[Dict[str, Any]] = None
    chart_data: Optional[Dict[str, Any]] = None

# =====================================================
# CORE ANALYSIS FUNCTIONS
# =====================================================

def fetch_data(ticker: str, period: str) -> pd.DataFrame:
    """Fetch OHLCV data from yfinance"""
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data

def calculate_rsi(data: pd.DataFrame, period: int = 14) -> Dict:
    """Calculate RSI indicator"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    current_rsi = float(rsi.iloc[-1]) if not rsi.empty else 50
    
    if current_rsi > 70:
        signal = "overbought"
    elif current_rsi < 30:
        signal = "oversold"
    else:
        signal = "neutral"
    
    return {
        "dates": data.index.strftime('%Y-%m-%d').tolist(),
        "values": [float(v) if not pd.isna(v) else 50 for v in rsi.tolist()],
        "current": current_rsi,
        "signal": signal
    }

def calculate_macd(data: pd.DataFrame) -> Dict:
    """Calculate MACD indicator"""
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line
    
    current_hist = float(histogram.iloc[-1])
    prev_hist = float(histogram.iloc[-2])
    
    if current_hist > 0 and prev_hist <= 0:
        signal = "bullish_crossover"
    elif current_hist < 0 and prev_hist >= 0:
        signal = "bearish_crossover"
    else:
        signal = "neutral"
    
    return {
        "dates": data.index.strftime('%Y-%m-%d').tolist(),
        "macd_line": [float(v) if not pd.isna(v) else 0 for v in macd_line.tolist()],
        "signal_line": [float(v) if not pd.isna(v) else 0 for v in signal_line.tolist()],
        "histogram": [float(v) if not pd.isna(v) else 0 for v in histogram.tolist()],
        "signal": signal
    }

def calculate_bollinger(data: pd.DataFrame, window: int = 20, num_std: int = 2) -> Dict:
    """Calculate Bollinger Bands"""
    ma = data['Close'].rolling(window=window).mean()
    std = data['Close'].rolling(window=window).std()
    
    upper = ma + (num_std * std)
    lower = ma - (num_std * std)
    
    return {
        "dates": data.index.strftime('%Y-%m-%d').tolist(),
        "upper": [float(v) if not pd.isna(v) else 0 for v in upper.tolist()],
        "middle": [float(v) if not pd.isna(v) else 0 for v in ma.tolist()],
        "lower": [float(v) if not pd.isna(v) else 0 for v in lower.tolist()],
        "close": data['Close'].tolist()
    }

def calculate_moving_averages(data: pd.DataFrame) -> Dict:
    """Calculate MA20, MA50"""
    ma20 = data['Close'].rolling(window=20).mean()
    ma50 = data['Close'].rolling(window=50).mean()
    
    return {
        "dates": data.index.strftime('%Y-%m-%d').tolist(),
        "close": data['Close'].tolist(),
        "ma20": [float(v) if not pd.isna(v) else None for v in ma20.tolist()],
        "ma50": [float(v) if not pd.isna(v) else None for v in ma50.tolist()]
    }

def calculate_drawdown(data: pd.DataFrame) -> Dict:
    """Calculate drawdown - % drop from peak"""
    close = data['Close']
    running_max = close.cummax()
    drawdown = ((close - running_max) / running_max) * 100
    
    max_drawdown = drawdown.min()
    
    return {
        "dates": data.index.strftime('%Y-%m-%d').tolist(),
        "drawdown": drawdown.tolist(),
        "max_drawdown": round(float(max_drawdown), 2)
    }

def calculate_cumulative_returns(data: pd.DataFrame) -> Dict:
    """Calculate cumulative returns"""
    returns = data['Close'].pct_change()
    cumulative = (1 + returns).cumprod() - 1
    cumulative = cumulative * 100  # Convert to percentage
    
    total_return = cumulative.iloc[-1]
    
    return {
        "dates": data.index.strftime('%Y-%m-%d').tolist(),
        "cumulative": cumulative.tolist(),
        "total_return": round(float(total_return), 2)
    }

def calculate_statistics(data: pd.DataFrame) -> Dict:
    """Calculate summary statistics"""
    close = data['Close']
    returns = close.pct_change().dropna()
    
    return {
        "current_price": float(close.iloc[-1]),
        "start_price": float(close.iloc[0]),
        "change_pct": float((close.iloc[-1] / close.iloc[0] - 1) * 100),
        "min_price": float(close.min()),
        "max_price": float(close.max()),
        "avg_volume": float(data['Volume'].mean()),
        "volatility_annual": float(returns.std() * np.sqrt(252) * 100),
        "sharpe_ratio": float(returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0,
        "data_points": len(close)
    }

def get_forecast(ticker: str, data: List[float]) -> List[float]:
    """Call MLE API to get forecast"""
    try:
        # Ensure data is simple list of floats
        payload = {
            "ticker": ticker,
            "data": [float(x) for x in data]
        }
        response = requests.post(MLE_API_URL, json=payload, timeout=5)
        if response.status_code == 200:
            return response.json().get("forecast", [])
        else:
            logger.error(f"MLE API Error: {response.text}")
            return []
    except Exception as e:
        logger.error(f"MLE API Connection Error: {e}")
        return []

def generate_future_dates(start_date_str: str, days: int) -> List[str]:
    """Generate future business dates"""
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    future_dates = []
    current_date = start_date
    while len(future_dates) < days:
        current_date += timedelta(days=1)
        # Skip weekends (5=Sat, 6=Sun)
        if current_date.weekday() < 5:
            future_dates.append(current_date.strftime('%Y-%m-%d'))
    return future_dates

def build_summary(ticker: str, stats: Dict, rsi: Dict, macd: Dict) -> str:
    """Build text summary"""
    return f"""
{ticker} Technical Summary:
• Price: ${stats['start_price']:.2f} → ${stats['current_price']:.2f} ({stats['change_pct']:+.1f}%)
• RSI: {rsi['current']:.1f} ({rsi['signal']})
• MACD: {macd['signal']}
• Volatility: {stats['volatility_annual']:.1f}% (annual)
• Sharpe Ratio: {stats['sharpe_ratio']:.2f}
""".strip()

# =====================================================
# ENDPOINTS
# =====================================================

@app.get("/")
async def root():
    return {"service": "DataAgent API", "version": "1.0.0", "port": 8003}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Full technical analysis with chart data for Plotly rendering
    """
    ticker = request.ticker.upper()
    logger.info(f"Analyzing {ticker} with period {request.period}")
    
    try:
        # Fetch data
        data = fetch_data(ticker, request.period)
        
        if data is None or len(data) < 60:
            return AnalyzeResponse(
                ticker=ticker,
                success=False,
                error="Insufficient data (need at least 60 data points)"
            )
        
        # Calculate all indicators
        rsi = calculate_rsi(data)
        macd = calculate_macd(data)
        bollinger = calculate_bollinger(data)
        ma = calculate_moving_averages(data)
        drawdown = calculate_drawdown(data)
        cumulative_returns = calculate_cumulative_returns(data)
        stats = calculate_statistics(data)
        
        # Build candlestick data
        candlestick = {
            "dates": data.index.strftime('%Y-%m-%d').tolist(),
            "open": data['Open'].tolist(),
            "high": data['High'].tolist(),
            "low": data['Low'].tolist(),
            "close": data['Close'].tolist(),
            "volume": data['Volume'].tolist()
        }
        
        # Returns distribution
        returns = data['Close'].pct_change().dropna()
        returns_data = {
            "values": returns.tolist()
        }
        
        # ==========================================
        # FORECASTING (VALIDATION & FUTURE)
        # ==========================================
        forecast_data = {
            "validation": {"dates": [], "actual": [], "predicted": []},
            "future": {"dates": [], "predicted": []}
        }
        
        close_prices = data['Close'].tolist()
        dates = data.index.strftime('%Y-%m-%d').tolist()
        
        # 1. Validation Forecast (Predict last 30 days using prior 60)
        # Need at least 90 days total: 60 input + 30 target
        if len(close_prices) >= 90:
            # Inputs: prices from -90 to -30
            input_val = close_prices[-90:-30]
            # Targets: prices from -30 to end
            target_val = close_prices[-30:]
            target_dates = dates[-30:]
            
            # Call MLE
            val_pred = get_forecast(ticker, input_val)
            
            if val_pred:
                # Calculate MAE (Mean Absolute Error)
                mae = np.mean(np.abs(np.array(target_val) - np.array(val_pred)))
                
                forecast_data["validation"] = {
                    "dates": target_dates,
                    "actual": target_val,
                    "predicted": val_pred,
                    "full_dates": dates,
                    "full_actual": close_prices,
                    "mae": round(float(mae), 2)
                }
        
        # 2. Future Forecast (Predict next 30 days using last 60)
        if len(close_prices) >= 60:
            input_future = close_prices[-60:]
            last_date = dates[-1]
            
            # Call MLE
            future_pred = get_forecast(ticker, input_future)
            
            if future_pred:
                future_dates = generate_future_dates(last_date, len(future_pred))
                
                # Use MAE from validation for confidence intervals
                mae_value = forecast_data.get("validation", {}).get("mae", 0)
                
                forecast_data["future"] = {
                    "dates": future_dates,
                    "predicted": future_pred,
                    "predicted_upper": [p + mae_value for p in future_pred],  # Optimistic
                    "predicted_lower": [p - mae_value for p in future_pred],  # Pessimistic
                    "history": close_prices[-60:],
                    "history_dates": dates[-60:],
                    "mae": mae_value
                }
        
        # Build response
        
        # Build response
        return AnalyzeResponse(
            ticker=ticker,
            success=True,
            technical_summary=build_summary(ticker, stats, rsi, macd),
            statistics=stats,
            chart_data={
                "candlestick": candlestick,
                "rsi": rsi,
                "macd": macd,
                "bollinger": bollinger,
                "moving_averages": ma,
                "drawdown": drawdown,
                "cumulative_returns": cumulative_returns,
                "returns": returns_data,
                "forecast": forecast_data
            }
        )
        
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return AnalyzeResponse(
            ticker=ticker,
            success=False,
            error=str(e)
        )

# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8006))
    uvicorn.run(app, host="0.0.0.0", port=port)
