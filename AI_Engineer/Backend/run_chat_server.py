import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify API Key
if not os.getenv("GOOGLE_API_KEY"):
    print("WARNING: GOOGLE_API_KEY not found in .env")

print("Starting AI Chat Backend...")
print("=" * 50)
print("Hybrid Mode: JSON + Vision")
print("Port: 8005")
print("=" * 50)

try:
    import uvicorn
    from app.main import app
    
    uvicorn.run(app, host="0.0.0.0", port=8005, log_level="info")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
