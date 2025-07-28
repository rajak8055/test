import asyncpg
import os
import json
from typing import List, Dict, Any, Tuple, Optional
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.connection_params = self._get_connection_params()
    
    def _get_connection_params(self) -> Dict[str, str]:
        """Get database connection parameters from environment variables"""
        # Try DATABASE_URL first (full connection string)
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            logger.info(f"Using DATABASE_URL connection")
            return {"dsn": database_url}
        
        # Fall back to individual parameters
        params = {
            "host": os.getenv("PGHOST", "localhost"),
            "port": int(os.getenv("PGPORT", "5432")),
            "database": os.getenv("PGDATABASE", "postgres"),
            "user": os.getenv("PGUSER", "postgres"),
            "password": os.getenv("PGPASSWORD", "")
        }
        
        # Log connection attempt (without password)
        logger.info(f"Using individual connection parameters: host={params['host']}, port={params['port']}, database={params['database']}, user={params['user']}")
        
        return params
    
    async def connect(self):
        """Create connection pool"""
        try:
            if "dsn" in self.connection_params:
                self.pool = await asyncpg.create_pool(
                    dsn=self.connection_params["dsn"],
                    min_size=1,
                    max_size=10,
                    command_timeout=30
                )
            else:
                self.pool = await asyncpg.create_pool(
                    **self.connection_params,
                    min_size=1,
                    max_size=10,
                    command_timeout=30
                )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            if not self.pool:
                return False
            
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    async def get_schema_info(self) -> List[Dict[str, Any]]:
        """Get database schema information"""
        try:
            async with self.pool.acquire() as conn:
                # Get tables and their columns
                query = """
                SELECT 
                    t.table_name,
                    t.table_type,
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    c.column_default,
                    c.character_maximum_length,
                    tc.constraint_type
                FROM information_schema.tables t
                LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
                LEFT JOIN information_schema.key_column_usage kcu ON c.table_name = kcu.table_name 
                    AND c.column_name = kcu.column_name
                LEFT JOIN information_schema.table_constraints tc ON kcu.constraint_name = tc.constraint_name
                WHERE t.table_schema = 'public'
                    AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_name, c.ordinal_position;
                """
                
                rows = await conn.fetch(query)
                
                # Group by table
                tables = {}
                for row in rows:
                    table_name = row['table_name']
                    if table_name not in tables:
                        tables[table_name] = {
                            'table_name': table_name,
                            'table_type': row['table_type'],
                            'columns': []
                        }
                    
                    if row['column_name']:  # Only add if column exists
                        column_info = {
                            'column_name': row['column_name'],
                            'data_type': row['data_type'],
                            'is_nullable': row['is_nullable'],
                            'column_default': row['column_default'],
                            'character_maximum_length': row['character_maximum_length'],
                            'constraint_type': row['constraint_type']
                        }
                        
                        # Check if column already exists (due to multiple constraints)
                        existing_column = next(
                            (col for col in tables[table_name]['columns'] 
                             if col['column_name'] == row['column_name']), None
                        )
                        
                        if existing_column:
                            # Add constraint type to existing column
                            if row['constraint_type'] and row['constraint_type'] not in str(existing_column.get('constraint_type', '')):
                                existing_column['constraint_type'] = f"{existing_column.get('constraint_type', '')}, {row['constraint_type']}".strip(', ')
                        else:
                            tables[table_name]['columns'].append(column_info)
                
                return list(tables.values())
                
        except Exception as e:
            logger.error(f"Failed to get schema info: {e}")
            raise
    
    def format_schema_for_llm(self, schema_info: List[Dict[str, Any]]) -> str:
        """Format schema information for LLM context"""
        schema_text = "Database Schema:\n\n"
        
        for table in schema_info:
            schema_text += f"Table: {table['table_name']}\n"
            schema_text += "Columns:\n"
            
            for column in table['columns']:
                constraint_info = ""
                if column.get('constraint_type'):
                    constraint_info = f" ({column['constraint_type']})"
                
                nullable_info = " NOT NULL" if column['is_nullable'] == 'NO' else ""
                
                schema_text += f"  - {column['column_name']}: {column['data_type']}{constraint_info}{nullable_info}\n"
            
            schema_text += "\n"
        
        # Add note about timestamp format
        schema_text += "Note: All timestamp columns use ISO 8601 format (YYYY-MM-DDTHH:MM:SS.sssZ)\n"
        schema_text += "When querying timestamps, use ISO 8601 format in your SQL queries.\n\n"
        
        return schema_text
    
    async def execute_query(self, sql_query: str) -> Tuple[List[Dict[str, Any]], float]:
        """Execute SQL query and return results with execution time"""
        start_time = time.time()
        
        try:
            async with self.pool.acquire() as conn:
                # Execute query
                rows = await conn.fetch(sql_query)
                
                # Convert to list of dictionaries
                results = []
                for row in rows:
                    row_dict = {}
                    for key, value in row.items():
                        # Handle datetime objects
                        if isinstance(value, datetime):
                            row_dict[key] = value.isoformat()
                        else:
                            row_dict[key] = value
                    results.append(row_dict)
                
                execution_time = time.time() - start_time
                logger.info(f"Query executed successfully in {execution_time:.3f}s")
                
                return results, execution_time
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query execution failed after {execution_time:.3f}s: {e}")
            raise Exception(f"Database query failed: {str(e)}")
    
    async def get_table_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample data from a table for context"""
        try:
            # Validate table name to prevent SQL injection
            async with self.pool.acquire() as conn:
                # Check if table exists
                table_exists = await conn.fetchval(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1 AND table_schema = 'public')",
                    table_name
                )
                
                if not table_exists:
                    raise Exception(f"Table '{table_name}' does not exist")
                
                # Get sample data
                query = f'SELECT * FROM "{table_name}" LIMIT $1'
                rows = await conn.fetch(query, limit)
                
                results = []
                for row in rows:
                    row_dict = {}
                    for key, value in row.items():
                        if isinstance(value, datetime):
                            row_dict[key] = value.isoformat()
                        else:
                            row_dict[key] = value
                    results.append(row_dict)
                
                return results
                
        except Exception as e:
            logger.error(f"Failed to get sample data from {table_name}: {e}")
            raise
