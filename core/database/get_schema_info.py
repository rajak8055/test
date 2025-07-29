import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

async def get_schema_info(pool) -> List[Dict[str, Any]]:
    """Get database schema information"""
    try:
        async with pool.acquire() as conn:
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
