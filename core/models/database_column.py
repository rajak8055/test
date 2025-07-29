from pydantic import BaseModel
from typing import Optional

class DatabaseColumn(BaseModel):
    column_name: str
    data_type: str
    is_nullable: str
    column_default: Optional[str] = None
    character_maximum_length: Optional[int] = None
    constraint_type: Optional[str] = None
