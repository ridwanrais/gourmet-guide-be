from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.infrastructure.database import get_db
from src.presentation.routes import location, preferences, restaurants
from src.utils.logging_config import setup_logging

# Set up logging
logger = setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(location.router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(preferences.router, prefix=f"{settings.API_V1_PREFIX}")
app.include_router(restaurants.router, prefix=f"{settings.API_V1_PREFIX}")


@app.get("/")
async def root():
    return {"message": "Welcome to the Gourmet Guide AI API"}


@app.get(f"{settings.API_V1_PREFIX}/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint to verify API and database connectivity."""
    try:
        # Check database connection
        await db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "api_version": "1.0.0",
        "database": db_status,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=True)
