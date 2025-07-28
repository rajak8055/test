#!/usr/bin/env python3
"""
Simple database connection test script
Run this to test your PostgreSQL connection before running the main application
"""

import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

async def test_database_connection():
    """Test database connection with detailed error reporting"""
    
    print("=== Database Connection Test ===")
    
    # Check for DATABASE_URL first
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        print(f"Found DATABASE_URL: {database_url[:50]}...")
        try:
            conn = await asyncpg.connect(database_url)
            result = await conn.fetchval("SELECT version()")
            print(f"✅ Connection successful!")
            print(f"PostgreSQL version: {result}")
            await conn.close()
            return True
        except Exception as e:
            print(f"❌ DATABASE_URL connection failed: {e}")
    
    # Try individual parameters
    print("\n--- Trying individual parameters ---")
    
    host = os.getenv("PGHOST", "localhost")
    port = int(os.getenv("PGPORT", "5432"))
    database = os.getenv("PGDATABASE", "postgres")
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD", "")
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    print(f"User: {user}")
    print(f"Password: {'*' * len(password) if password else '(empty)'}")
    
    if not password:
        print("⚠️  WARNING: PGPASSWORD is empty!")
    
    try:
        conn = await asyncpg.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        result = await conn.fetchval("SELECT version()")
        print(f"✅ Connection successful!")
        print(f"PostgreSQL version: {result}")
        
        # Test creating a simple table
        await conn.execute("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name TEXT)")
        await conn.execute("DROP TABLE IF EXISTS test_table")
        print("✅ Basic table operations work!")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n--- Troubleshooting Tips ---")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your username and password")
        print("3. Verify the database exists")
        print("4. Try connecting with psql first:")
        print(f"   psql -h {host} -p {port} -U {user} -d {database}")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    print("\n=== Environment Variables Check ===")
    
    env_vars = [
        "DATABASE_URL",
        "PGHOST", "PGPORT", "PGDATABASE", "PGUSER", "PGPASSWORD",
        "GROQ_API_KEY"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if "PASSWORD" in var or "KEY" in var:
                print(f"{var}: {'*' * min(len(value), 10)} (hidden)")
            else:
                print(f"{var}: {value}")
        else:
            print(f"{var}: (not set)")

async def main():
    check_environment_variables()
    
    success = await test_database_connection()
    
    if success:
        print("\n🎉 Database connection test passed! You can run the main application.")
    else:
        print("\n❌ Database connection test failed. Please fix the issues above.")

if __name__ == "__main__":
    asyncio.run(main())