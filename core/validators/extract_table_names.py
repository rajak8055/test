import re
from typing import List

def extract_table_names(parsed_query) -> List[str]:
    """Extract table names from parsed SQL"""
    tables = []

    def extract_from_token(token):
        if hasattr(token, 'tokens'):
            for sub_token in token.tokens:
                extract_from_token(sub_token)
        elif token.ttype is None and str(token).strip():
            # This might be a table name
            token_str = str(token).strip()
            if token_str and not token_str.upper() in ['FROM', 'WHERE', 'SELECT', 'AND', 'OR']:
                # Basic table name validation
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token_str):
                    tables.append(token_str)

    extract_from_token(parsed_query)
    return list(set(tables))  # Remove duplicates
