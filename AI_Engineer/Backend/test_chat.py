import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from app.llm_client import llm_client

async def test_chat():
    print("Testing Chat Agent (DeepSeek via OpenRouter)...")
    
    question = "Apa dampak kenaikan suku bunga The Fed terhadap saham bank di Indonesia?"
    print(f"\nQuestion: {question}")
    
    try:
        response = await llm_client.answer_question(question=question)
        print("\nResponse Received:")
        print(response)
        print("\nSUCCESS: Chat Agent is working!")
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())
