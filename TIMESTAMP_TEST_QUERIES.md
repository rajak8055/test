# Millisecond Timestamp Testing Guide

## Database Format
All timestamps are stored in PostgreSQL with millisecond precision:
**Format: `2025-03-10T09:46:40.541+00:00`**

## Sample Test Questions for Timestamp Queries

### 1. Exact Timestamp Matching
**Question:** "Show me the production run that ended exactly at 2025-03-25T19:46:40.541+00:00"
**Expected SQL Pattern:**
```sql
WHERE end_timestamp = '2025-03-25T19:46:40.541+00:00'
```

### 2. Time Range Queries
**Question:** "Find all production runs that started between 2025-03-10T06:00:00.000+00:00 and 2025-03-10T14:00:00.000+00:00"
**Expected SQL Pattern:**
```sql
WHERE start_timestamp >= '2025-03-10T06:00:00.000+00:00' 
AND start_timestamp <= '2025-03-10T14:00:00.000+00:00'
```

### 3. Millisecond Precision Calculations
**Question:** "Calculate the exact duration in milliseconds for production run RUN-2025-028"
**Expected SQL Pattern:**
```sql
EXTRACT(EPOCH FROM (end_timestamp - start_timestamp)) * 1000 AS duration_milliseconds
```

### 4. Complex Timestamp Filtering
**Question:** "Show quality checks performed within 2 hours after production start for runs on 2025-03-10"
**Expected SQL Pattern:**
```sql
WHERE qc.check_timestamp >= pr.start_timestamp 
AND qc.check_timestamp <= pr.start_timestamp + INTERVAL '2 hours'
AND pr.start_timestamp::date = '2025-03-10'
```

### 5. Timestamp Grouping
**Question:** "Group production runs by hour and show counts for March 25, 2025"
**Expected SQL Pattern:**
```sql
DATE_TRUNC('hour', start_timestamp) AS hour_group
WHERE start_timestamp::date = '2025-03-25'
GROUP BY DATE_TRUNC('hour', start_timestamp)
```

### 6. Recent Data with Precision
**Question:** "Find all machine downtime events in the last 48 hours with exact timestamps"
**Expected SQL Pattern:**
```sql
WHERE start_timestamp >= (CURRENT_TIMESTAMP - INTERVAL '48 hours')
```

### 7. Overlapping Events
**Question:** "Find production runs and downtime that overlapped, showing exact start and end times"
**Expected SQL Pattern:**
```sql
WHERE pr.start_timestamp < md.end_timestamp 
AND pr.end_timestamp > md.start_timestamp
```

### 8. Millisecond Duration Analysis
**Question:** "Show the shortest and longest production runs with durations in seconds including milliseconds"
**Expected SQL Pattern:**
```sql
EXTRACT(EPOCH FROM (end_timestamp - start_timestamp)) AS duration_seconds
```

## Key Timestamp Functions to Use

1. **Exact Matching:** `timestamp = '2025-03-10T09:46:40.541+00:00'`
2. **Date Extraction:** `timestamp::date = '2025-03-10'`
3. **Time Extraction:** `timestamp::time`
4. **Duration Calculation:** `EXTRACT(EPOCH FROM (end_time - start_time))`
5. **Interval Addition:** `timestamp + INTERVAL '2 hours'`
6. **Truncation:** `DATE_TRUNC('hour', timestamp)`
7. **Formatting:** `TO_CHAR(timestamp, 'YYYY-MM-DD"T"HH24:MI:SS.MS"+00:00"')`

## Test Data Available

- **Production Runs:** 30 runs from March 10-26, 2025
- **Quality Checks:** 13 checks with millisecond precision
- **Machine Downtime:** 8 events with precise start/end times
- **All timestamps** include milliseconds: `.123`, `.456`, `.541`, etc.

## Sample Complex Query
"Show me all production runs on March 25th with their quality checks, including exact timestamps and time differences between production start and quality check"

Expected to generate complex JOIN with timestamp calculations and precise filtering.