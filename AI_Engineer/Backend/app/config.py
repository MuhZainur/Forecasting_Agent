import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel
    class BaseSettings(BaseModel):
        class Config:
            extra = "ignore"

class Settings(BaseSettings):
    # API Keys
    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    tavily_api_key: Optional[str] = os.getenv("TAVILY_API_KEY")
    
    # OpenRouter
    openrouter_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    openrouter_model_vision: str = os.getenv("OPENROUTER_MODEL_VISION", "mistralai/ministral-3b-2512")
    openrouter_model_chat: str = os.getenv("OPENROUTER_MODEL_CHAT", "deepseek/deepseek-v3.2")
    
    # Stock API
    stock_api_url: str = os.getenv("STOCK_API_URL", "http://localhost:8002")
    
    # App
    debug: bool = True
    log_level: str = "INFO"
    
    # Memory
    max_messages: int = 20
    chroma_persist_dir: str = "./chroma_db"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
