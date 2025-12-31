# Stock Market Forecasting & AI Agent Platform 📈

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)]()
[![Vue.js](https://img.shields.io/badge/Frontend-Vue.js-4FC08D?style=flat-square&logo=vue.js&logoColor=white)]()
[![Google Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20%2B%203%20Pro-8E75B2?style=flat-square&logo=google-gemini&logoColor=white)]()
[![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)]()

**🔴 LIVE DEMO:**
*   *Coming Soon (Cloud Run / AWS)*

An End-to-End AI-Powered Stock Forecasting & Analysis Platform. This project transforms raw market data into actionable insights using deep learning (NeuralForecast) and generative AI (Gemini Agent).

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

### Phase 4: AI Agent Engineering (GenAI) 🤖
*   **Goal:** Create an autonomous market analyst agent to assist users.
*   **Backend:** **FastAPI** service (Port 8005) acting as the "Brain".
*   **Capabilities:**
    *   **Snippet Mode:** Real-time Google Search Grounding for breaking news (Decoupled & Optimized).
    *   **Vision Mode:** Analyzes chart screenshots for patterns (Double top/bottom, etc.) using Gemini 2.5 Flash.
    *   **JSON Mode:** Answers technical questions with structured data using Gemini 3 Pro.

### Phase 5: DevOps & Deployment 🐳
*   **Goal:** Ensure scalability and ease of deployment.
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
├── MLE/                  # Phase 2 & 3: Model & Inference
│   ├── api.py            
│   ├── models/           # Trained Artifacts (.pth/.pkl)
│   └── Dockerfile
├── DA_API/               # Phase 1: Technical Analysis
│   ├── api.py            
│   └── Dockerfile
├── AI_Engineer/          # Phase 4: AI Agent & UI 
│   ├── Backend/          # Gemini Chat Service
│   │   ├── app/          
│   │   └── Dockerfile    
│   └── Frontend/         # Vue.js Dashboard
│       └── Dockerfile
├── docker-compose.yml    # Phase 5: Orchestration
└── README.md             # Project Documentation
```

---

*Created by **[MuhZainur]** - AI Engineer & Data Scientist*
