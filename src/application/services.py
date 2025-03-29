from typing import List
from langchain_core.prompts import ChatPromptTemplate
from src.application.workflows import get_llm
from src.domain.value_objects import CoordinatesResponse, AddressResponse


async def generate_food_preference_suggestions(count: int = 5) -> List[str]:
    """
    Generate food preference suggestions using LLM.
    
    Args:
        count: Number of suggestions to return
        
    Returns:
        List of food preference suggestions
    """
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
    
    return suggestions


async def geocode_address_service(address: str) -> CoordinatesResponse:
    """
    Convert a text address to geographic coordinates.
    
    In a real implementation, this would call a geocoding service like Google Maps,
    Mapbox, or OpenStreetMap. For this example, we'll return mock data.
    
    Args:
        address: The address to geocode
        
    Returns:
        Coordinates with formatted address
    """
    if not address:
        raise ValueError("Address cannot be empty")
    
    # Mock data for Jakarta, Indonesia
    if "jakarta" in address.lower():
        return CoordinatesResponse(
            latitude=-6.2088,
            longitude=106.8456,
            formattedAddress="Jakarta, Indonesia"
        )
    # Mock data for Singapore
    elif "singapore" in address.lower():
        return CoordinatesResponse(
            latitude=1.3521,
            longitude=103.8198,
            formattedAddress="Singapore"
        )
    # Default mock data
    else:
        raise ValueError(f"Mock geocoding service could not resolve address: {address}")

        return CoordinatesResponse(
            latitude=-6.2087,
            longitude=106.8456,
            formattedAddress=address
        )


async def reverse_geocode_service(latitude: float, longitude: float) -> AddressResponse:
    """
    Convert geographic coordinates to a text address.
    
    In a real implementation, this would call a reverse geocoding service.
    For this example, we'll return mock data.
    
    Args:
        latitude: The latitude coordinate
        longitude: The longitude coordinate
        
    Returns:
        Address information
    """
    # Jakarta coordinates (approximate)
    if abs(latitude + 6.2088) < 0.1 and abs(longitude - 106.8456) < 0.1:
        return AddressResponse(
            address="Jakarta, Indonesia",
            city="Jakarta",
            country="Indonesia"
        )
    # Singapore coordinates (approximate)
    elif abs(latitude - 1.3521) < 0.1 and abs(longitude - 103.8198) < 0.1:
        return AddressResponse(
            address="Singapore",
            city="Singapore",
            country="Singapore"
        )
    # Default mock data
    else:
        return AddressResponse(
            address=f"Location at {latitude}, {longitude}",
            city="Unknown City",
            country="Unknown Country"
        )
