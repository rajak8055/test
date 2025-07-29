import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)

def get_connection_params() -> Dict[str, str]:
    """Get database connection parameters from environment variables"""
    # Use in-memory SQLite database for testing
    return {"dsn": "sqlite:///:memory:"}
