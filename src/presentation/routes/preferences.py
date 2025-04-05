from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from src.application.services import generate_food_preference_suggestions
from src.domain.value_objects import (ErrorDetail, ErrorResponse,
                                      SuggestionsResponse)
from src.utils.error_handlers import ErrorHandlers

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get(
    "/suggestions",
    response_model=SuggestionsResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_food_preference_suggestions(
    count: int = Query(5, description="Number of suggestions to return")
):
    """
    Get a list of suggested food preferences for the user.

    This endpoint uses LangGraph to generate contextual food preference suggestions.
    """
    try:
        # Call the application service to generate suggestions
        suggestions = await generate_food_preference_suggestions(count)

        return SuggestionsResponse(suggestions=suggestions)

    except Exception as e:
        ErrorHandlers.handle_server_error(e)
