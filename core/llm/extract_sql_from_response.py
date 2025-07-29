import logging
from typing import Optional

logger = logging.getLogger(__name__)

def extract_sql_from_response(response: str) -> Optional[str]:
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

    # Basic validation - should start with SELECT or WITH (for CTEs)
    query_upper = response.upper().strip()
    if not (query_upper.startswith('SELECT') or query_upper.startswith('WITH')):
        logger.warning(f"Generated query doesn't start with SELECT or WITH: {response}")
        return None

    # Add semicolon if not present
    if not response.endswith(';'):
        response += ';'

    return response
