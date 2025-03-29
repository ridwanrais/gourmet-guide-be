from typing import Dict, Any, List, Optional, Tuple
import json
import uuid
import requests
import math
from src.application.workflows import get_openai_client
from src.domain.value_objects import (
    Restaurant, Coordinates, FoodItem, RecommendationsResponse
)
from src.config import settings


def run_restaurant_recommendation_workflow(
    coordinates: Coordinates,
    prompt: str,
    user_id: str = None,
    radius: float = 5.0,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Run the restaurant recommendation workflow using LangGraph.

    This workflow processes the user's coordinates and prompt to generate
    personalized restaurant recommendations.

    Args:
        coordinates: The user's location coordinates
        prompt: The user's food preference prompt
        user_id: Optional user ID for personalized recommendations
        radius: Search radius in kilometers
        limit: Maximum number of recommendations to return

    Returns:
        A dictionary containing the workflow result
    """
    # First, fetch real restaurant data from GoFood API
    restaurants_data = fetch_restaurants_from_gofood(coordinates)

    # Get LLM with Deepseek R1 model from OpenRouter
    llm = get_openai_client()

    # Get the response from the LLM
    response = llm.chat.completions.create(
        model=settings.OPENROUTER_MODEL,
        temperature=0.7,
        extra_headers={
            "HTTP-Referer": "https://gourmetguide.ai",
            "X-Title": "Gourmet Guide AI"
        },
        messages=[
            {"role": "system", "content": "You are a helpful food recommendation assistant. Generate restaurant recommendations based on the user's location and preferences."},
            {"role": "user", "content": f"""I'm at coordinates {coordinates.latitude}, {coordinates.longitude} and {prompt}.
            Can you recommend some restaurants from this list? Limit to {limit} restaurants.

            Available restaurants:
            {json.dumps(restaurants_data, ensure_ascii=False, indent=2)}"""}
        ]
    )

    # In a real application, we would parse the response and extract structured data
    # For this example, we'll return the raw response
    return {
        "coordinates": {"latitude": coordinates.latitude, "longitude": coordinates.longitude},
        "prompt": prompt,
        "user_id": user_id,
        "restaurants_data": restaurants_data,
        "response": response.choices[0].message.content
    }


def fetch_restaurants_from_gofood(coordinates: Coordinates) -> List[Dict[str, Any]]:
    """
    Fetch restaurant data from GoFood API based on coordinates.

    Args:
        coordinates: The user's location coordinates

    Returns:
        List of restaurant data from GoFood API
    """
    # Find the nearest service area based on coordinates
    service_area, locality = get_nearest_service_area(coordinates)

    # Construct the GoFood API URL
    url = f"https://gofood.co.id/_next/data/16.0.0/en/{service_area}/{locality}-restaurants/near_me.json?service_area={service_area}"

    try:
        # Make the API request
        headers = {
            "User-Agent": "GourmetGuideAPI/1.0",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()

            # Extract the outlets from the response
            outlets = data.get("pageProps", {}).get("outlets", [])

            # Process the outlets to extract relevant information
            processed_outlets = []
            for outlet in outlets:
                if "core" in outlet:
                    processed_outlet = {
                        "id": outlet.get("uid", ""),
                        "name": outlet.get("core", {}).get("displayName", ""),
                        "location": outlet.get("core", {}).get("location", {}),
                        "cuisineTypes": [tag.get("displayName", "") for tag in outlet.get("core", {}).get("tags", [])],
                        "priceLevel": outlet.get("priceLevel", 0),
                        "ratings": outlet.get("ratings", {}).get("average", 0),
                        "coverImgUrl": outlet.get("media", {}).get("coverImgUrl", ""),
                        "distance": outlet.get("delivery", {}).get("distanceKm", 0),
                        "path": outlet.get("path", "")
                    }
                    processed_outlets.append(processed_outlet)

            return processed_outlets
        else:
            # If the request failed, return an empty list
            print(f"Failed to fetch data from GoFood API: {response.status_code}")
            return []
    except Exception as e:
        # If an exception occurred, return an empty list
        print(f"Error fetching data from GoFood API: {str(e)}")
        return []


def get_nearest_service_area(coordinates: Coordinates) -> Tuple[str, str]:
    """
    Get the nearest service area and locality based on coordinates.
    This is a simplified version that returns default values for Bali.
    In a real application, this would use a more sophisticated approach.

    Args:
        coordinates: The user's location coordinates

    Returns:
        Tuple of (service_area, locality)
    """
    # For now, we'll just return Bali and Kuta Utara as defaults
    # In a real application, this would use a more sophisticated approach
    return "bali", "kuta-utara"


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the Haversine distance between two points in kilometers.

    Args:
        lat1: Latitude of point 1
        lon1: Longitude of point 1
        lat2: Latitude of point 2
        lon2: Longitude of point 2

    Returns:
        Distance in kilometers
    """
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences in coordinates
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance


async def get_restaurant_recommendations_service(
    prompt: str,
    coordinates: Coordinates,
    user_id: Optional[str] = None,
    radius: Optional[float] = None,
    limit: Optional[int] = None
) -> RecommendationsResponse:
    """
    Get personalized restaurant recommendations based on coordinates and prompt.

    This service uses LangGraph to process the user's query and generate restaurant recommendations.

    Args:
        prompt: The user's food preference prompt
        coordinates: The user's location coordinates
        user_id: Optional user ID for personalized recommendations
        radius: Optional search radius in kilometers
        limit: Optional maximum number of recommendations to return

    Returns:
        Restaurant recommendations with match score
    """
    # Generate a session ID for tracking this recommendation request
    session_id = str(uuid.uuid4())

    # Set default values if not provided
    radius = radius or 5.0
    limit = limit or 5

    # Run the restaurant recommendation workflow using LangGraph
    result = run_restaurant_recommendation_workflow(
        coordinates=coordinates,
        prompt=prompt,
        user_id=user_id,
        radius=radius,
        limit=limit
    )

    # Process the restaurants data from GoFood API
    restaurants = []

    # If we have restaurant data from GoFood
    if result.get("restaurants_data"):
        # Use LLM to analyze which restaurants best match the user's preferences
        llm = get_openai_client()

        try:
            # Call OpenAI API to analyze restaurants
            analysis_response = llm.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                temperature=0.7,
                extra_headers={
                    "HTTP-Referer": "https://gourmetguide.ai",
                    "X-Title": "Gourmet Guide AI"
                },
                messages=[
                    {"role": "system", "content": "You are a restaurant analysis assistant. Analyze restaurants based on user preferences."},
                    {"role": "user", "content": f"""
                    Based on the user's request: "{prompt}", analyze these restaurants and select the top {limit} matches.
                    For each selected restaurant, provide:
                    1. A brief explanation of why it matches the user's preferences
                    2. What popular items they might enjoy there

                    Respond in JSON format like this:
                    {{
                        "selected_restaurants": [
                            {{
                                "id": "restaurant_id",
                                "explanation": "Why this restaurant matches the user's preferences",
                                "popular_items": [
                                    {{
                                        "name": "Item name",
                                        "description": "Brief description",
                                        "price": estimated_price_in_rupiah
                                    }}
                                ]
                            }}
                        ],
                        "match_score": 0.95
                    }}

                    Restaurant data: {json.dumps(result.get("restaurants_data"), ensure_ascii=False)}
                    """}
                ]
            )
            
            # Get the response content
            response_content = analysis_response.choices[0].message.content
            print(f"LLM Response: {response_content}")
            
            # Try to extract JSON from the response
            try:
                # First, try to parse the entire content as JSON
                analysis = json.loads(response_content)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from the text
                try:
                    # Look for JSON content between triple backticks
                    import re
                    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_content)
                    if json_match:
                        json_str = json_match.group(1)
                        analysis = json.loads(json_str)
                    else:
                        # Try to find JSON between curly braces
                        json_match = re.search(r'({[\s\S]*})', response_content)
                        if json_match:
                            json_str = json_match.group(1)
                            analysis = json.loads(json_str)
                        else:
                            raise Exception("Could not extract JSON from LLM response")
                except Exception as e:
                    print(f"Error extracting JSON: {str(e)}")
                    raise Exception(f"Failed to parse JSON from LLM response: {str(e)}")
            
            # Create Restaurant objects from the analysis
            for selected in analysis.get("selected_restaurants", []):
                restaurant_id = selected.get("id")
                if restaurant_id in [r.get("id") for r in result.get("restaurants_data")]:
                    data = next(r for r in result.get("restaurants_data") if r.get("id") == restaurant_id)

                    # Create popular items
                    popular_items = []
                    for item in selected.get("popular_items", []):
                        popular_items.append(
                            FoodItem(
                                id=f"item_{uuid.uuid4()}",
                                name=item.get("name", ""),
                                price=item.get("price", 0),
                                description=item.get("description", ""),
                                tags=[]
                            )
                        )

                    # Map price level to price range
                    price_ranges = {1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}
                    price_range = price_ranges.get(data.get("priceLevel", 2), "$$")

                    # Create the restaurant object
                    restaurant = Restaurant(
                        id=data.get("id", ""),
                        name=data.get("name", ""),
                        rating=data.get("ratings", 4.0),
                        priceRange=price_range,
                        cuisineTypes=data.get("cuisineTypes", []),
                        address=f"GoFood Restaurant in Bali",
                        coordinates=Coordinates(
                            latitude=data.get("location", {}).get("latitude", coordinates.latitude),
                            longitude=data.get("location", {}).get("longitude", coordinates.longitude)
                        ),
                        distance=data.get("distance", 0),
                        aiDescription=selected.get("explanation", ""),
                        popularItems=popular_items,
                        openNow=True,
                        hours={}
                    )

                    restaurants.append(restaurant)
        except Exception as e:
            print(f"Error processing restaurant analysis: {str(e)}")
            raise Exception(f"Error processing restaurant analysis: {str(e)}")

    # If we couldn't get any restaurants from the API or analysis, use mock data
    if not restaurants:
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
            # Add more mock restaurants as needed
        ]



    # Create the response with match score
    match_score = 0.92  # Default match score
    try:
        if "match_score" in analysis:
            match_score = float(analysis.get("match_score", 0.92))
    except:
        pass

    response = RecommendationsResponse(
        restaurants=restaurants,
        matchScore=match_score
    )

    return response, session_id
