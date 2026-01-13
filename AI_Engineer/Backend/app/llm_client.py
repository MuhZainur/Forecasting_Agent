from openai import AsyncOpenAI
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.vision_model = settings.openrouter_model_vision
        self.chat_model = settings.openrouter_model_chat
        
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not found. Vision calls may fail.")
            # Prevent startup crash by setting dummy key. Calls will fail later if not set.
            self.api_key = "setup_needed"

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        logger.info(f"LLM Client initialized (Vision: {self.vision_model})")

    async def analyze_chart(self, image_base64: str) -> str:
        """Vision analysis using OpenRouter"""
        try:
            # Clean base64 string if it contains header
            if "," in image_base64:
                image_data = image_base64.split(",")[1]
                # Re-add header if it was stripped or just use the clean base64?
                # OpenAI usually expects a data URL for 'image_url' input type
                # format: "data:image/jpeg;base64,{base64_string}"
                # If input ALREADY has header, use it.
                image_url = image_base64
            else:
                # Assuming PNG if no header provided, or generic
                image_url = f"data:image/png;base64,{image_base64}"

            prompt = """Analyze this stock forecast chart. Identify:
1. Trend direction (upward/downward/sideways)
2. Confidence band width - are bands widening (low confidence) or tight (high confidence)?
3. Any visual anomalies or concerning patterns
4. Overall reliability based on visual patterns

Be concise and focus on actionable insights."""

            logger.info(f"Sending vision request to {self.vision_model}...")

            response = await self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                # OpenRouter specific headers can be handled via default_headers if needed, 
                # but standard OpenAI SDK usually works fine.
                extra_headers={
                    "HTTP-Referer": settings.stock_api_url, # Optional
                    "X-Title": "Stock Analysis AI", # Optional
                }
            )
            
            result = response.choices[0].message.content
            logger.info("Vision analysis completed successfully")
            return result

        except Exception as e:
            logger.error(f"Vision analysis error (OpenRouter): {e}")
            return f"Error analyzing chart: {str(e)}"

    async def answer_question(
        self, 
        question: str,
        technical_data: dict = None,
        vision_analysis: str = None,
        news_context: str = None, 
        history: list = []
    ) -> str:
        """Generate answer using DeepSeek (Reasoning) via OpenRouter"""
        try:
            logger.info(f"Generating answer with {self.chat_model}...")
            
            # Build context (Similar to previous logic)
            context = self._build_context(technical_data, vision_analysis, news_context, history)
            
            messages = [
                {"role": "system", "content": context},
                {"role": "user", "content": question}
            ]
            
            # Using extra_body to pass 'reasoning' parameter
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                extra_body={
                    "reasoning": {"enabled": True} 
                },
                extra_headers={
                    "HTTP-Referer": settings.stock_api_url,
                    "X-Title": "Stock Analysis AI",
                }
            )
            
            # Extract content. 
            # Note: If we want to capture 'reasoning_details' for UI, we would need to 
            # change the return type to dict or handle it differently.
            # For now, returning just the content as per original contract.
            result = response.choices[0].message.content
            
            logger.info("Answer generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Answer generation error (OpenRouter): {e}")
            return f"Maaf, terjadi error: {str(e)}"

    async def generate_market_report(self, ticker: str) -> str:
        """Fetch real-time market news using OpenRouter Web Plugin"""
        try:
            logger.info(f"Generating market report for {ticker}...")
            
            prompt = f"""
            Find the latest breaking news for {ticker} stock from the last 24 hours.
            Identify exactly 3 most important news items.
            For each item, provide:
            1. Headline
            2. Summary
            3. Sentiment (Positive/Negative/Neutral)
            
            Return the output in a clean, structured format (Markdown).
            """
            
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                extra_body={
                    "plugins": [{"id": "web", "max_results": 3}]
                },
                extra_headers={
                    "HTTP-Referer": settings.stock_api_url,
                    "X-Title": "Stock Analysis AI",
                }
            )
            
            result = response.choices[0].message.content
            logger.info("Market report generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Market report error (OpenRouter): {e}")
            return f"Market news unavailable: {str(e)}"

    def _build_context(self, technical_data, vision_analysis, news_context, history):
        """Build context string for LLM"""
        parts = ["You are a professional stock analysis AI assistant. Answer in Bahasa Indonesia."]
        
        if news_context:
            parts.append(f"\n🌍 REAL-TIME MARKET NEWS:\n{news_context}\n")

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
        return "\n".join(lines) if lines else "No technical data available"
    
    def _format_history(self, history: list) -> str:
        """Format conversation history"""
        formatted = []
        for h in history[-3:]: 
            formatted.append(f"User: {h['user']}\nAssistant: {h['assistant']}")
        return "\n\n".join(formatted)

# Create singleton
llm_client = LLMClient()
