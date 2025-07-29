import os
import logging
from .generate_sql import generate_sql
from .explain_query import explain_query

logger = logging.getLogger(__name__)

class GroqLLMService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

        # Try different models in order of preference (updated list)
        self.available_models = [
            "llama-3.1-8b-instant",  # Primary - fast and available
            "llama-3.2-90b-text-preview",  # High capability backup
            "llama-3.2-11b-text-preview",  # Medium capability
            "llama-3.2-3b-preview",  # Fast fallback
            "gemma2-9b-it"  # Final fallback
        ]
        self.model = self.available_models[0]  # Start with the best model

        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment variables")

    async def generate_sql(self, question: str, schema_context: str, additional_context: str = None):
        return await generate_sql(self, question, schema_context, additional_context)

    async def explain_query(self, sql_query: str, schema_context: str):
        return await explain_query(self, sql_query, schema_context)
