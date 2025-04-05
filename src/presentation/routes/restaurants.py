from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.repositories import RestaurantRepository
from src.application.restaurant_workflow import \
    get_restaurant_recommendations_service
from src.domain.value_objects import (ErrorDetail, ErrorResponse,
                                      RecommendationRequest,
                                      RecommendationsResponse)
from src.infrastructure.database import get_db
from src.utils.error_handlers import ErrorHandlers
from src.utils.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.post(
    "/recommendations",
    response_model=RecommendationsResponse,
    responses={400: {"model": ErrorResponse}},
)
async def get_restaurant_recommendations(
    request: RecommendationRequest, db: AsyncSession = Depends(get_db)
):
    """
    Get personalized restaurant recommendations based on coordinates and prompt.

    This endpoint uses LangGraph to process the user's query and generate restaurant recommendations.
    The results are stored in TimescaleDB for future reference and analytics.
    """
    logger.info(
        f"Received recommendation request: coordinates={request.coordinates}, prompt='{request.prompt}'"
    )

    try:
        # Call the application service to get restaurant recommendations
        logger.debug("Calling restaurant recommendation service")
        response, session_id = await get_restaurant_recommendations_service(
            prompt=request.prompt,
            coordinates=request.coordinates,
            user_id=request.userId,
            radius=request.radius,
            limit=request.limit,
        )
        logger.info(
            f"Generated {len(response.restaurants)} restaurant recommendations with session_id={session_id}"
        )

        # Use the repository to save the recommendation to the database
        logger.debug(f"Saving recommendation to database with session_id={session_id}")
        restaurant_repo = RestaurantRepository(db)
        await restaurant_repo.save_recommendation(
            session_id=session_id,
            user_id=request.userId,
            location=f"{request.coordinates.latitude}, {request.coordinates.longitude}",
            preference=request.prompt,
            recommendations=response.restaurants,
            match_score=response.matchScore,
        )
        logger.info(
            f"Successfully saved recommendation to database with session_id={session_id}"
        )

        return response

    except Exception as e:
        logger.error(
            f"Error processing restaurant recommendation request: {str(e)}",
            exc_info=True,
        )
        ErrorHandlers.handle_invalid_request(e)
