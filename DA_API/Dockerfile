# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some pandas/numpy/scipy)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1

# Expose port (Internal container port)
EXPOSE 8006

# Command to run the application
# Note: Using shell form to allow variable expansion if needed, but array form is safer.
# IMPORTANT: File is named 'api_.py' so module is 'api_'
# We use 'sh -c' to expand $PORT variable provided by Cloud Run
CMD sh -c "uvicorn api_:app --host 0.0.0.0 --port ${PORT:-8006}"
