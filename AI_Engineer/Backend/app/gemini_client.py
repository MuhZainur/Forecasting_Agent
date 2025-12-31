from google import genai
from google.genai import types
import os
import base64
import logging
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

# Initialize Client (New SDK)
# Note: In a real scenario, we'd handle the API key securely.
# Assuming OS environ has GOOGLE_API_KEY
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

class GeminiClient:
    def __init__(self):
        self.vision_model = "gemini-2.5-flash"
        self.chat_model = "gemini-3-pro-preview"
        logger.info(f"Gemini client initialized (Vision: {self.vision_model}, Chat: {self.chat_model} [High Thinking])")
    
    async def analyze_chart(self, image_base64: str) -> str:
        """Vision analysis using Gemini 2.5 Flash (New SDK)"""
        try:
            # Decode base64
            if "," in image_base64:
                image_data = base64.b64decode(image_base64.split(",")[1])
            else:
                image_data = base64.b64decode(image_base64)
            
            prompt = """Analyze this stock forecast chart. Identify:
1. Trend direction (upward/downward/sideways)
2. Confidence band width - are bands widening (low confidence) or tight (high confidence)?
3. Any visual anomalies or concerning patterns
4. Overall reliability based on visual patterns

Be concise and focus on actionable insights."""
            
            # New SDK Call
            response = client.models.generate_content(
                model=self.vision_model,
                contents=[
                    types.Part.from_bytes(
                        data=image_data,
                        mime_type='image/png'
                    ),
                    prompt
                ]
            )
            
            logger.info("Vision analysis completed")
            return response.text
            
        except Exception as e:
            logger.error(f"Vision analysis error: {e}")
            return f"Error analyzing chart: {str(e)}"
    
    async def generate_market_report(self, ticker: str) -> str:
        """Agent Search: Fetch real-time market news using Google Search Grounding"""
        import asyncio
        print(f"DEBUG: Starting Agent Search for {ticker}") # Force console output
        try:
            logger.info(f"Agent Search: Searching news for {ticker}...")
            
            prompt = f"""
            Find exactly ONE most critical breaking news headline for {ticker} stock from the last 24 hours.
            Return ONLY the headline and a 1-sentence summary based on Google Search Snippets.
            Do not click links. Do not analyze. Just extract facts.
            """
            
            # Configure Google Search Tool
            grounding_tool = types.Tool(
                google_search=types.GoogleSearch()
            )
            
            config = types.GenerateContentConfig(
                tools=[grounding_tool]
            )
            
            # Run Agent Search with TIMEOUT
            # Wrapping sync call in thread or using asyncio.to_thread if the SDK is blocking
            # The SDK generate_content is synchronous? No, we used client.models.generate_content which is sync.
            # We need client.aio.models.generate_content for async!
            # WAIT! The new SDK usually has an async client.
            # If I initialized `client = genai.Client(...)`, that's the sync client.
            # I need to check if there is an async client or if I should run it in a thread.
            
            # FIX: Run in threadpool to avoid blocking event loop
            from starlette.concurrency import run_in_threadpool
            
            def _search():
                print("DEBUG: Executing Search API Call...")
                return client.models.generate_content(
                    model=self.vision_model, 
                    contents=prompt,
                    config=config
                )

            # 15 second timeout
            response = await asyncio.wait_for(
                run_in_threadpool(_search),
                timeout=15.0
            )
            
            print("DEBUG: Agent Search Completed")
            logger.info("Agent Search: Report generated")
            return response.text
            
        except asyncio.TimeoutError:
            print(f"DEBUG: Agent Search TIMEOUT for {ticker}")
            logger.error(f"Agent Search timed out for {ticker}")
            return "Market news unavailable (Search Timed Out)"
        except Exception as e:
            print(f"DEBUG: Agent Search ERROR: {e}")
            logger.error(f"Agent Search error: {e}")
            return f"Market news unavailable: {str(e)}"

    async def answer_question(
        self, 
        question: str,
        technical_data: dict = None,
        vision_analysis: str = None,
        news_context: str = None, 
        history: list = []
    ) -> str:
        """Generate answer using Gemini with fallback logic"""
        from starlette.concurrency import run_in_threadpool
        print(f"DEBUG: answer_question called for: {question[:30]}...", flush=True)
        
        try:
            # Build context
            context = self._build_context(technical_data, vision_analysis, news_context, history)
            
            prompt = f"""{context}

User Question: {question}

Provide a clear, data-driven answer in Bahasa Indonesia. 
COMBINE insights from the Technical Data, Visual Chart Analysis, and Market News.
"""
            
            def _generate(model_name):
                print(f"DEBUG: Calling generate_content with {model_name}...", flush=True)
                return client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

            try:
                # Try primary model (Gemini 3 Pro / High Thinking)
                logger.info(f"Generating answer with {self.chat_model}...")
                response = await run_in_threadpool(_generate, self.chat_model)
            except Exception as e:
                logger.warning(f"Primary model {self.chat_model} failed ({e}), falling back to gemini-1.5-pro")
                # Fallback to stable model
                response = await run_in_threadpool(_generate, "gemini-1.5-pro")
            
            logger.info("Answer generated successfully")
            print("DEBUG: Answer generation success", flush=True)
            return response.text
            
        except Exception as e:
            logger.error(f"Answer generation error: {e}")
            return f"Maaf, terjadi error: {str(e)}"
    
    def _build_context(self, technical_data, vision_analysis, news_context, history):
        """Build context string for LLM"""
        parts = ["You are a professional stock analysis AI assistant."]
        
        if news_context:
            parts.append(f"\n🌍 REAL-TIME MARKET NEWS (Agent Search):\n{news_context}\n(Use this to explain 'WHY' the chart looks like that)")

        if technical_data:
            parts.append(f"\nTechnical Indicators:\n{self._format_technical(technical_data)}")
        
        if vision_analysis:
            parts.append(f"\nForecast Chart Analysis (from Vision AI):\n{vision_analysis}")
        
        if history:
            parts.append(f"\nRecent Conversation:\n{self._format_history(history)}")
        
        return "\n".join(parts)
    
    def _format_technical(self, data: dict) -> str:
        """Format technical data for context"""
        lines = []
        
        if rsi := data.get('rsi'):
            lines.append(f"- RSI: {rsi.get('current')} (Signal: {rsi.get('signal', 'N/A')})")
        
        if macd := data.get('macd'):
            lines.append(f"- MACD Signal: {macd.get('signal', 'N/A')}")
        
        if dd := data.get('drawdown'):
            lines.append(f"- Maximum Drawdown: {dd.get('max_drawdown')}%")
        
        if cr := data.get('cumulative_returns'):
            lines.append(f"- Total Return: {cr.get('total_return')}%")
        
        if ma := data.get('moving_averages'):
            lines.append(f"- MA20: {ma.get('ma20')}, MA50: {ma.get('ma50')}")
        
        if forecast := data.get('forecast'):
            if val := forecast.get('validation'):
                lines.append(f"- Forecast MAE: ${val.get('mae')}")
        
        return "\n".join(lines) if lines else "No technical data available"
    
    def _format_history(self, history: list) -> str:
        """Format conversation history"""
        formatted = []
        for h in history[-3:]:  # Last 3 exchanges only
            formatted.append(f"User: {h['user']}\nAssistant: {h['assistant']}")
        return "\n\n".join(formatted)

# Create singleton instance
gemini_client = GeminiClient()
