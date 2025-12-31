from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    google_api_key: str
    tavily_api_key: Optional[str] = None
    
    # Model Configuration (Default to latest stable/experimental)
    # Users can override these in .env if models are deprecated or changed
    google_model_vision: str = "gemini-1.5-flash"
    google_model_thinking: str = "gemini-2.0-flash-thinking-exp-01-21"
    
    # Stock API
    stock_api_url: str = "http://localhost:8002"
    
    # App
    debug: bool = True
    log_level: str = "INFO"
    
    # Memory
    max_messages: int = 20
    
    # ChromaDB
    chroma_persist_dir: str = "./chroma_db"
    
    class Config:
        env_file = ".env"

settings = Settings()
