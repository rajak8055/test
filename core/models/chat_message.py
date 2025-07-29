from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    id: str
    message: str
    is_user: bool
    timestamp: datetime
    sql_query: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None
