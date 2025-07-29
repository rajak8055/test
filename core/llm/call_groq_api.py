import aiohttp
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def call_groq_api(self, prompt: str) -> Optional[str]:
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
