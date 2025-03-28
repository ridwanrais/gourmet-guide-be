import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import engine, Base, async_session_factory
from app.models.timeseries import ConversationHistory, AIUsageStatistics, RestaurantRecommendation


async def create_tables():
    """Create database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def setup_timescaledb():
    """Set up TimescaleDB hypertables for time-series data."""
    async with async_session_factory() as session:
        # Create TimescaleDB extension if it doesn't exist
        await session.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
        
        # Convert regular tables to hypertables
        await session.execute(
            text(
                "SELECT create_hypertable('conversation_history', 'timestamp', "
                "if_not_exists => TRUE, migrate_data => TRUE);"
            )
        )
        
        await session.execute(
            text(
                "SELECT create_hypertable('ai_usage_statistics', 'timestamp', "
                "if_not_exists => TRUE, migrate_data => TRUE);"
            )
        )
        
        await session.execute(
            text(
                "SELECT create_hypertable('restaurant_recommendations', 'timestamp', "
                "if_not_exists => TRUE, migrate_data => TRUE);"
            )
        )
        
        # Create indexes for better query performance
        await session.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_conversation_history_session_id_timestamp "
                "ON conversation_history (session_id, timestamp DESC);"
            )
        )
        
        await session.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_ai_usage_statistics_endpoint_timestamp "
                "ON ai_usage_statistics (endpoint, timestamp DESC);"
            )
        )
        
        await session.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_restaurant_recommendations_user_id_timestamp "
                "ON restaurant_recommendations (user_id, timestamp DESC);"
            )
        )
        
        await session.commit()


async def init_db():
    """Initialize database with tables and TimescaleDB setup."""
    await create_tables()
    await setup_timescaledb()


if __name__ == "__main__":
    asyncio.run(init_db())
