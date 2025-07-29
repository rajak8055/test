from pydantic import BaseModel
from typing import List
from .database_column import DatabaseColumn

class DatabaseTable(BaseModel):
    table_name: str
    table_type: str
    columns: List[DatabaseColumn]
