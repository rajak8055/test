from pydantic import BaseModel
from typing import List, Optional
from .query_type import QueryType

class ValidationResult(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None
    query_type: Optional[QueryType] = None
    tables_accessed: List[str] = []
    potentially_dangerous: bool = False
