import re
from ..models import ValidationResult

def check_dangerous_functions(self, sql_query: str) -> ValidationResult:
    """Check for dangerous PostgreSQL functions"""
    sql_upper = sql_query.upper()

    for func in self.dangerous_functions:
        pattern = r'\b' + re.escape(func.upper()) + r'\s*\('
        if re.search(pattern, sql_upper):
            return ValidationResult(
                is_valid=False,
                error_message=f"Dangerous function '{func}' is not allowed",
                potentially_dangerous=True
            )

    return ValidationResult(is_valid=True)
