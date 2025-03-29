from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from src.application.workflows import get_llm
from src.domain.value_objects import (
    Restaurant, Coordinates, FoodItem, RecommendationsResponse
)
import json
import uuid


def run_restaurant_recommendation_workflow(
    location: str,
    preference: str,
    user_id: str = None
) -> Dict[str, Any]:
    """
    Run the restaurant recommendation workflow using LangGraph.
    
    This workflow processes the user's location and preference to generate
    personalized restaurant recommendations.
    
    Args:
        location: The user's location (e.g., "Jakarta, Indonesia")
        preference: The user's food preference (e.g., "I want something spicy and vegetarian")
        user_id: Optional user ID for personalized recommendations
        
    Returns:
        A dictionary containing the workflow result
    """
    # Get LLM with Deepseek R1 model from OpenRouter
    llm = get_llm()
    
    # Create a prompt for generating restaurant recommendations
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful food recommendation assistant. 
        Generate restaurant recommendations based on the user's location and preferences.
        Consider factors like cuisine type, price range, and specific dietary needs."""),
        ("human", f"I'm in {location} and {preference}. Can you recommend some restaurants?")
    ])
    
    # Get the response from the LLM
    response = llm.invoke(prompt)
    
    # In a real application, we would parse the response and extract structured data
    # For this example, we'll return the raw response
    return {
        "location": location,
        "preference": preference,
        "user_id": user_id,
        "response": response.content
    }


async def get_restaurant_recommendations_service(
    location: str,
    preference: str,
    user_id: Optional[str] = None,
    coordinates: Optional[Coordinates] = None,
    radius: Optional[float] = None,
    limit: Optional[int] = None
) -> RecommendationsResponse:
    """
    Get personalized restaurant recommendations based on location and preferences.
    
    This service uses LangGraph to process the user's query and generate restaurant recommendations.
    
    Args:
        location: The user's location
        preference: The user's food preference
        user_id: Optional user ID for personalized recommendations
        coordinates: Optional coordinates for location-based search
        radius: Optional search radius in kilometers
        limit: Optional maximum number of recommendations to return
        
    Returns:
        Restaurant recommendations with match score
    """
    # Generate a session ID for tracking this recommendation request
    session_id = str(uuid.uuid4())
    
    # Run the restaurant recommendation workflow using LangGraph
    result = run_restaurant_recommendation_workflow(
        location=location,
        preference=preference,
        user_id=user_id
    )
    
    # Create mock restaurant data
    restaurants = [
        Restaurant(
            id="rest1",
            name="Spice Garden",
            rating=4.7,
            priceRange="$$",
            cuisineTypes=["Indian", "Spicy", "Vegetarian"],
            address="123 Spice Lane, Jakarta",
            coordinates=Coordinates(latitude=-6.2088, longitude=106.8456),
            distance=1.2,
            aiDescription="Spice Garden stands out for its authentic Indian flavors and generous vegetarian options. Their perfectly balanced spice levels cater to both spice enthusiasts and those who prefer milder tastes. The restaurant's warm ambiance and attentive service make it ideal for both casual dining and special occasions.",
            popularItems=[
                FoodItem(
                    id="item1",
                    name="Vegetable Biryani",
                    price=75000,
                    description="Fragrant basmati rice cooked with mixed vegetables and aromatic spices",
                    tags=["Vegetarian", "Spicy", "Popular"]
                ),
                FoodItem(
                    id="item2",
                    name="Paneer Tikka Masala",
                    price=85000,
                    description="Cubes of paneer cheese in a rich, creamy tomato sauce",
                    tags=["Vegetarian", "Spicy", "Signature"]
                )
            ],
            openNow=True,
            hours={
                "monday": "10:00 AM - 10:00 PM",
                "tuesday": "10:00 AM - 10:00 PM",
                "wednesday": "10:00 AM - 10:00 PM",
                "thursday": "10:00 AM - 10:00 PM",
                "friday": "10:00 AM - 11:00 PM",
                "saturday": "10:00 AM - 11:00 PM",
                "sunday": "11:00 AM - 9:00 PM"
            }
        ),
        Restaurant(
            id="rest2",
            name="Green Plate",
            rating=4.5,
            priceRange="$$",
            cuisineTypes=["Healthy", "Vegetarian", "Organic"],
            address="456 Health Street, Jakarta",
            coordinates=Coordinates(latitude=-6.2100, longitude=106.8500),
            distance=1.5,
            aiDescription="Green Plate is Jakarta's premier destination for health-conscious diners. They source only organic, locally-grown ingredients and prepare them with minimal processing to preserve nutrients. Their menu changes seasonally to ensure the freshest options.",
            popularItems=[
                FoodItem(
                    id="item3",
                    name="Buddha Bowl",
                    price=65000,
                    description="A nourishing bowl with quinoa, roasted vegetables, avocado, and tahini dressing",
                    tags=["Vegan", "Healthy", "Popular"]
                )
            ],
            openNow=True,
            hours={
                "monday": "08:00 AM - 9:00 PM",
                "tuesday": "08:00 AM - 9:00 PM",
                "wednesday": "08:00 AM - 9:00 PM",
                "thursday": "08:00 AM - 9:00 PM",
                "friday": "08:00 AM - 10:00 PM",
                "saturday": "09:00 AM - 10:00 PM",
                "sunday": "09:00 AM - 8:00 PM"
            }
        ),
        Restaurant(
            id="rest3",
            name="Spice Route",
            rating=4.8,
            priceRange="$$$",
            cuisineTypes=["Thai", "Spicy", "Fusion"],
            address="789 Flavor Avenue, Jakarta",
            coordinates=Coordinates(latitude=-6.2050, longitude=106.8400),
            distance=0.8,
            aiDescription="Spice Route offers an innovative fusion of traditional Thai flavors with modern culinary techniques. Their spice levels can be customized to your preference, and their presentation is as impressive as their flavors.",
            popularItems=[
                FoodItem(
                    id="item4",
                    name="Tom Yum Soup",
                    price=55000,
                    description="Hot and sour soup with lemongrass, lime leaves, and choice of protein",
                    tags=["Spicy", "Signature", "Popular"]
                )
            ],
            openNow=True,
            hours={
                "monday": "11:00 AM - 10:00 PM",
                "tuesday": "11:00 AM - 10:00 PM",
                "wednesday": "11:00 AM - 10:00 PM",
                "thursday": "11:00 AM - 10:00 PM",
                "friday": "11:00 AM - 11:00 PM",
                "saturday": "11:00 AM - 11:00 PM",
                "sunday": "12:00 PM - 9:00 PM"
            }
        )
    ]
    
    # Create the response
    response = RecommendationsResponse(
        restaurants=restaurants,
        matchScore=0.92  # Mock match score
    )
    
    return response, session_id
