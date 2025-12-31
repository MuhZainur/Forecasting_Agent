
import os
import shutil
import logging
# IMPORT FIX: NeuralForecast first
from neuralforecast import NeuralForecast
from neuralforecast.models import NBEATS
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pickle

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODELS_DIR = r"H:\coding\Portfolio\Stock_Forecasting\MLE\models"
os.makedirs(MODELS_DIR, exist_ok=True)

def test_pipeline():
    ticker = "NVDA"
    logger.info(f"🧪 Testing pipeline for {ticker}...")
    
    # 1. Fetch small data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=100)
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    df = df.reset_index()
    data = pd.DataFrame()
    data['ds'] = df['Date']
    data['y'] = df['Close']
    data['unique_id'] = ticker
    
    # 2. Train tiny model
    model = NBEATS(
        h=5,
        input_size=10,
        max_steps=1, # One step only
        scaler_type='standard'
    )
    nf = NeuralForecast(models=[model], freq='D')
    nf.fit(df=data)
    
    # 3. Save
    save_path = os.path.join(MODELS_DIR, f"TEST_{ticker}_nbeats.pkl")
    with open(save_path, 'wb') as f:
        pickle.dump(nf, f)
    
    logger.info(f"✅ Saved to {save_path}")
    
    # 4. Verify Load (Simulation of API)
    with open(save_path, 'rb') as f:
        loaded = pickle.load(f)
    logger.info(f"✅ Loaded back successfully: {type(loaded)}")

if __name__ == "__main__":
    test_pipeline()
