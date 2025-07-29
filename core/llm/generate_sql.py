import logging
from typing import Optional
from .build_prompt import build_prompt
from .call_groq_api import call_groq_api
from .extract_sql_from_response import extract_sql_from_response

logger = logging.getLogger(__name__)

async def generate_sql(self, question: str, schema_context: str, additional_context: str = None) -> Optional[str]:
    """Generate SQL query from natural language question"""
    try:
        # Construct the prompt
        prompt = build_prompt(question, schema_context, additional_context)

        # Make API call to Groq
        response = await call_groq_api(self, prompt)

        if response:
            # Extract SQL from response
            sql_query = extract_sql_from_response(response)
            return sql_query

        return None

    except Exception as e:
        logger.error(f"Failed to generate SQL: {e}")
        return None
