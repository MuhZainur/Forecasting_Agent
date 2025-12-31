
import os
import time
import logging
# IMPORTS: NeuralForecast MUST be imported before pandas/yfinance to avoid DLL load errors
from neuralforecast import NeuralForecast
from neuralforecast.models import NBEATS
import pandas as pd
import yfinance as yf
import torch
import numpy as np
import shutil
from datetime import datetime, timedelta

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
TICKERS = ["NVDA", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AAPL", "AMD", "INTC", "TSM"]

# Determine base directory (one level up from this script)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "MLE", "models")
HISTORY_YEARS = 2 # Training windowm this script)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "MLE", "models")
HISTORY_YEARS = 2 # Training window

def fetch_data(ticker):
    """Fetch last N years of data from yfinance"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=HISTORY_YEARS*365)
    
    logger.info(f"Fetching data for {ticker}...")
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    
    if df.empty:
        raise ValueError(f"No data found for {ticker}")
        
    df = df.reset_index()
    # NeuralForecast expects columns: ds, y, unique_id
    data = pd.DataFrame()
    data['ds'] = df['Date']
    data['y'] = df['Close']
    data['unique_id'] = ticker
    
    return data

def train_model(data, ticker):
    """Train N-BEATS model on data"""
    logger.info(f"Training N-BEATS for {ticker}...")
    
    # Model Configuration (Same as DS Phase)
    model = NBEATS(
        h=30, # Forecast horizon
        input_size=60, # Lookback window
        loss=NBEATS.mae,
        max_steps=500, # Fast retraining
        scaler_type='standard',
        enable_progress_bar=True
    )
    
    nf = NeuralForecast(models=[model], freq='D')
    nf.fit(df=data)
    return nf

def save_model(nf, ticker):
    """Save model to disk with versioning"""
    # 1. Save 'latest' version for API
    save_path = os.path.join(MODELS_DIR, f"{ticker}_nbeats.pkl")
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    nf.save(save_path, model_index=None, overwrite=True, save_dataset=False)
    logger.info(f"💾 Model saved to {save_path}")
    
    # 2. Save 'versioned' backup (Simulated artifact store)
    # In real MLOps, this would go to S3/MLFlow
    date_str = datetime.now().strftime("%Y%m%d")
    backup_path = os.path.join(MODELS_DIR, "archive", f"{ticker}_nbeats_{date_str}.pkl")
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    
    # NeuralForecast save is a directory structure or pickle depending on usage.
    # The .save method of NeuralForecast saves a directory.
    # Our API expects a pickle of the wrapper or specific handling.
    # Let's check how the API loads it. 
    # API uses: `model_data = CPU_Unpickler(f).load()`
    # If NeuralForecast.save() creates a folder, we might need to pickle the object manually 
    # OR adjust the API to load from folder.
    # The DS notebook likely used `pickle.dump`. Let's stick to that for compatibility.
    
    import pickle
    with open(save_path, 'wb') as f:
        pickle.dump(nf, f)
        
    shutil.copy(save_path, backup_path)
    logger.info(f"📦 Backup created at {backup_path}")

def main():
    logger.info("🚀 Starting Daily Retraining Pipeline")
    
    for ticker in TICKERS:
        try:
            # 1. Data Ingestion
            data = fetch_data(ticker)
            
            # 2. Training
            nf_model = train_model(data, ticker)
            
            # 3. Model Registry (Local)
            save_model(nf_model, ticker)
            
            logger.info(f"✅ Successfully updated {ticker}")
            
        except Exception as e:
            logger.error(f"❌ Failed to retrain {ticker}: {e}")
            
    logger.info("🎉 Pipeline Finished")

if __name__ == "__main__":
    main()
