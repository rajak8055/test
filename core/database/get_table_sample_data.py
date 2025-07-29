import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

async def get_table_sample_data(pool, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get sample data from a table for context"""
    try:
        # Validate table name to prevent SQL injection
        async with pool.acquire() as conn:
            # Check if table exists
            table_exists = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1 AND table_schema = 'public')",
                table_name
            )

            if not table_exists:
                raise Exception(f"Table '{table_name}' does not exist")

            # Get sample data
            query = f'SELECT * FROM "{table_name}" LIMIT $1'
            rows = await conn.fetch(query, limit)

            results = []
            for row in rows:
                row_dict = {}
                for key, value in row.items():
                    if isinstance(value, datetime):
                        row_dict[key] = value.isoformat()
                    else:
                        row_dict[key] = value
                results.append(row_dict)

            return results

    except Exception as e:
        logger.error(f"Failed to get sample data from {table_name}: {e}")
        raise
