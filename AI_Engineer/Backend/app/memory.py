from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ConversationMemory:
    """In-memory conversation storage per ticker"""
    
    def __init__(self):
        self.store: Dict[str, List[dict]] = {}
        logger.info("Conversation memory initialized")
    
    def add_exchange(self, ticker: str, user_msg: str, ai_msg: str):
        """Add a user-AI exchange to memory"""
        if ticker not in self.store:
            self.store[ticker] = []
        
        self.store[ticker].append({
            "user": user_msg,
            "assistant": ai_msg
        })
        
        # Keep last 10 exchanges to prevent memory bloat
        if len(self.store[ticker]) > 10:
            self.store[ticker] = self.store[ticker][-10:]
        
        logger.info(f"Added exchange for {ticker}. Total: {len(self.store[ticker])}")
    
    def get_history(self, ticker: str) -> List[dict]:
        """Retrieve conversation history for a ticker"""
        return self.store.get(ticker, [])
    
    def clear(self, ticker: str = None):
        """Clear memory for a specific ticker or all"""
        if ticker:
            if ticker in self.store:
                del self.store[ticker]
                logger.info(f"Cleared memory for {ticker}")
        else:
            self.store.clear()
            logger.info("Cleared all memory")
    
    def get_stats(self) -> dict:
        """Get memory statistics"""
        return {
            "total_tickers": len(self.store),
            "total_exchanges": sum(len(h) for h in self.store.values())
        }

# Create singleton instance
memory = ConversationMemory()
