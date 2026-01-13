# from app.gemini_client import gemini_client (Legacy)
from app.llm_client import llm_client
from app.memory import memory
import time
import logging

logger = logging.getLogger(__name__)

async def process_chat(
    ticker: str,
    message: str,
    technical_data: dict = None,
    forecast_screenshot: str = None
) -> dict:
    """Main chat processing logic with hybrid approach"""
    
    start_time = time.time()
    
    # Detect if this is a forecast-related question
    forecast_keywords = ["prediksi", "forecast", "ramalan", "masa depan", "future", "projection"]
    is_forecast_question = any(
        keyword in message.lower() 
        for keyword in forecast_keywords
    )
    
    vision_analysis = None
    mode = "json"
    
    # Use Vision mode if forecast question AND screenshot provided
    if is_forecast_question and forecast_screenshot:
        logger.info(f"Using VISION mode for: {message[:50]}...")
        mode = "vision"
        try:
            # SWITCH: Use OpenRouter (Mistral) for Vision
            vision_analysis = await llm_client.analyze_chart(forecast_screenshot)
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            # Fallback to JSON mode
            mode = "json_fallback"
    else:
        logger.info(f"Using JSON mode for: {message[:50]}...")
    
    # Get conversation history for context
    history = memory.get_history(ticker)
    
    # Generate answer using DeepSeek (OpenRouter)
    try:
        response = await llm_client.answer_question(
            question=message,
            technical_data=technical_data,
            vision_analysis=vision_analysis,
            history=history
        )
    except Exception as e:
        logger.error(f"Answer generation failed: {e}")
        response = f"Maaf, terjadi error saat memproses pertanyaan: {str(e)}"
    
    # Save exchange to memory
    memory.add_exchange(ticker, message, response)
    
    processing_time = time.time() - start_time
    
    logger.info(f"Chat processed in {processing_time:.2f}s ({mode} mode)")
    
    return {
        "response": response,
        "mode": mode,
        "processing_time": round(processing_time, 2)
    }
