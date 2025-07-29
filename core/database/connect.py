import aiosqlite
import logging
from typing import Dict

logger = logging.getLogger(__name__)

async def connect(connection_params: Dict[str, str]):
    """Create connection pool"""
    try:
        if "dsn" in connection_params:
            pool = await aiosqlite.connect(connection_params["dsn"])
            logger.info("Database connection pool created successfully")
            return pool
    except Exception as e:
        logger.error(f"Failed to create database connection pool: {e}")
        raise
