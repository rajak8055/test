import re
from ..models import ValidationResult

def validate_select_query(parsed_query) -> ValidationResult:
    """Additional validation for SELECT queries"""
    query_str = str(parsed_query).upper()

    # Check for common SQL injection patterns
    injection_patterns = [
        r'UNION\s+SELECT',
        r';\s*DROP',
        r';\s*DELETE',
        r';\s*INSERT',
        r';\s*UPDATE',
        r'--',  # SQL comments
        r'/\*.*\*/',  # Multi-line comments
    ]

    for pattern in injection_patterns:
        if re.search(pattern, query_str, re.IGNORECASE | re.DOTALL):
            return ValidationResult(
                is_valid=False,
                error_message="Potential SQL injection pattern detected",
                potentially_dangerous=True
            )

    return ValidationResult(is_valid=True)
