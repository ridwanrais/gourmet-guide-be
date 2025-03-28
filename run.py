import asyncio
import uvicorn
from app.db.init_db import init_db

async def setup():
    """Initialize the database before starting the application."""
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully!")

if __name__ == "__main__":
    # Run database setup
    asyncio.run(setup())
    
    # Start the FastAPI application
    print("Starting Gourmet Guide API server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
