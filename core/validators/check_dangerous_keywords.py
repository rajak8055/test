import re
from ..models import ValidationResult

def check_dangerous_keywords(self, sql_query: str) -> ValidationResult:
    """Check for dangerous SQL keywords"""
    sql_upper = sql_query.upper()

    for keyword in self.dangerous_keywords:
        # Use word boundaries to avoid false positives
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, sql_upper):
            return ValidationResult(
                is_valid=False,
                error_message=f"Dangerous keyword '{keyword}' is not allowed",
                potentially_dangerous=True
            )

    return ValidationResult(is_valid=True)
