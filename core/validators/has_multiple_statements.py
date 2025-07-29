import re

def has_multiple_statements(parsed_query) -> bool:
    """Check if query contains multiple statements (semicolon-separated)"""
    # Count semicolons that separate statements
    query_str = str(parsed_query).strip()

    # Remove trailing semicolon if present
    if query_str.endswith(';'):
        query_str = query_str[:-1]

    # Check for semicolons that indicate multiple statements
    semicolon_count = query_str.count(';')

    # Also check for multiple DML/DDL keywords that could indicate multiple statements
    statement_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'TRUNCATE']
    keyword_count = 0

    for keyword in statement_keywords:
        # Use word boundaries to avoid counting keywords within strings or identifiers
        pattern = r'\b' + re.escape(keyword) + r'\b'
        matches = re.findall(pattern, query_str.upper())
        keyword_count += len(matches)

    # Consider it multiple statements if there are semicolons OR multiple statement keywords
    # Exception: WITH clauses can have multiple SELECT keywords
    if query_str.upper().strip().startswith('WITH'):
        # For CTEs, allow multiple SELECT keywords
        return semicolon_count > 0

    return semicolon_count > 0 or keyword_count > 1
