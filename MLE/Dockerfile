# MLE Service Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies (might take time for torch/neuralforecast)
RUN pip install --no-cache-dir -r requirements.txt

# Copy model files from DS/models to container
COPY ../DS/models ./models

# Copy API code
COPY . .

EXPOSE 8002

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8002"]
