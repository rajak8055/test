#!/usr/bin/env python3
"""
Local development server - runs on port 8000 for better compatibility
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting NLP to SQL Chatbot on http://localhost:8000")
    print("📊 Database schema will be shown on the left")
    print("💬 Chat interface on the right")
    print("🛡️  Only safe SELECT queries allowed")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        app,
        host="127.0.0.1",  # localhost only
        port=8000,         # different port
        reload=False,
        log_level="info"
    )