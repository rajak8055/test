from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class QueryType(str, Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"
    TRUNCATE = "TRUNCATE"

class ValidationResult(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None
    query_type: Optional[QueryType] = None
    tables_accessed: List[str] = []
    potentially_dangerous: bool = False

class DatabaseColumn(BaseModel):
    column_name: str
    data_type: str
    is_nullable: str
    column_default: Optional[str] = None
    character_maximum_length: Optional[int] = None
    constraint_type: Optional[str] = None

class DatabaseTable(BaseModel):
    table_name: str
    table_type: str
    columns: List[DatabaseColumn]

class ChatMessage(BaseModel):
    id: str
    message: str
    is_user: bool
    timestamp: datetime
    sql_query: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None

class QueryContext(BaseModel):
    question: str
    schema_context: str
    previous_queries: List[str] = []
    table_samples: Dict[str, List[Dict[str, Any]]] = {}

class LLMResponse(BaseModel):
    sql_query: str
    explanation: Optional[str] = None
    confidence: Optional[float] = None
    suggested_improvements: List[str] = []
