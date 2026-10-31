# Stock Market Forecasting & AI Agent Platform 📈

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)]()
[![Vue.js](https://img.shields.io/badge/Frontend-Vue.js-4FC08D?style=flat-square&logo=vue.js&logoColor=white)]()
[![OpenRouter](https://img.shields.io/badge/AI-OpenRouter-7F52FF?style=flat-square&logo=openai&logoColor=white)]()
[![DeepSeek](https://img.shields.io/badge/Reasoning-DeepSeek%20v3.2-1C58F2?style=flat-square)]()
[![Mistral](https://img.shields.io/badge/Vision-Mistral%203B-FD6F00?style=flat-square)]()
[![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)]()

**🔴 LIVE DEMO:**
[**🚀 Launch StockMind AI Dashboard**](https://forecasting-agent-6dly.vercel.app)

An End-to-End AI-Powered Stock Forecasting & Analysis Platform. This project transforms raw market data into actionable insights using deep learning (NeuralForecast) and state-of-the-art Reasoning AI (DeepSeek R1/v3 via OpenRouter).

---

## 🏗️ Architecture Overview

This project simulates a professional AI Engineering workflow, executed in **5 Production Phases**:

### Phase 1: Data Analytics (DA) 📊
*   **Goal:** Visualize complex technical indicators and market trends.
*   **Analysis:** RSI, MACD, Bollinger Bands, Moving Averages.
*   **Deliverable:** Interactive Plotly Charts via `DA_API`.

### Phase 2: Data Science (DS) 🧠
*   **Goal:** Research and train robust predictive models for time-series forecasting.
*   **Model:** **NeuralForecast (N-BEATS/NHITS)** - Specialized deep learning architecture for time series.
*   **Methodology:**
    *   Hyperparameter tuning on historical stock data.
    *   Feature engineering (lags, rolling windows).
    *   Validation splitting to prevent look-ahead bias.
*   **Deliverable:** Optimized model artifacts (`.pth`, `.pkl`).

### Phase 3: ML Engineering (MLE) ⚙️
*   **Goal:** Deploy the model into a production-grade inference service.
*   **Service:** Dedicated **FastAPI** microservice (Port 8002).
*   **Features:**
    *   Low-latency inference endpoint (`/predict`).
    *   Dynamic model loading.
    *   Standardized Input/Output schema.

### Phase 4: AI Agent Engineering (Reasoning & Vision) 🤖
*   **Goal:** Create an autonomous market analyst agent that can "See" and "Think".
*   **Backend:** **FastAPI** service (Port 8005) acting as the "Brain", powered by **OpenRouter**.
*   **Capabilities:**
    *   **Reasoning Agent:** Uses **DeepSeek v3.2** (with Thinking enabled) to answer complex financial questions and analyze market sentiment.
    *   **Vision Agent:** Uses **Mistral 3B (Ministral)** to technically analyze stock charts (support/resistance, patterns) from images.
    *   **Agent Search:** Uses **OpenRouter Web Plugin (Exa)** for real-time market news scouting (On-demand).
    *   **Hybrid Architecture:** Automatically switches between Vision, Search, and Reasoning modes based on user input.

### Phase 5: DevOps & Deployment 🐳
*   **Goal:** Ensure scalability and ease of deployment.
*   **Containerization:** Full Docker support for all 4 microservices.
*   **Orchestration:** `docker-compose` for one-click local deployment.

---

## 💻 Tech Stack

| Component | Technologies |
| :--- | :--- |
| **Data Science** | Python 3.10, NeuralForecast, Pandas, NumPy, Scikit-Learn |
| **AI Brain** | **OpenRouter** (DeepSeek v3.2, Mistral 3B, Exa Search Plugin) |
| **Backend API** | FastAPI, Uvicorn, Python-Multipart, Pydantic |
| **Frontend UI** | Vue.js 3, Vite, Tailwind CSS, Plotly.js |
| **Infrastructure** | Docker, Docker Compose, Redis (Planned) |

---

## 🚀 Deployment & Access

The application is deployed on **Vercel** (Vue.js 3 Frontend) and **Render** (Unified FastAPI Backend).

### 🔗 Live Services
*   **Frontend Dashboard:** [https://forecasting-agent-6dly.vercel.app](https://forecasting-agent-6dly.vercel.app)
*   **Unified API (Swagger):** [https://forecasting-agent-1.onrender.com/docs](https://forecasting-agent-1.onrender.com/docs)



---

## 📂 Project Structure

```
├── MLE/                  # Phase 2 & 3: Model & Inference
│   ├── api.py            
│   ├── models/           # Trained Artifacts (.pth/.pkl)
│   └── Dockerfile
├── DA_API/               # Phase 1: Technical Analysis
│   ├── api.py            
│   └── Dockerfile
├── AI_Engineer/          # Phase 4: AI Agent & UI 
│   ├── Backend/          # Reasoning Chat Service (OpenRouter)
│   │   ├── app/          
│   │   └── Dockerfile    
│   └── Frontend/         # Vue.js Dashboard
│       └── Dockerfile
├── docker-compose.yml    # Phase 5: Orchestration
└── README.md             # Project Documentation
```

---

*Created by **[MuhZainur]** - AI Engineer & Data Scientist*
