from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.value_objects import (
    RecommendationRequest, RecommendationsResponse, 
    ErrorResponse, ErrorDetail
)
from src.infrastructure.database import get_db
from src.application.restaurant_workflow import get_restaurant_recommendations_service
from src.adapters.repositories import RestaurantRepository
from src.utils.error_handlers import ErrorHandlers

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.post("/recommendations", response_model=RecommendationsResponse, responses={400: {"model": ErrorResponse}})
async def get_restaurant_recommendations(
    request: RecommendationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized restaurant recommendations based on location and preferences.
    
    This endpoint uses LangGraph to process the user's query and generate restaurant recommendations.
    The results are stored in TimescaleDB for future reference and analytics.
    """
    try:
        # Call the application service to get restaurant recommendations
        response, session_id = await get_restaurant_recommendations_service(
            location=request.location,
            preference=request.preference,
            user_id=request.userId,
            coordinates=request.coordinates,
            radius=request.radius,
            limit=request.limit
        )
        
        # Use the repository to save the recommendation to the database
        restaurant_repo = RestaurantRepository(db)
        await restaurant_repo.save_recommendation(
            session_id=session_id,
            user_id=request.userId,
            location=request.location,
            preference=request.preference,
            recommendations=response.restaurants,
            match_score=response.matchScore
        )
        
        return response
        
    except Exception as e:
        ErrorHandlers.handle_invalid_request(e)
