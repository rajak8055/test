import logging

logger = logging.getLogger(__name__)

async def test_connection(pool) -> bool:
    """Test database connection"""
    try:
        if not pool:
            return False

        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
