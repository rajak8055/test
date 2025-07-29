import logging

logger = logging.getLogger(__name__)

async def disconnect(pool):
    """Close connection pool"""
    if pool:
        await pool.close()
        logger.info("Database connection pool closed")
