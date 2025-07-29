from pydantic import BaseModel
from typing import List, Optional

class LLMResponse(BaseModel):
    sql_query: str
    explanation: Optional[str] = None
    confidence: Optional[float] = None
    suggested_improvements: List[str] = []
