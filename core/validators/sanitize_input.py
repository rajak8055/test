import re

def sanitize_input(user_input: str) -> str:
    """Sanitize user input to prevent injection"""
    if not user_input:
        return ""

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[;\'"\\]', '', user_input)

    # Limit length
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]

    return sanitized.strip()
