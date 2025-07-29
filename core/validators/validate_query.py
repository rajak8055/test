import sqlparse
from sqlparse import sql, tokens
import logging
from ..models import ValidationResult, QueryType
from .check_dangerous_keywords import check_dangerous_keywords
from .check_dangerous_functions import check_dangerous_functions
from .check_dangerous_patterns import check_dangerous_patterns
from .has_multiple_statements import has_multiple_statements
from .get_query_type import get_query_type
from .extract_table_names import extract_table_names
from .validate_select_query import validate_select_query

logger = logging.getLogger(__name__)

def validate_query(self, sql_query: str) -> ValidationResult:
    """Validate SQL query for security and compliance"""
    try:
        # Basic validation
        if not sql_query or not sql_query.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Empty SQL query"
            )

        # Parse the SQL query
        try:
            parsed = sqlparse.parse(sql_query)
            if not parsed:
                return ValidationResult(
                    is_valid=False,
                    error_message="Unable to parse SQL query"
                )

            parsed_query = parsed[0]
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"SQL parsing error: {str(e)}"
            )

        # Check for dangerous keywords
        dangerous_check = check_dangerous_keywords(self, sql_query)
        if not dangerous_check.is_valid:
            return dangerous_check

        # Check for dangerous functions
        function_check = check_dangerous_functions(self, sql_query)
        if not function_check.is_valid:
            return function_check

        # Check for dangerous patterns
        pattern_check = check_dangerous_patterns(self, sql_query)
        if not pattern_check.is_valid:
            return pattern_check

        # Check for multiple statements (SQL injection prevention)
        if has_multiple_statements(parsed_query):
            return ValidationResult(
                is_valid=False,
                error_message="Multiple SQL statements are not allowed"
            )

        # Determine query type
        query_type = get_query_type(parsed_query)

        # Only allow SELECT statements for safety
        if query_type != QueryType.SELECT:
            return ValidationResult(
                is_valid=False,
                error_message=f"Only SELECT queries are allowed. Found: {query_type}",
                query_type=query_type,
                potentially_dangerous=True
            )

        # Extract table names
        tables = extract_table_names(parsed_query)

        # Additional SELECT query validation
        select_validation = validate_select_query(parsed_query)
        if not select_validation.is_valid:
            return select_validation

        return ValidationResult(
            is_valid=True,
            query_type=query_type,
            tables_accessed=tables
        )

    except Exception as e:
        logger.error(f"Validation error: {e}")
        return ValidationResult(
            is_valid=False,
            error_message=f"Validation failed: {str(e)}"
        )
