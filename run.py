import asyncio
import uvicorn
import os
from src.infrastructure.init_db import init_db

async def setup():
    """Initialize the database before starting the application."""
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully!")

if __name__ == "__main__":
    # Run database setup
    asyncio.run(setup())
    
    # Start the FastAPI application
    port = int(os.getenv("PORT", 8080))  # Default to 8080 if PORT not set
    print("Starting Gourmet Guide API server...")
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True)
