import logging
from typing import Optional
from .call_groq_api import call_groq_api

logger = logging.getLogger(__name__)

async def explain_query(self, sql_query: str, schema_context: str) -> Optional[str]:
    """Generate explanation for SQL query"""
    try:
        prompt = f"""Explain the following PostgreSQL query in simple terms:

{schema_context}

SQL Query: {sql_query}

Explain what this query does, which tables it accesses, what data it returns, and any important details about the query structure. Keep the explanation concise and user-friendly."""

        explanation = await call_groq_api(self, prompt)
        return explanation

    except Exception as e:
        logger.error(f"Failed to generate query explanation: {e}")
        return None
