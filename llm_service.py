import os
import json
import logging
from typing import Optional, Dict, Any
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

class GroqLLMService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Try different models in order of preference
        self.available_models = [
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant", 
            "mixtral-8x7b-32768",
            "llama3-70b-8192",
            "gemma2-9b-it"
        ]
        self.model = self.available_models[0]  # Start with the best model
        
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment variables")
    
    async def generate_sql(self, question: str, schema_context: str, additional_context: str = None) -> Optional[str]:
        """Generate SQL query from natural language question"""
        try:
            # Construct the prompt
            prompt = self._build_prompt(question, schema_context, additional_context)
            
            # Make API call to Groq
            response = await self._call_groq_api(prompt)
            
            if response:
                # Extract SQL from response
                sql_query = self._extract_sql_from_response(response)
                return sql_query
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to generate SQL: {e}")
            return None
    
    def _build_prompt(self, question: str, schema_context: str, additional_context: str = None) -> str:
        """Build the prompt for the LLM"""
        prompt = f"""You are an expert SQL developer. Convert the following natural language question into a PostgreSQL query.

{schema_context}

IMPORTANT RULES:
1. ONLY generate SELECT queries - no INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, or TRUNCATE
2. Use proper PostgreSQL syntax
3. For timestamp queries, use ISO 8601 format (YYYY-MM-DDTHH:MM:SS.sssZ)
4. When dealing with dates/timestamps, consider timezone handling
5. Use appropriate JOIN clauses when multiple tables are involved
6. Include proper WHERE clauses for filtering
7. Use LIMIT when appropriate to avoid large result sets
8. Return ONLY the SQL query, no explanations or additional text
9. Do not use any dangerous functions or operations
10. Ensure the query is safe and follows best practices

Question: {question}"""

        if additional_context:
            prompt += f"\n\nAdditional Context: {additional_context}"
        
        prompt += "\n\nSQL Query:"
        
        return prompt
    
    async def _call_groq_api(self, prompt: str) -> Optional[str]:
        """Make API call to Groq with automatic model fallback"""
        if not self.api_key:
            logger.error("GROQ_API_KEY is required but not provided")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Try each model until one works
        for model_name in self.available_models:
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert PostgreSQL developer. Generate safe, efficient SELECT queries only. Return only the SQL query without any additional text or formatting."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.1,
                "top_p": 0.9,
                "stream": False
            }
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.base_url,
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            
                            if "choices" in data and len(data["choices"]) > 0:
                                content = data["choices"][0]["message"]["content"]
                                # Update the working model for future requests
                                if self.model != model_name:
                                    logger.info(f"Switched to working model: {model_name}")
                                    self.model = model_name
                                return content.strip()
                            else:
                                logger.error(f"No choices in Groq API response for model {model_name}")
                        else:
                            error_text = await response.text()
                            logger.warning(f"Model {model_name} failed: {response.status} - {error_text}")
                            # Try next model
                            continue
                            
            except asyncio.TimeoutError:
                logger.warning(f"Model {model_name} timed out, trying next model")
                continue
            except Exception as e:
                logger.warning(f"Model {model_name} failed with error: {e}, trying next model")
                continue
        
        logger.error("All available models failed")
        return None
    
    def _extract_sql_from_response(self, response: str) -> Optional[str]:
        """Extract SQL query from LLM response"""
        if not response:
            return None
        
        # Clean up the response
        response = response.strip()
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = [
            "```sql", "```SQL", "```",
            "sql:", "SQL:",
            "Query:", "query:"
        ]
        
        suffixes_to_remove = [
            "```", ";"
        ]
        
        # Remove prefixes
        for prefix in prefixes_to_remove:
            if response.lower().startswith(prefix.lower()):
                response = response[len(prefix):].strip()
        
        # Remove suffixes
        for suffix in suffixes_to_remove:
            if response.endswith(suffix):
                response = response[:-len(suffix)].strip()
        
        # Basic validation - should start with SELECT
        if not response.upper().strip().startswith('SELECT'):
            logger.warning(f"Generated query doesn't start with SELECT: {response}")
            return None
        
        # Add semicolon if not present
        if not response.endswith(';'):
            response += ';'
        
        return response
    
    async def explain_query(self, sql_query: str, schema_context: str) -> Optional[str]:
        """Generate explanation for SQL query"""
        try:
            prompt = f"""Explain the following PostgreSQL query in simple terms:

{schema_context}

SQL Query: {sql_query}

Explain what this query does, which tables it accesses, what data it returns, and any important details about the query structure. Keep the explanation concise and user-friendly."""

            explanation = await self._call_groq_api(prompt)
            return explanation
            
        except Exception as e:
            logger.error(f"Failed to generate query explanation: {e}")
            return None
