
from locust import HttpUser, task, between
import random
import json

class StockForecastUser(HttpUser):
    # Simulate user waiting 1-3 seconds between tasks
    wait_time = between(1, 3)

    @task(3)
    def predict_nvda_cached(self):
        """Simulate frequent requests to a popular ticker (High Cache Hit Rate)"""
        # Fixed data = same hash = Cache Hit
        fixed_data = [0.1] * 60
        payload = {
            "ticker": "NVDA",
            "data": fixed_data
        }
        with self.client.post("/predict", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with {response.status_code}")

    @task(1)
    def predict_random_new_data(self):
        """Simulate a request with new data (Cache Miss / Computation)"""
        # Random data = different hash = Cache Miss = CPU Compute
        random_data = [random.random() for _ in range(60)]
        payload = {
            "ticker": "MSFT",
            "data": random_data
        }
        self.client.post("/predict", json=payload)

    @task(1)
    def health_check(self):
        """Occasional health check"""
        self.client.get("/health")
