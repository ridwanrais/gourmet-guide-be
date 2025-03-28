from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from app.schemas.preferences import SuggestionsResponse
from app.workflows.base import get_llm
from langchain_core.prompts import ChatPromptTemplate

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_food_preference_suggestions(count: int = Query(5, description="Number of suggestions to return")):
    """
    Get a list of suggested food preferences for the user.
    
    This endpoint uses LangGraph to generate contextual food preference suggestions.
    """
    try:
        # Get LLM with Deepseek R1 model from OpenRouter
        llm = get_llm()
        
        # Create a prompt for generating food preference suggestions
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful food recommendation assistant. Generate diverse and creative food preference suggestions that users might want to ask about."),
            ("human", f"Generate {count} different food preference suggestions. These should be phrased as if a user is asking for food recommendations. Make them diverse in terms of cuisine types, dietary restrictions, price ranges, and specific needs (like quick meals, healthy options, etc.). Format your response as a simple list with each suggestion on a new line.")
        ])
        
        # Get the response from the LLM
        response = llm.invoke(prompt)
        
        # Process the response to extract suggestions
        suggestions = [line.strip() for line in response.content.split('\n') if line.strip()]
        
        # Limit to the requested count
        suggestions = suggestions[:count]
        
        return SuggestionsResponse(suggestions=suggestions)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "An error occurred while generating suggestions",
                "details": str(e)
            }
        )
