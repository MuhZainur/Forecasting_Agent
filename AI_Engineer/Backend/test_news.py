import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from app.llm_client import llm_client

async def test_news():
    print("Testing News Generation (DeepSeek + Web Plugin)...")
    
    ticker = "NVDA"
    print(f"\nFetching news for: {ticker}")
    
    try:
        report = await llm_client.generate_market_report(ticker)
        print("\nReport Received:")
        print(report)
        print("\nSUCCESS: Web Plugin is working!")
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_news())
