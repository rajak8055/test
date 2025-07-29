import logging
from .validate_query import validate_query
from .sanitize_input import sanitize_input

logger = logging.getLogger(__name__)

class SQLValidator:
    def __init__(self):
        # Define dangerous operations that should be blocked
        self.dangerous_keywords = {
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE'
        }

        # Define dangerous functions and operations
        self.dangerous_functions = {
            'pg_sleep', 'pg_read_file', 'pg_ls_dir', 'pg_stat_file',
            'copy', 'lo_import', 'lo_export', 'dblink', 'dblink_exec'
        }

        # File system related patterns
        self.dangerous_patterns = [
            r'\.\./',  # Directory traversal
            r'\\x[0-9a-fA-F]+',  # Hex encoded strings
            r'chr\s*\(',  # Character conversion
            r'ascii\s*\(',  # ASCII conversion
        ]

    def validate_query(self, sql_query: str):
        return validate_query(self, sql_query)

    def sanitize_input(self, user_input: str):
        return sanitize_input(user_input)
