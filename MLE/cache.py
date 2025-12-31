
import redis
import json
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class PredictionCache:
    def __init__(self, host='localhost', port=6379, db=0, ttl=3600):
        """
        Initialize Redis connection.
        ttl: Time to live in seconds (default 1 hour)
        """
        self.ttl = ttl
        self.enabled = False
        try:
            self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.redis.ping()
            self.enabled = True
            logger.info(f"✅ Redis connected successfully at {host}:{port}")
        except redis.ConnectionError:
            logger.warning("⚠️ Redis connection failed. Caching will be disabled.")
            self.redis = None

    def _get_key(self, ticker: str, insample_hash: str) -> str:
        """Create a unique key based on ticker and input data hash"""
        return f"pred:{ticker.upper()}:{insample_hash}"

    def get_forecast(self, ticker: str, data: List[float]) -> Optional[List[float]]:
        if not self.enabled:
            return None
        
        # Simple hash of the input data to ensure we return cache only for same input
        data_hash = hash(tuple(data))
        key = self._get_key(ticker, str(data_hash))
        
        try:
            val = self.redis.get(key)
            if val:
                logger.info(f"⚡ Cache hit for {ticker}")
                return json.loads(val)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            
        return None

    def set_forecast(self, ticker: str, data: List[float], forecast: List[float]):
        if not self.enabled:
            return
            
        data_hash = hash(tuple(data))
        key = self._get_key(ticker, str(data_hash))
        
        try:
            self.redis.setex(key, self.ttl, json.dumps(forecast))
            logger.debug(f"💾 Cached forecast for {ticker}")
        except Exception as e:
            logger.error(f"Redis set error: {e}")
