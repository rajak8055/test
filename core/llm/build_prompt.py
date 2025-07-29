def build_prompt(question: str, schema_context: str, additional_context: str = None) -> str:
    """Build enhanced prompt for complex SQL generation"""
    prompt = f"""You are an expert PostgreSQL database analyst specializing in manufacturing data analysis.

{schema_context}

ADVANCED SQL GENERATION RULES:
1. ONLY generate SELECT queries - no INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, or TRUNCATE
2. Use sophisticated PostgreSQL features: JOINs, subqueries, CTEs (WITH clauses), window functions
3. For complex questions, use multiple table JOINs and advanced aggregations
4. Calculate metrics: efficiency rates, percentages, time differences, totals
5. CRITICAL: Handle timestamps in EXACT format '2025-03-10T09:46:40.541+00:00' with milliseconds
6. Use window functions for ranking, running totals, and comparisons
7. Apply CASE statements for conditional logic and categorization
8. Include date/time extractions: EXTRACT, DATE_TRUNC, AGE functions
9. Use appropriate GROUP BY, HAVING, ORDER BY clauses
10. Return ONLY the SQL query without explanations or formatting

MANUFACTURING CONTEXT:
- production_runs: Links machines, operations, shifts, operators with timestamps
- quality_checks: Inspection results linked to production runs
- machine_downtime: Maintenance and failure records with duration
- Use JOINs to connect: machines→departments, runs→employees, etc.

ADVANCED PATTERNS TO USE:
- Multi-table JOINs: FROM production_runs pr JOIN machines m ON pr.machine_id = m.id
- Time calculations: EXTRACT(EPOCH FROM (end_timestamp - start_timestamp))/3600 AS duration_hours
- Efficiency calculations: (actual_units * 100.0 / planned_units) AS efficiency_percent
- Window functions: ROW_NUMBER() OVER (PARTITION BY machine_id ORDER BY start_timestamp DESC)
- TIMESTAMP FILTERING EXAMPLES:
  * Exact timestamp: WHERE start_timestamp = '2025-03-10T09:46:40.541+00:00'
  * Time range: WHERE start_timestamp >= '2025-03-10T06:00:00.000+00:00' AND start_timestamp < '2025-03-11T06:00:00.000+00:00'
  * Date filtering: WHERE start_timestamp::date = '2025-03-10'
  * Recent data: WHERE start_timestamp >= (CURRENT_TIMESTAMP - INTERVAL '7 days')
- CTEs for complex logic: WITH machine_stats AS (SELECT machine_id, COUNT(*) as runs...)
- Millisecond precision: Always use format YYYY-MM-DDTHH:MM:SS.sss+00:00 for timestamp literals

Question: {question}"""

    if additional_context:
        prompt += f"\n\nAdditional Context: {additional_context}"

    prompt += "\n\nGenerate a comprehensive PostgreSQL query:"

    return prompt
