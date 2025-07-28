import re
import sqlparse
from sqlparse import sql, tokens
from typing import List, Set
import logging

from models import ValidationResult, QueryType

logger = logging.getLogger(__name__)

class SQLValidator:
    def __init__(self):
        # Define dangerous operations that should be blocked
        self.dangerous_keywords = {
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE'
        }
        
        # Define dangerous functions and operations
        self.dangerous_functions = {
            'pg_sleep', 'pg_read_file', 'pg_ls_dir', 'pg_stat_file',
            'copy', 'lo_import', 'lo_export', 'dblink', 'dblink_exec'
        }
        
        # File system related patterns
        self.dangerous_patterns = [
            r'\.\./',  # Directory traversal
            r'\\x[0-9a-fA-F]+',  # Hex encoded strings
            r'chr\s*\(',  # Character conversion
            r'ascii\s*\(',  # ASCII conversion
        ]
    
    def validate_query(self, sql_query: str) -> ValidationResult:
        """Validate SQL query for security and compliance"""
        try:
            # Basic validation
            if not sql_query or not sql_query.strip():
                return ValidationResult(
                    is_valid=False,
                    error_message="Empty SQL query"
                )
            
            # Parse the SQL query
            try:
                parsed = sqlparse.parse(sql_query)
                if not parsed:
                    return ValidationResult(
                        is_valid=False,
                        error_message="Unable to parse SQL query"
                    )
                
                parsed_query = parsed[0]
            except Exception as e:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"SQL parsing error: {str(e)}"
                )
            
            # Check for dangerous keywords
            dangerous_check = self._check_dangerous_keywords(sql_query)
            if not dangerous_check.is_valid:
                return dangerous_check
            
            # Check for dangerous functions
            function_check = self._check_dangerous_functions(sql_query)
            if not function_check.is_valid:
                return function_check
            
            # Check for dangerous patterns
            pattern_check = self._check_dangerous_patterns(sql_query)
            if not pattern_check.is_valid:
                return pattern_check
            
            # Check for multiple statements (SQL injection prevention)
            if self._has_multiple_statements(parsed_query):
                return ValidationResult(
                    is_valid=False,
                    error_message="Multiple SQL statements are not allowed"
                )
            
            # Determine query type
            query_type = self._get_query_type(parsed_query)
            
            # Only allow SELECT statements for safety
            if query_type != QueryType.SELECT:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Only SELECT queries are allowed. Found: {query_type}",
                    query_type=query_type,
                    potentially_dangerous=True
                )
            
            # Extract table names
            tables = self._extract_table_names(parsed_query)
            
            # Additional SELECT query validation
            select_validation = self._validate_select_query(parsed_query)
            if not select_validation.is_valid:
                return select_validation
            
            return ValidationResult(
                is_valid=True,
                query_type=query_type,
                tables_accessed=tables
            )
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return ValidationResult(
                is_valid=False,
                error_message=f"Validation failed: {str(e)}"
            )
    
    def _check_dangerous_keywords(self, sql_query: str) -> ValidationResult:
        """Check for dangerous SQL keywords"""
        sql_upper = sql_query.upper()
        
        for keyword in self.dangerous_keywords:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, sql_upper):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Dangerous keyword '{keyword}' is not allowed",
                    potentially_dangerous=True
                )
        
        return ValidationResult(is_valid=True)
    
    def _check_dangerous_functions(self, sql_query: str) -> ValidationResult:
        """Check for dangerous PostgreSQL functions"""
        sql_upper = sql_query.upper()
        
        for func in self.dangerous_functions:
            pattern = r'\b' + re.escape(func.upper()) + r'\s*\('
            if re.search(pattern, sql_upper):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Dangerous function '{func}' is not allowed",
                    potentially_dangerous=True
                )
        
        return ValidationResult(is_valid=True)
    
    def _check_dangerous_patterns(self, sql_query: str) -> ValidationResult:
        """Check for dangerous patterns in SQL"""
        for pattern in self.dangerous_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Dangerous pattern detected in query",
                    potentially_dangerous=True
                )
        
        return ValidationResult(is_valid=True)
    
    def _has_multiple_statements(self, parsed_query) -> bool:
        """Check if query contains multiple statements"""
        statement_count = 0
        for token in parsed_query.tokens:
            if token.ttype is None and str(token).strip():
                statement_count += 1
            elif token.ttype in (tokens.Keyword.DML, tokens.Keyword):
                if str(token).upper() in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']:
                    statement_count += 1
        
        return statement_count > 1
    
    def _get_query_type(self, parsed_query) -> QueryType:
        """Determine the type of SQL query"""
        for token in parsed_query.tokens:
            if token.ttype is tokens.Keyword.DML:
                keyword = str(token).upper()
                if keyword in [e.value for e in QueryType]:
                    return QueryType(keyword)
            elif token.ttype is tokens.Keyword:
                keyword = str(token).upper()
                if keyword in [e.value for e in QueryType]:
                    return QueryType(keyword)
        
        return QueryType.SELECT  # Default to SELECT
    
    def _extract_table_names(self, parsed_query) -> List[str]:
        """Extract table names from parsed SQL"""
        tables = []
        
        def extract_from_token(token):
            if hasattr(token, 'tokens'):
                for sub_token in token.tokens:
                    extract_from_token(sub_token)
            elif token.ttype is None and str(token).strip():
                # This might be a table name
                token_str = str(token).strip()
                if token_str and not token_str.upper() in ['FROM', 'WHERE', 'SELECT', 'AND', 'OR']:
                    # Basic table name validation
                    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token_str):
                        tables.append(token_str)
        
        extract_from_token(parsed_query)
        return list(set(tables))  # Remove duplicates
    
    def _validate_select_query(self, parsed_query) -> ValidationResult:
        """Additional validation for SELECT queries"""
        query_str = str(parsed_query).upper()
        
        # Check for common SQL injection patterns
        injection_patterns = [
            r'UNION\s+SELECT',
            r';\s*DROP',
            r';\s*DELETE',
            r';\s*INSERT',
            r';\s*UPDATE',
            r'--',  # SQL comments
            r'/\*.*\*/',  # Multi-line comments
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, query_str, re.IGNORECASE | re.DOTALL):
                return ValidationResult(
                    is_valid=False,
                    error_message="Potential SQL injection pattern detected",
                    potentially_dangerous=True
                )
        
        return ValidationResult(is_valid=True)
    
    def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input to prevent injection"""
        if not user_input:
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[;\'"\\]', '', user_input)
        
        # Limit length
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]
        
        return sanitized.strip()
