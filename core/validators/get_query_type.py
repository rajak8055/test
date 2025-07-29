from sqlparse import tokens
from ..models import QueryType

def get_query_type(parsed_query) -> QueryType:
    """Determine the type of SQL query"""
    # Handle WITH clauses (CTEs) - they are SELECT queries
    query_str = str(parsed_query).upper().strip()
    if query_str.startswith('WITH'):
        return QueryType.SELECT

    for token in parsed_query.tokens:
        if token.ttype is tokens.Keyword.DML:
            keyword = str(token).upper()
            if keyword in [e.value for e in QueryType]:
                return QueryType(keyword)
        elif token.ttype is tokens.Keyword:
            keyword = str(token).upper()
            if keyword in [e.value for e in QueryType]:
                return QueryType(keyword)

    return QueryType.SELECT  # Default to SELECT
