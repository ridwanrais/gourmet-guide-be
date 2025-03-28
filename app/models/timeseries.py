from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from app.db.database import Base


class ConversationHistory(Base):
    """
    Time-series model for storing conversation history.
    Uses TimescaleDB hypertable for efficient time-series data storage.
    """
    __tablename__ = "conversation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    user_input = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSON, nullable=True)
    
    # Additional fields for analytics
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<ConversationHistory(id={self.id}, session_id={self.session_id}, timestamp={self.timestamp})>"


class AIUsageStatistics(Base):
    """
    Time-series model for storing AI usage statistics.
    Uses TimescaleDB hypertable for efficient time-series data storage.
    """
    __tablename__ = "ai_usage_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    endpoint = Column(String, index=True, nullable=False)
    model_name = Column(String, nullable=False)
    tokens_used = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=False)
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<AIUsageStatistics(id={self.id}, endpoint={self.endpoint}, timestamp={self.timestamp})>"


class RestaurantRecommendation(Base):
    """
    Time-series model for storing restaurant recommendations.
    Uses TimescaleDB hypertable for efficient time-series data storage.
    """
    __tablename__ = "restaurant_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    location = Column(String, nullable=False)
    preference = Column(Text, nullable=False)
    recommendations = Column(JSON, nullable=False)
    match_score = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<RestaurantRecommendation(id={self.id}, session_id={self.session_id}, timestamp={self.timestamp})>"
