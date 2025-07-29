import time
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

async def execute_query(pool, sql_query: str) -> Tuple[List[Dict[str, Any]], float]:
    """Execute SQL query and return results with execution time"""
    start_time = time.time()

    try:
        async with pool.acquire() as conn:
            # Execute query
            rows = await conn.fetch(sql_query)

            # Convert to list of dictionaries
            results = []
            for row in rows:
                row_dict = {}
                for key, value in row.items():
                    # Handle datetime objects
                    if isinstance(value, datetime):
                        row_dict[key] = value.isoformat()
                    else:
                        row_dict[key] = value
                results.append(row_dict)

            execution_time = time.time() - start_time
            logger.info(f"Query executed successfully in {execution_time:.3f}s")

            return results, execution_time

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Query execution failed after {execution_time:.3f}s: {e}")
        raise Exception(f"Database query failed: {str(e)}")
