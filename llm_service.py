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
        """Build enhanced prompt for complex SQL generation"""
        prompt = f"""You are an expert PostgreSQL database analyst specializing in manufacturing data analysis.

{schema_context}

ADVANCED SQL GENERATION RULES:
1. ONLY generate SELECT queries - no INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, or TRUNCATE
2. Use sophisticated PostgreSQL features: JOINs, subqueries, CTEs (WITH clauses), window functions
3. For complex questions, use multiple table JOINs and advanced aggregations
4. Calculate metrics: efficiency rates, percentages, time differences, totals
5. CRITICAL: Handle timestamps in EXACT format '2025-03-10T09:46:40.541+00:00' with milliseconds
6. Use window functions for ranking, running totals, and comparisons
7. Apply CASE statements for conditional logic and categorization
8. Include date/time extractions: EXTRACT, DATE_TRUNC, AGE functions
9. Use appropriate GROUP BY, HAVING, ORDER BY clauses
10. Return ONLY the SQL query without explanations or formatting

MANUFACTURING CONTEXT:
- production_runs: Links machines, operations, shifts, operators with timestamps
- quality_checks: Inspection results linked to production runs
- machine_downtime: Maintenance and failure records with duration
- Use JOINs to connect: machines→departments, runs→employees, etc.

ADVANCED PATTERNS TO USE:
- Multi-table JOINs: FROM production_runs pr JOIN machines m ON pr.machine_id = m.id
- Time calculations: EXTRACT(EPOCH FROM (end_timestamp - start_timestamp))/3600 AS duration_hours
- Efficiency calculations: (actual_units * 100.0 / planned_units) AS efficiency_percent
- Window functions: ROW_NUMBER() OVER (PARTITION BY machine_id ORDER BY start_timestamp DESC)
- TIMESTAMP FILTERING EXAMPLES:
  * Exact timestamp: WHERE start_timestamp = '2025-03-10T09:46:40.541+00:00'
  * Time range: WHERE start_timestamp >= '2025-03-10T06:00:00.000+00:00' AND start_timestamp < '2025-03-11T06:00:00.000+00:00'
  * Date filtering: WHERE start_timestamp::date = '2025-03-10'
  * Recent data: WHERE start_timestamp >= (CURRENT_TIMESTAMP - INTERVAL '7 days')
- CTEs for complex logic: WITH machine_stats AS (SELECT machine_id, COUNT(*) as runs...)
- Millisecond precision: Always use format YYYY-MM-DDTHH:MM:SS.sss+00:00 for timestamp literals

Question: {question}"""

        if additional_context:
            prompt += f"\n\nAdditional Context: {additional_context}"
        
        prompt += "\n\nGenerate a comprehensive PostgreSQL query:"
        
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
                        "content": "You are an expert PostgreSQL database analyst specializing in complex manufacturing data queries. Generate sophisticated SELECT queries using advanced SQL features like JOINs, subqueries, CTEs, window functions, and calculations. Return only the SQL query without explanations or formatting."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.2,
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
