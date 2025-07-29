from typing import List, Dict, Any

def format_schema_for_llm(schema_info: List[Dict[str, Any]]) -> str:
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
