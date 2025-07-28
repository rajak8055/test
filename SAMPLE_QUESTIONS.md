# Manufacturing Database - Sample Test Questions

## Database Overview
The manufacturing database includes:
- **8 Tables**: departments, machines, shifts, employees, operations, production_runs, quality_checks, machine_downtime
- **28 Production Runs** with ISO 8601 timestamps from January 15-28, 2025
- **Complex Relationships**: Multi-table joins with temporal data
- **Real Manufacturing Scenarios**: Shifts, operations, quality control, downtime tracking

## Simple Questions (Getting Started)

1. "Show me all the machines in the database"
2. "What departments do we have?"
3. "List all employees and their roles"
4. "Show me the different shifts we operate"
5. "What operations do we perform?"

## Intermediate Questions

6. "Which machines are currently under maintenance?"
7. "Show me production runs from the day shift only"
8. "Find all quality checks that failed"
9. "List machines in Assembly Line A department"
10. "Show me all packaging operations from this month"

## Complex Timestamp-Based Questions

### Date Range Queries
11. "Show me all production runs between January 20th and January 25th, 2025"
12. "Find quality checks performed in the last 7 days"
13. "What machines had downtime during the weekend (January 25-26)?"
14. "Show production runs that started after 2 PM yesterday"

### Time Analysis Queries
15. "Which production runs took longer than 8 hours to complete?"
16. "Find machines that were down for more than 2 hours"
17. "Show me night shift production from the last week"
18. "What operations were running during the afternoon shift on January 21st?"

### Performance & Efficiency Queries
19. "Calculate the efficiency rate (actual vs planned units) for each machine this month"
20. "Which operator had the highest production output in the last 10 days?"
21. "Show me production runs with rejection rates above 3%"
22. "Find the average downtime duration by machine type"

### Multi-Table Complex Queries
23. "Show me all production runs with their quality check results and operator details"
24. "Find machines that had both production runs and downtime on the same day"
25. "Which departments had the most quality issues this month?"
26. "Show me the complete production history for machine ASM-001 including downtime"

### Advanced Timestamp Calculations
27. "Calculate total productive hours vs downtime hours for each machine"
28. "Find overlapping production runs (runs that started before another ended)"
29. "Show me the busiest production hour of each day this week"
30. "Which shift produces the most units per hour on average?"

### Business Intelligence Queries  
31. "Show me daily production trends for the last 2 weeks"
32. "Find patterns in quality issues by time of day"
33. "Calculate OEE (Overall Equipment Effectiveness) for each machine"
34. "Which combination of operator and machine produces the best quality?"

## Ultra-Complex Queries (Advanced Testing)

### Temporal Pattern Analysis
35. "Find machines that consistently have higher rejection rates during night shifts compared to day shifts"
36. "Show me production runs where quality checks were performed more than 4 hours after start"
37. "Identify time periods where multiple machines were down simultaneously"

### Cross-Department Analysis  
38. "Compare productivity between Assembly Line A and Assembly Line B for the same time periods"
39. "Show me the flow of products from welding to assembly to packaging with timestamps"
40. "Find bottlenecks by analyzing average time between operations"

### Predictive Analysis Preparation
41. "Show me machines that had quality issues within 24 hours before scheduled maintenance"
42. "Find patterns in downtime: do certain machines fail more often during specific shifts?"
43. "Calculate the time between quality checks and identify gaps longer than 3 hours"

## Data Validation Questions
44. "Show me any production runs with missing end timestamps"
45. "Find quality checks without corresponding production runs"
46. "Identify any overlapping shift assignments for the same operator"

## Sample Expected Results Preview

For question "Show production runs from January 21st with operator names":
```
Expected: 3 runs (RUN-2025-015, RUN-2025-016, RUN-2025-017) 
with operators: James Taylor, Sarah Johnson, Emma Wilson
```

For question "Which machines had the highest downtime in January?":
```
Expected: Machine ASM-102 (40+ hours scheduled maintenance)
followed by WLD-001 (2h 45m electrical issue)
```

## Testing Instructions

1. **Start Simple**: Begin with questions 1-10 to verify basic functionality
2. **Test Timestamps**: Use questions 11-18 to validate ISO 8601 date handling  
3. **Complex Joins**: Questions 19-26 test multi-table relationships
4. **Performance**: Questions 27-34 test calculation capabilities
5. **Edge Cases**: Questions 35-46 test advanced scenarios

## Expected Behavior

- All timestamps should display in ISO 8601 format
- Date ranges should work with natural language ("last week", "yesterday")
- Complex calculations should show intermediate steps
- Multi-table joins should preserve data relationships
- Error handling should be graceful for impossible queries