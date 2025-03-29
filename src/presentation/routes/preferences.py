from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from src.domain.value_objects import SuggestionsResponse
from src.application.services import generate_food_preference_suggestions

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_food_preference_suggestions(count: int = Query(5, description="Number of suggestions to return")):
    """
    Get a list of suggested food preferences for the user.
    
    This endpoint uses LangGraph to generate contextual food preference suggestions.
    """
    try:
        # Call the application service to generate suggestions
        suggestions = await generate_food_preference_suggestions(count)
        
        return SuggestionsResponse(suggestions=suggestions)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "An error occurred while generating suggestions",
                "details": str(e)
            }
        )
