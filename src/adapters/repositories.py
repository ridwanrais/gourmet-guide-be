from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models import RestaurantRecommendation
import json


class RestaurantRepository:
    """Repository for restaurant-related database operations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def save_recommendation(
        self, 
        session_id: str, 
        user_id: str, 
        location: str, 
        preference: str, 
        recommendations: list, 
        match_score: float
    ) -> RestaurantRecommendation:
        """
        Save a restaurant recommendation to the database.
        
        Args:
            session_id: Unique session identifier
            user_id: Optional user identifier
            location: User's location
            preference: User's food preference
            recommendations: List of restaurant recommendations
            match_score: How well the recommendations match the preferences
            
        Returns:
            The saved RestaurantRecommendation entity
        """
        # Create a simplified representation of restaurants for storage
        simplified_recommendations = [{
            "id": r.id,
            "name": r.name,
            "rating": r.rating,
            "cuisineTypes": r.cuisineTypes
        } for r in recommendations]
        
        # Create the database entity
        db_recommendation = RestaurantRecommendation(
            session_id=session_id,
            user_id=user_id,
            location=location,
            preference=preference,
            recommendations=json.dumps(simplified_recommendations),
            match_score=match_score
        )
        
        # Add to the database session
        self.db_session.add(db_recommendation)
        await self.db_session.commit()
        
        return db_recommendation
