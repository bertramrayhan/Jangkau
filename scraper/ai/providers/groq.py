from scraper.ai.providers.base import BaseAIProvider
from config.logging_config import logger

class Groq(BaseAIProvider):
    """
    Groq AI Provider - Fallback provider when Gemini reaches rate limits.
    """
    
    def __init__(self):
        self.current_model_index = 0
        self.is_limit = False

    @property
    def model_list(self):
        """Property untuk model list Groq"""
        return [
            'mixtral-8x7b-32768',
            'llama-3.1-70b-versatile',
            'llama-3.1-8b-instant',
        ]

    def strukturkan_dengan_ai(self, valid_tags, batch_lomba_mentah):
        """
        TODO: Implement Groq API integration
        For now, this is a placeholder that returns None.
        """
        logger.warning("⚠️ Groq provider belum diimplementasikan. Returning None.")
        return None
    pass