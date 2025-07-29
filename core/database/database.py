import logging
from .get_connection_params import get_connection_params
from .connect import connect
from .disconnect import disconnect
from .test_connection import test_connection
from .get_schema_info import get_schema_info
from .format_schema_for_llm import format_schema_for_llm
from .execute_query import execute_query
from .get_table_sample_data import get_table_sample_data

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.connection_params = get_connection_params()

    async def connect(self):
        self.pool = await connect(self.connection_params)

    async def disconnect(self):
        await disconnect(self.pool)

    async def test_connection(self) -> bool:
        return await test_connection(self.pool)

    async def get_schema_info(self):
        return await get_schema_info(self.pool)

    def format_schema_for_llm(self, schema_info):
        return format_schema_for_llm(schema_info)

    async def execute_query(self, sql_query: str):
        return await execute_query(self.pool, sql_query)

    async def get_table_sample_data(self, table_name: str, limit: int = 5):
        return await get_table_sample_data(self.pool, table_name, limit)
