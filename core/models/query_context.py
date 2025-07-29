from pydantic import BaseModel
from typing import List, Dict, Any

class QueryContext(BaseModel):
    question: str
    schema_context: str
    previous_queries: List[str] = []
    table_samples: Dict[str, List[Dict[str, Any]]] = {}
