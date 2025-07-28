from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import asyncpg
import os
from typing import List, Dict, Any, Optional
import logging
from contextlib import asynccontextmanager

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading .env file
    pass

from database import DatabaseManager
from validators import SQLValidator
from llm_service import GroqLLMService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class NLPQuery(BaseModel):
    question: str
    context: Optional[str] = None

class SQLResponse(BaseModel):
    sql_query: str
    results: List[Dict[str, Any]]
    success: bool
    error: Optional[str] = None
    execution_time: Optional[float] = None

class SchemaResponse(BaseModel):
    tables: List[Dict[str, Any]]
    success: bool
    error: Optional[str] = None

# Global variables
db_manager = None
sql_validator = None
llm_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_manager, sql_validator, llm_service
    
    try:
        # Initialize services with detailed logging
        logger.info("Initializing database manager...")
        db_manager = DatabaseManager()
        
        logger.info("Attempting database connection...")
        await db_manager.connect()
        
        logger.info("Initializing SQL validator...")
        sql_validator = SQLValidator()
        
        logger.info("Initializing LLM service...")
        llm_service = GroqLLMService()
        
        logger.info("Application startup completed successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        
        # Try to provide more helpful error information
        if "password authentication failed" in str(e):
            logger.error("Database connection failed - check your credentials:")
            logger.error(f"DATABASE_URL exists: {bool(os.getenv('DATABASE_URL'))}")
            logger.error(f"PGHOST: {os.getenv('PGHOST', 'not set')}")
            logger.error(f"PGUSER: {os.getenv('PGUSER', 'not set')}")
            logger.error(f"PGDATABASE: {os.getenv('PGDATABASE', 'not set')}")
            logger.error(f"PGPORT: {os.getenv('PGPORT', 'not set')}")
        
        raise
    finally:
        # Shutdown
        if db_manager:
            await db_manager.disconnect()
        logger.info("Application shutdown completed")

# Create FastAPI app
app = FastAPI(
    title="NLP to SQL Chatbot",
    description="Convert natural language queries to SQL and execute them on PostgreSQL",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        is_connected = await db_manager.test_connection()
        return {
            "status": "healthy" if is_connected else "unhealthy",
            "database_connected": is_connected,
            "services": {
                "database": "connected" if is_connected else "disconnected",
                "llm": "available" if llm_service else "unavailable"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database_connected": False,
            "error": str(e)
        }

@app.get("/api/schema", response_model=SchemaResponse)
async def get_database_schema():
    """Get database schema information"""
    try:
        schema_info = await db_manager.get_schema_info()
        return SchemaResponse(
            tables=schema_info,
            success=True
        )
    except Exception as e:
        logger.error(f"Failed to get schema: {e}")
        return SchemaResponse(
            tables=[],
            success=False,
            error=str(e)
        )

@app.post("/api/query", response_model=SQLResponse)
async def process_nlp_query(query: NLPQuery):
    """Process natural language query and return SQL results"""
    try:
        # Get database schema for context
        schema_info = await db_manager.get_schema_info()
        schema_context = db_manager.format_schema_for_llm(schema_info)
        
        # Generate SQL from natural language
        sql_query = await llm_service.generate_sql(
            question=query.question,
            schema_context=schema_context,
            additional_context=query.context
        )
        
        if not sql_query:
            return SQLResponse(
                sql_query="",
                results=[],
                success=False,
                error="Failed to generate SQL query from natural language"
            )
        
        # Validate SQL query
        validation_result = sql_validator.validate_query(sql_query)
        if not validation_result.is_valid:
            return SQLResponse(
                sql_query=sql_query,
                results=[],
                success=False,
                error=f"Query validation failed: {validation_result.error_message}"
            )
        
        # Execute SQL query
        results, execution_time = await db_manager.execute_query(sql_query)
        
        return SQLResponse(
            sql_query=sql_query,
            results=results,
            success=True,
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"Failed to process query: {e}")
        return SQLResponse(
            sql_query="",
            results=[],
            success=False,
            error=str(e)
        )

@app.post("/api/execute-sql")
async def execute_raw_sql(request: dict):
    """Execute raw SQL query (with validation)"""
    try:
        sql_query = request.get("sql_query", "").strip()
        
        if not sql_query:
            raise HTTPException(status_code=400, detail="SQL query is required")
        
        # Validate SQL query
        validation_result = sql_validator.validate_query(sql_query)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400, 
                detail=f"Query validation failed: {validation_result.error_message}"
            )
        
        # Execute SQL query
        results, execution_time = await db_manager.execute_query(sql_query)
        
        return {
            "sql_query": sql_query,
            "results": results,
            "success": True,
            "execution_time": execution_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute SQL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
