# NLP to SQL Chatbot Setup Guide

## Installation

### Method 1: Using pip
```bash
pip install fastapi uvicorn asyncpg sqlparse aiohttp python-multipart jinja2 python-dotenv
```

### Method 2: Using requirements.txt
Create a `requirements.txt` file with:
```
fastapi>=0.100.0
uvicorn>=0.23.0
asyncpg>=0.28.0
sqlparse>=0.4.4
aiohttp>=3.8.0
python-multipart>=0.0.6
jinja2>=3.1.0
pydantic>=2.0.0
```

Then install:
```bash
pip install -r requirements.txt
```

## Environment Setup

1. **Database Configuration**
   Set up PostgreSQL and add these environment variables:
   ```bash
   DATABASE_URL=postgresql://username:password@localhost:5432/database_name
   # OR individual parameters:
   PGHOST=localhost
   PGPORT=5432
   PGDATABASE=your_database_name
   PGUSER=your_username
   PGPASSWORD=your_password
   ```

2. **Groq API Key**
   Get your free API key from https://console.groq.com/keys
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Running the Application

```bash
python main.py
```

The server will start on http://localhost:5000

## API Endpoints

- `POST /api/query` - Convert natural language to SQL
- `GET /api/schema` - Get database schema
- `GET /health` - Health check
- `POST /api/execute-sql` - Execute raw SQL (validated)

## Files Structure

```
├── main.py           # FastAPI application
├── database.py       # Database connection manager
├── llm_service.py    # Groq LLM integration
├── validators.py     # SQL validation and security
├── models.py         # Pydantic data models
├── static/           # Frontend assets
│   ├── style.css
│   └── script.js
└── templates/
    └── index.html    # Main interface
```

## Security Features

- Only SELECT queries allowed
- SQL injection protection
- Dangerous operation blocking (DROP, DELETE, TRUNCATE, etc.)
- Query validation and sanitization

## Troubleshooting Database Connection Issues

### Test Your Connection First
```bash
python test_connection.py
```

### Common Issues and Solutions

1. **"password authentication failed for user 'postgres'"**
   - Verify your PostgreSQL credentials
   - Make sure PostgreSQL service is running
   - Test connection with psql: `psql -h localhost -U postgres -d postgres`

2. **Environment Variables Not Loading**
   - Create a `.env` file in your project root
   - Install python-dotenv: `pip install python-dotenv`
   - Copy from `.env.example` and update with your values

3. **Connection Works in Test but Fails in Main App**
   - Ensure `.env` file is in the same directory as `main.py`
   - Check that python-dotenv is installed
   - Verify no typos in environment variable names

4. **Different Behavior from Other Projects**
   - Check if other projects use different connection libraries
   - Ensure same PostgreSQL version and configuration
   - Compare environment variable names and formats

### Example .env File
```env
# Copy your working credentials from other projects
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/your_database
GROQ_API_KEY=your_groq_api_key
```