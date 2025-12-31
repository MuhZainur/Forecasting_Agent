
import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
from datetime import datetime, timedelta

# Page Config
st.set_page_config(
    page_title="Stock N-BEATS Forecaster",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for "Premium" look
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main-title {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-title">🚀 N-BEATS Stock Forecaster</div>', unsafe_allow_html=True)

# Sidebar controls
st.sidebar.header("Configuration")
ticker = st.sidebar.text_input("Ticker Symbol", value="NVDA").upper()
days_to_predict = st.sidebar.slider("Forecast Horizon (Days)", min_value=1, max_value=30, value=30)
api_url = st.sidebar.text_input("API URL", value="http://localhost:8002/predict")

# Main Logic
if st.button("Generate Forecast"):
    with st.spinner(f"Fetching data and forecasting for {ticker}..."):
        try:
            # 1. Get History from YFinance (Last 1 year)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            stock = yf.Ticker(ticker)
            history = stock.history(start=start_date, end=end_date)
            
            if history.empty:
                st.error(f"No data found for {ticker}")
                st.stop()
                
            # Prepare Input for API (Last 60 days of Close)
            if len(history) < 60:
                st.error("Not enough historical data (need at least 60 days)")
                st.stop()
                
            input_data = history['Close'].values[-60:].tolist()
            
            # 2. Call API
            payload = {
                "ticker": ticker,
                "data": input_data
            }
            
            resp = requests.post(api_url, json=payload)
            
            if resp.status_code != 200:
                st.error(f"API Error: {resp.text}")
                st.stop()
                
            prediction = resp.json().get("forecast", [])
            model_ver = resp.json().get("model_version", "Unknown")
            
            # Slice prediction based on slider
            final_forecast = prediction[:days_to_predict]
            
            # 3. Visualization
            last_date = history.index[-1]
            forecast_dates = [last_date + timedelta(days=i+1) for i in range(len(final_forecast))]
            
            # Create Plot
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot History (Last 90 days for clarity)
            plot_history = history.iloc[-90:]
            ax.plot(plot_history.index, plot_history['Close'], label='Actual Price', color='blue', linewidth=2)
            
            # Plot Prediction
            ax.plot(forecast_dates, final_forecast, label='N-BEATS Prediction', color='red', linewidth=2, marker='.', markersize=8)
            
            # connecting line
            ax.plot([plot_history.index[-1], forecast_dates[0]], [plot_history['Close'].iloc[-1], final_forecast[0]], color='red', linestyle='--')
            
            # Highlight Forecast Area
            ax.axvspan(forecast_dates[0], forecast_dates[-1], color='yellow', alpha=0.1, label='Forecast Period')
            ax.axvline(x=last_date, color='green', linestyle=':', label='Forecast Start')
            
            # Styling
            ax.set_title(f"{ticker} Price Forecast - Next {days_to_predict} Days", fontsize=16, fontweight='bold')
            ax.set_ylabel("Price (USD)")
            ax.legend(loc='upper left')
            ax.grid(True, linestyle='--', alpha=0.5)
            
            # Format Date axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.xticks(rotation=45)
            
            st.pyplot(fig)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Price", f"${history['Close'].iloc[-1]:.2f}")
            with col2:
                final_price = final_forecast[-1]
                delta = final_price - history['Close'].iloc[-1]
                st.metric(f"Price in {days_to_predict} Days", f"${final_price:.2f}", f"{delta:.2f}")
            with col3:
                st.info(f"Model: {model_ver}")
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
