import re
from ..models import ValidationResult

def check_dangerous_patterns(self, sql_query: str) -> ValidationResult:
    """Check for dangerous patterns in SQL"""
    for pattern in self.dangerous_patterns:
        if re.search(pattern, sql_query, re.IGNORECASE):
            return ValidationResult(
                is_valid=False,
                error_message=f"Dangerous pattern detected in query",
                potentially_dangerous=True
            )

    return ValidationResult(is_valid=True)
