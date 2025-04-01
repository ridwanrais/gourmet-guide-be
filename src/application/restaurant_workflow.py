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
from src.utils.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

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
    logger.info(f"Starting restaurant recommendation workflow: coordinates={coordinates}, prompt='{prompt}', limit={limit}")

    # First, fetch real restaurant data from GoFood API
    logger.debug(f"Fetching restaurant data from GoFood API for coordinates: {coordinates}")
    restaurants_data = fetch_restaurants_from_gofood(coordinates)
    logger.info(f"Retrieved {len(restaurants_data)} restaurants from GoFood API")

    # Get LLM with Deepseek R1 model from OpenRouter
    logger.debug("Initializing OpenAI client for LLM processing")
    llm = get_openai_client()

    # Get the response from the LLM - single call for both filtering and analysis
    logger.debug(f"Sending request to LLM with model={settings.OPENROUTER_MODEL} for filtering and analysis")
    response = llm.chat.completions.create(
        model=settings.OPENROUTER_MODEL,
        temperature=0.7,
        extra_headers={
            "HTTP-Referer": "https://gourmetguide.ai",
            "X-Title": "Gourmet Guide AI"
        },
        messages=[
            {"role": "system", "content": "You are a restaurant analysis assistant. Filter and analyze restaurants based on user preferences."},
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

            Available restaurants:
            {json.dumps(restaurants_data, ensure_ascii=False)}
            """}
        ]
    )

    if response.model_extra.get('error'):
        logger.error(f"Error from LLM: {response.model_extra['error']}")
        raise RuntimeError("There was an error while the AI analyze your request. Please try again later.")



    response_content = response.choices[0].message.content if response.choices else None
    logger.debug("Successfully received response from LLM")
    logger.debug(f"LLM Response: {response_content}")

    # In a real application, we would parse the response and extract structured data
    # For this example, we'll return the raw response
    result = {
        "coordinates": {"latitude": coordinates.latitude, "longitude": coordinates.longitude},
        "prompt": prompt,
        "user_id": user_id,
        "restaurants_data": restaurants_data,
        "analysis_response": response_content
    }

    logger.info("Restaurant recommendation workflow completed successfully")
    return result


def fetch_restaurants_from_gofood(coordinates: Coordinates) -> List[Dict[str, Any]]:
    """
    Fetch restaurant data from GoFood API based on coordinates.

    Args:
        coordinates: The user's location coordinates

    Returns:
        List of restaurant data from GoFood API
    """
    logger.info(f"Fetching restaurants from GoFood API for coordinates: {coordinates}")
    # Find the nearest service area based on coordinates
    service_area, locality = get_nearest_service_area(coordinates)
    logger.debug(f"Using service area: {service_area}, locality: {locality}")

    # Construct the GoFood API URL
    url = f"https://gofood.co.id/_next/data/16.0.0/en/{service_area}/{locality}-restaurants/near_me.json?service_area={service_area}"
    logger.debug(f"GoFood API URL: {url}")

    try:
        # Make the API request
        headers = {
            "User-Agent": "GourmetGuideAPI/1.0",
            "Accept": "application/json"
        }
        logger.debug("Sending request to GoFood API")
        response = requests.get(url, headers=headers)
        logger.debug(f"GoFood API response status code: {response.status_code}")

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            logger.debug("Successfully parsed GoFood API response as JSON")

            # Extract the outlets from the response
            outlets = data.get("pageProps", {}).get("outlets", [])
            logger.info(f"Found {len(outlets)} outlets in GoFood API response")

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

            logger.info(f"Processed {len(processed_outlets)} outlets from GoFood API")
            return processed_outlets
        else:
            # If the request failed, return an empty list
            logger.warning(f"Failed to fetch data from GoFood API: {response.status_code}")
            print(f"Failed to fetch data from GoFood API: {response.status_code}")
            return []
    except Exception as e:
        # If an exception occurred, return an empty list
        logger.error(f"Error fetching data from GoFood API: {str(e)}", exc_info=True)
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
    logger.debug(f"Finding nearest service area for coordinates: {coordinates}")
    # For now, we'll just return Bali and Kuta Utara as defaults
    # In a real application, this would use a more sophisticated approach
    logger.debug("Using default service area: bali, locality: kuta-utara")
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
    logger.debug(f"Calculating distance between ({lat1}, {lon1}) and ({lat2}, {lon2})")
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

    logger.debug(f"Calculated distance: {distance:.2f} km")
    return distance


def parse_llm_response_to_json(response_content: str) -> Dict[str, Any]:
    """
    Parse the LLM response to extract JSON content.

    Args:
        response_content: The raw response content from the LLM

    Returns:
        Parsed JSON as a dictionary
    """
    if not response_content:
        logger.warning("Empty response content received from LLM")
        return {"selected_restaurants": [], "match_score": 0.0}

    logger.debug("Attempting to parse LLM response to JSON")

    try:
        # First, try to parse the entire content as JSON
        analysis = json.loads(response_content)
        logger.debug("Successfully parsed entire content as JSON")
        return analysis
    except json.JSONDecodeError:
        logger.warning("Failed to parse entire content as JSON, trying alternative methods")
        # If that fails, try to extract JSON from the text
        try:
            # Look for JSON content between triple backticks
            import re
            logger.debug("Looking for JSON between triple backticks")
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_content)
            if json_match:
                logger.debug("Found JSON between triple backticks")
                json_str = json_match.group(1)
                return json.loads(json_str)
            else:
                # Try to find JSON between curly braces
                logger.debug("Looking for JSON between curly braces")
                json_match = re.search(r'({[\s\S]*})', response_content)
                if json_match:
                    logger.debug("Found JSON between curly braces")
                    json_str = json_match.group(1)
                    return json.loads(json_str)
                else:
                    # Try to find JSON in a boxed format
                    logger.debug("Looking for JSON in boxed format")
                    boxed_match = re.search(r'\\boxed{([\s\S]*)}', response_content)
                    if boxed_match:
                        logger.debug("Found JSON in boxed format")
                        boxed_content = boxed_match.group(1)
                        # Now try to extract JSON from the boxed content
                        json_in_box_match = re.search(r'```json\s*([\s\S]*?)\s*```', boxed_content)
                        if json_in_box_match:
                            logger.debug("Found JSON between triple backticks in boxed content")
                            json_str = json_in_box_match.group(1)
                            return json.loads(json_str)
                        else:
                            raise Exception("Could not extract JSON from boxed content")
                    else:
                        raise Exception("Could not extract JSON from LLM response")
        except Exception as e:
            logger.error(f"Error extracting JSON: {str(e)}", exc_info=True)
            # Return empty result instead of raising exception
            return {"selected_restaurants": [], "match_score": 0.0}


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
    logger.info(f"Starting restaurant recommendation service: coordinates={coordinates}, prompt='{prompt}'")

    # Generate a session ID for tracking this recommendation request
    session_id = str(uuid.uuid4())
    logger.debug(f"Generated session ID: {session_id}")

    # Set default values if not provided
    radius = radius or 5.0
    limit = limit or 5
    logger.debug(f"Using radius={radius}km, limit={limit}")

    # Run the restaurant recommendation workflow using LangGraph
    logger.debug("Running restaurant recommendation workflow")
    result = run_restaurant_recommendation_workflow(
        coordinates=coordinates,
        prompt=prompt,
        user_id=user_id,
        radius=radius,
        limit=limit
    )
    logger.debug("Restaurant recommendation workflow completed")

    # Process the restaurants data from GoFood API
    restaurants = []

    # If we have restaurant data from GoFood
    if result.get("restaurants_data"):
        logger.debug(f"Processing {len(result.get('restaurants_data'))} restaurants from GoFood API")

        # Parse the LLM response to extract structured data
        analysis_response = result.get("analysis_response")
        logger.debug(f"Parsing analysis response from LLM")

        try:
            # Try to extract JSON from the response
            logger.debug("Attempting to parse JSON from LLM response")
            analysis = parse_llm_response_to_json(analysis_response)
            logger.debug("Successfully parsed JSON from LLM response")

            logger.info(f"Successfully analyzed {len(analysis.get('selected_restaurants', []))} restaurants")

            # Create Restaurant objects from the analysis
            for selected in analysis.get("selected_restaurants", []):
                restaurant_id = selected.get("id")
                if restaurant_id in [r.get("id") for r in result.get("restaurants_data")]:
                    data = next(r for r in result.get("restaurants_data") if r.get("id") == restaurant_id)
                    logger.debug(f"Processing restaurant: {data.get('name')}")

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
                    logger.debug(f"Added {len(popular_items)} popular items for restaurant {data.get('name')}")

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
                        address=data.get("location", {}).get("address", ""),
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
                    logger.debug(f"Added restaurant {data.get('name')} to recommendations")
        except Exception as e:
            logger.error(f"Error processing restaurant analysis: {str(e)}", exc_info=True)
            print(f"Error processing restaurant analysis: {str(e)}")

    # Create the response with match score
    match_score = 0.7  # Default match score
    try:
        if "match_score" in analysis:
            match_score = float(analysis.get("match_score", 0.92))
            logger.debug(f"Using match score from analysis: {match_score}")
    except:
        logger.warning("Could not extract match score from analysis, using default")
        pass

    response = RecommendationsResponse(
        restaurants=restaurants,
        matchScore=match_score
    )
    logger.info(f"Created response with {len(restaurants)} restaurants and match score {match_score}")

    return response, session_id
