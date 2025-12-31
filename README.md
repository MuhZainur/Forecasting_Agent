# Stock Market Forecasting AI 📈

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)]()
[![Vue.js](https://img.shields.io/badge/Frontend-Vue.js-4FC08D?style=flat-square&logo=vue.js&logoColor=white)]()
[![Google Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash%20%2B%203%20Pro-8E75B2?style=flat-square&logo=google-gemini&logoColor=white)]()
[![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)]()

**🔴 LIVE DEMO:**
*   *Coming Soon (Cloud Run / AWS)*

An End-to-End AI-Powered Stock Forecasting & Analysis Platform. Combines Neural Networks (NeuralForecast) for price prediction with Generative AI (Gemini) for real-time market news analysis and interactive chat.

---

## 🏗️ Architecture Overview

This project simulates a comprehensive AI Engineering workflow, executed in three professional phases:

### Phase 1: Data Analytics (DA) 📊
*   **Goal:** Visualize complex technical indicators and market trends.
*   **Analysis:** RSI, MACD, Bollinger Bands, Moving Averages.
*   **Deliverable:** Interactive Plotly Charts (Frontend).

### Phase 2: ML Engineering (MLE) ⚙️
*   **Goal:** Deploy robust predictive models for time-series forecasting.
*   **Model:** **NeuralForecast** (Deep Learning for Time Series).
*   **Service:** Dedicated FastAPI microservice (Port 8002) for high-performance inference.
*   **Validation:** Backtesting with MAE/RMSE metrics.

### Phase 3: AI Agent Engineering (GenAI) 🤖
*   **Goal:** Create an autonomous market analyst agent.
*   **Backend:** **FastAPI** service (Port 8005) integrating Google Gemini 2.5 Flash & 3 Pro.
*   **Capabilities:**
    *   **Snippet Mode:** Real-time Google Search Grounding for breaking news (Decoupled & Optimized).
    *   **Vision Mode:** Analyzes chart screenshots for patterns (Double top/bottom, etc.).
    *   **JSON Mode:** Answers technical questions with structured data.

### Phase 4: DevOps & Deployment 🐳
*   **Containerization:** Full Docker support for all 4 microservices.
*   **Orchestration:** `docker-compose` for one-click local deployment.

---

## 💻 Tech Stack

| Component | Technologies |
| :--- | :--- |
| **Data Science** | Python 3.10, NeuralForecast, Pandas, NumPy, Scikit-Learn |
| **AI Agent** | Google Gemini (2.5 Flash, 3 Pro), Google Search Grounding |
| **Backend API** | FastAPI, Uvicorn, Python-Multipart, Pydantic |
| **Frontend UI** | Vue.js 3, Vite, Tailwind CSS, Plotly.js |
| **Infrastructure** | Docker, Docker Compose, Redis (Planned) |

---

## 🚀 How to Run (Docker)

The entire application can be launched with a single command using Docker Compose.

### Prerequisites
*   Docker & Docker Compose installed.
*   **API Key**: Create a `.env` file in `AI_Engineer/Backend/` with your `GOOGLE_API_KEY`.

### Steps
1.  **Clone the Repository**
    ```bash
    git clone https://github.com/YourUsername/Stock_Forecasting.git
    cd Stock_Forecasting
    ```

2.  **Launch Application**
    ```bash
    docker-compose up --build
    ```

3.  **Access Services**
    *   **Frontend Dashboard:** http://localhost:5173
    *   **Chat Backend (Swagger):** http://localhost:8005/docs
    *   **Data Agent (Swagger):** http://localhost:8006/docs
    *   **MLE API (Swagger):** http://localhost:8002/docs

---

## 📂 Project Structure

```
├── MLE/                  # Machine Learning Engineering Service
│   ├── api.py            # Forecasting Inference
│   ├── Dockerfile
│   └── models/           # Pre-trained Neural Models
├── DA_API/               # Data Agent Service
│   ├── api.py            # Technical Analysis Logic
│   └── Dockerfile
├── AI_Engineer/          # AI Agent & Frontend 
│   ├── Backend/          # Chat Intelligence (Gemini)
│   │   ├── app/          # Core Logic (Memory, Client, Service)
│   │   └── Dockerfile    
│   └── Frontend/         # Vue.js Dashboard
│       └── Dockerfile
├── docker-compose.yml    # Orchestration
└── README.md             # Project Documentation
```

---

*Created by **[MuhZainur]** - AI Engineer & Data Scientist*
