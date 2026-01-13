import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from app.config import settings
from app.llm_client import llm_client

async def test_vision():
    print(f"DEBUG: ENV OPENROUTER_API_KEY: {os.getenv('OPENROUTER_API_KEY')}")
    print(f"DEBUG: SETTINGS openrouter_api_key: {settings.openrouter_api_key}")
    
    print("Testing Vision Agent (OpenRouter)...")
    
    # Load dummy image or use a tiny 1x1 pixel base64
    # 1x1 red pixel
    dummy_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKwjwAAAAABJRU5ErkJggg=="
    
    try:
        response = await llm_client.analyze_chart(dummy_image)
        print("\nResponse Received:")
        print(response)
        print("\nSUCCESS: Vision Agent is working!")
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_vision())
