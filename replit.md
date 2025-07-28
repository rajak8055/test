# NLP to SQL Chatbot

## Overview

This is a FastAPI-based web application that converts natural language questions into SQL queries using Groq's LLM service. The application provides a chat interface where users can ask questions about their database in plain English, and the system will generate appropriate SQL queries, execute them safely, and display the results.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modern web architecture with clear separation of concerns:

- **Frontend**: Static HTML/CSS/JavaScript providing a chat-based user interface
- **Backend**: FastAPI REST API server handling NLP-to-SQL conversion and query execution
- **Database**: PostgreSQL database with connection pooling via asyncpg
- **LLM Integration**: Groq API for natural language processing and SQL generation
- **Security Layer**: SQL validation and sanitization to prevent dangerous operations

## Key Components

### Backend Services

1. **DatabaseManager** (`database.py`)
   - Manages PostgreSQL connections using asyncpg connection pooling
   - Supports both DATABASE_URL and individual connection parameters
   - Handles schema introspection and query execution
   - Implements proper error handling and logging

2. **GroqLLMService** (`llm_service.py`)
   - Integrates with Groq's Mixtral-8x7b model for SQL generation
   - Constructs context-aware prompts with schema information
   - Enforces SELECT-only query generation for security
   - Handles API communication and response parsing

3. **SQLValidator** (`validators.py`)
   - Validates and sanitizes SQL queries before execution
   - Blocks dangerous operations (INSERT, UPDATE, DELETE, DROP, etc.)
   - Detects potentially harmful patterns and functions
   - Uses sqlparse for proper SQL syntax analysis

4. **FastAPI Application** (`main.py`)
   - REST API endpoints for chat functionality and health checks
   - Static file serving for frontend assets
   - Proper async context management with lifespan events
   - Structured error handling and logging

### Frontend Interface

1. **Chat Interface** (`static/script.js`, `templates/index.html`)
   - Real-time chat interface for natural language queries
   - Dynamic schema display panel
   - Result visualization with syntax highlighting
   - System health monitoring and status indicators

2. **Styling** (`static/style.css`)
   - Modern, responsive design with CSS Grid layout
   - Dark/light theme support with CSS custom properties
   - Professional UI components with proper accessibility

### Data Models

1. **Pydantic Models** (`models.py`)
   - Structured data validation for API requests/responses
   - Database schema representation models
   - Chat message and query context models
   - Type-safe enums for query classifications

## Data Flow

1. **User Input**: User enters natural language question in chat interface
2. **Schema Context**: System retrieves current database schema information
3. **LLM Processing**: Question and schema sent to Groq API for SQL generation
4. **Validation**: Generated SQL validated for security and compliance
5. **Execution**: Safe queries executed against PostgreSQL database
6. **Response**: Results formatted and displayed in chat interface

## External Dependencies

### Core Technologies
- **FastAPI**: Modern Python web framework for API development
- **asyncpg**: High-performance PostgreSQL adapter for Python
- **Pydantic**: Data validation and serialization
- **Jinja2**: Template engine for HTML rendering

### LLM Integration
- **Groq API**: Mixtral-8x7b model for natural language to SQL conversion
- **aiohttp**: Async HTTP client for API communication

### SQL Processing
- **sqlparse**: SQL parsing and validation library

### Frontend
- **Vanilla JavaScript**: No framework dependencies for simplicity
- **CSS Grid/Flexbox**: Modern layout techniques
- **Fetch API**: For backend communication

## Deployment Strategy

### Environment Configuration
- Database connection via DATABASE_URL or individual parameters (PGHOST, PGPORT, etc.)
- GROQ_API_KEY for LLM service integration
- Supports both development and production PostgreSQL instances

### Security Considerations
- SQL injection prevention through query validation
- Read-only query enforcement (SELECT operations only)
- Connection pooling for performance and resource management
- Comprehensive logging for monitoring and debugging

### Scalability Features
- Async/await throughout for non-blocking operations
- Connection pooling for database efficiency
- Stateless design enabling horizontal scaling
- Proper error handling and graceful degradation

The application is designed to be easily deployable on platforms like Replit, with minimal configuration required beyond setting the appropriate environment variables for database and API access.