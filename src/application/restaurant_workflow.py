import json
import math
import os
import random
import time
import urllib.parse
import uuid
from typing import Any, Dict, List, Optional, Tuple

import requests

from src.application.services import reverse_geocode_service
from src.application.workflows import get_openai_client
from src.config import settings
from src.domain.value_objects import (Coordinates, FoodItem,
                                      RecommendationsResponse, Restaurant)
from src.utils.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)


async def run_restaurant_recommendation_workflow(
    coordinates: Coordinates,
    prompt: str,
    user_id: str = None,
    radius: float = 5.0,
    limit: int = 5,
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
    logger.info(
        f"Starting restaurant recommendation workflow: coordinates={coordinates}, prompt='{prompt}', limit={limit}"
    )

    # First, fetch real restaurant data from GoFood API
    logger.debug(
        f"Fetching restaurant data from GoFood API for coordinates: {coordinates}"
    )
    restaurants_data = await fetch_restaurants_from_gofood(coordinates)
    logger.info(f"Retrieved {len(restaurants_data)} restaurants from GoFood API")

    # Get LLM with Deepseek R1 model from OpenRouter
    logger.debug("Initializing OpenAI client for LLM processing")
    llm = get_openai_client()

    # Get the response from the LLM - single call for both filtering and analysis
    logger.debug(
        f"Sending request to LLM with model={settings.OPENROUTER_MODEL} for filtering and analysis"
    )
    response = llm.chat.completions.create(
        model=settings.OPENROUTER_MODEL,
        temperature=0.7,
        extra_headers={
            "HTTP-Referer": "https://gourmetguide.ai",
            "X-Title": "Gourmet Guide AI",
        },
        messages=[
            {
                "role": "system",
                "content": "You are a restaurant analysis assistant. Filter and analyze restaurants based on user preferences.",
            },
            {
                "role": "user",
                "content": f"""
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
            """,
            },
        ],
    )

    if response.model_extra.get("error"):
        logger.error(f"Error from LLM: {response.model_extra['error']}")
        raise RuntimeError(
            "There was an error while the AI analyze your request. Please try again later."
        )

    response_content = response.choices[0].message.content if response.choices else None
    logger.debug("Successfully received response from LLM")
    logger.debug(f"LLM Response: {response_content}")

    # In a real application, we would parse the response and extract structured data
    # For this example, we'll return the raw response
    result = {
        "coordinates": {
            "latitude": coordinates.latitude,
            "longitude": coordinates.longitude,
        },
        "prompt": prompt,
        "user_id": user_id,
        "restaurants_data": restaurants_data,
        "analysis_response": response_content,
    }

    logger.info("Restaurant recommendation workflow completed successfully")
    return result


async def fetch_restaurants_from_gofood(
    coordinates: Coordinates,
) -> List[Dict[str, Any]]:
    """
    Fetch restaurant data from GoFood API based on coordinates.

    Args:
        coordinates: The user's location coordinates

    Returns:
        List of restaurant data from GoFood API
    """
    logger.info(f"Fetching restaurants from GoFood API for coordinates: {coordinates}")

    try:
        # Find the nearest service area based on coordinates
        service_area, locality = await get_nearest_service_area(coordinates)
        logger.debug(f"Using service area: {service_area}, locality: {locality}")

        # Construct the GoFood API URL
        url = f"https://gofood.co.id/_next/data/16.0.0/en/{service_area}/{locality}-restaurants/near_me.json?service_area={service_area}"
        logger.debug(f"GoFood API URL: {url}")

        # Make the API request
        headers = {"User-Agent": "GourmetGuideAPI/1.0", "Accept": "application/json"}
        logger.debug("Sending request to GoFood API")
        response = requests.get(url, headers=headers, timeout=10)
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
                        "cuisineTypes": [
                            tag.get("displayName", "")
                            for tag in outlet.get("core", {}).get("tags", [])
                        ],
                        "priceLevel": outlet.get("priceLevel", 0),
                        "ratings": outlet.get("ratings", {}).get("average", 0),
                        "coverImgUrl": outlet.get("media", {}).get("coverImgUrl", ""),
                        "distance": outlet.get("delivery", {}).get("distanceKm", 0),
                        "path": outlet.get("path", ""),
                    }
                    processed_outlets.append(processed_outlet)

            logger.info(f"Processed {len(processed_outlets)} outlets from GoFood API")
            return processed_outlets
        else:
            logger.warning(
                f"Failed to fetch data from GoFood API: {response.status_code}"
            )
            print(f"Failed to fetch data from GoFood API: {response.status_code}")
            return []

    except RuntimeError as e:
        # This is the error raised when get_nearest_service_area fails
        logger.error(f"Service area determination failed: {str(e)}")
        print(f"Service area determination failed: {str(e)}")
        return []
    except Exception as e:
        logger.error(
            f"Error fetching restaurants from GoFood API: {str(e)}", exc_info=True
        )
        print(f"Error fetching restaurants from GoFood API: {str(e)}")
        return []


async def get_nearest_service_area(coordinates: Coordinates) -> Tuple[str, str]:
    """
    Get the nearest service area and locality based on coordinates.

    Args:
        coordinates: The user's location coordinates

    Returns:
        Tuple of (service_area, locality)
    """
    logger.debug(f"Finding nearest service area for coordinates: {coordinates}")

    try:
        # First, use reverse geocoding to get the address information
        address_response = await reverse_geocode_service(
            coordinates.latitude, coordinates.longitude
        )

        # Use the formatted address as search keyword
        formatted_address = address_response.formattedAddress
        search_keyword = formatted_address.replace(" ", "%20")

        logger.debug(f"Using search keyword: {search_keyword}")

        # Use GoFood API to search for locations using the keyword
        search_url = f"https://gofood.co.id/api/poi/search?keyword={search_keyword}"
        logger.debug(f"Searching GoFood POI API: {search_url}")

        # Make the request to the GoFood API with cookie header
        headers = {
            "cookie": settings.GOFOOD_COOKIE,
            "User-Agent": "GourmetGuideAPI/1.0",
            "Accept": "application/json",
        }

        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the response
            locations = response.json()

            if locations and len(locations) > 0:
                # Find the nearest location from the results
                nearest_location = None
                min_distance = float("inf")

                for location in locations:
                    loc_lat = location.get("latitude")
                    loc_lng = location.get("longitude")

                    if loc_lat is not None and loc_lng is not None:
                        # Calculate distance to this location
                        distance = calculate_distance(
                            coordinates.latitude,
                            coordinates.longitude,
                            loc_lat,
                            loc_lng,
                        )

                        # Update nearest location if this one is closer
                        if distance < min_distance:
                            min_distance = distance
                            nearest_location = location

                if nearest_location:
                    # Extract service area and locality from the nearest location
                    service_area = nearest_location.get("service_area_name", "").lower()
                    locality = nearest_location.get("locality_name", "").lower()

                    # If locality is missing, try to use service area
                    if not locality:
                        locality = service_area

                    logger.debug(
                        f"Determined service area: {service_area}, locality: {locality} (distance: {min_distance:.2f} km)"
                    )
                    return service_area, locality

        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching GoFood POI API: {str(e)}", exc_info=True)
            print(f"Error searching GoFood POI API: {str(e)}")

        # Fallback to using the geocoded address if no suitable location found
        logger.warning(
            "No suitable location found from GoFood POI API, falling back to geocoded address"
        )
        locality = (address_response.city or address_response.state or "bali").lower()
        service_area = (
            address_response.state.lower() if address_response.state else "bali"
        )

        logger.debug(f"Fallback service area: {service_area}, locality: {locality}")
        return service_area, locality

    except Exception as e:
        logger.error(f"Error determining service area: {str(e)}", exc_info=True)
        # Fallback to default values for Bali
        raise RuntimeError("Failed to determine service area and locality")


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
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
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
        logger.warning(
            "Failed to parse entire content as JSON, trying alternative methods"
        )
        # If that fails, try to extract JSON from the text
        try:
            # Look for JSON content between triple backticks
            import re

            logger.debug("Looking for JSON between triple backticks")
            json_match = re.search(r"```json\s*([\s\S]*?)\s*```", response_content)
            if json_match:
                logger.debug("Found JSON between triple backticks")
                json_str = json_match.group(1)
                return json.loads(json_str)
            else:
                # Try to find JSON between curly braces
                logger.debug("Looking for JSON between curly braces")
                json_match = re.search(r"({[\s\S]*})", response_content)
                if json_match:
                    logger.debug("Found JSON between curly braces")
                    json_str = json_match.group(1)
                    return json.loads(json_str)
                else:
                    # Try to find JSON in a boxed format
                    logger.debug("Looking for JSON in boxed format")
                    boxed_match = re.search(r"\\boxed{([\s\S]*)}", response_content)
                    if boxed_match:
                        logger.debug("Found JSON in boxed format")
                        boxed_content = boxed_match.group(1)
                        # Now try to extract JSON from the boxed content
                        json_in_box_match = re.search(
                            r"```json\s*([\s\S]*?)\s*```", boxed_content
                        )
                        if json_in_box_match:
                            logger.debug(
                                "Found JSON between triple backticks in boxed content"
                            )
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
    limit: Optional[int] = None,
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
    logger.info(
        f"Starting restaurant recommendation service: coordinates={coordinates}, prompt='{prompt}'"
    )

    # Generate a session ID for tracking this recommendation request
    session_id = str(uuid.uuid4())
    logger.debug(f"Generated session ID: {session_id}")

    # Set default values if not provided
    radius = radius or 5.0
    limit = limit or 5
    logger.debug(f"Using radius={radius}km, limit={limit}")

    # Run the restaurant recommendation workflow using LangGraph
    logger.debug("Running restaurant recommendation workflow")
    result = await run_restaurant_recommendation_workflow(
        coordinates=coordinates,
        prompt=prompt,
        user_id=user_id,
        radius=radius,
        limit=limit,
    )
    logger.debug("Restaurant recommendation workflow completed")

    # Process the restaurants data from GoFood API
    restaurants = []

    # Get service area for URL generation
    service_area, _ = await get_nearest_service_area(coordinates)
    logger.debug(f"Using service area for URLs: {service_area}")

    # If we have restaurant data from GoFood
    if result.get("restaurants_data"):
        logger.debug(
            f"Processing {len(result.get('restaurants_data'))} restaurants from GoFood API"
        )

        # Parse the LLM response to extract structured data
        analysis_response = result.get("analysis_response")
        logger.debug(f"Parsing analysis response from LLM")

        analysis = parse_llm_response_to_json(analysis_response)
        logger.debug("Successfully parsed JSON from LLM response")

        logger.info(
            f"Successfully analyzed {len(analysis.get('selected_restaurants', []))} restaurants"
        )

        # Create Restaurant objects from the analysis
        for selected in analysis.get("selected_restaurants", []):
            restaurant_id = selected.get("id")
            if restaurant_id in [r.get("id") for r in result.get("restaurants_data")]:
                data = next(
                    r
                    for r in result.get("restaurants_data")
                    if r.get("id") == restaurant_id
                )
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
                            tags=[],
                        )
                    )
                logger.debug(
                    f"Added {len(popular_items)} popular items for restaurant {data.get('name')}"
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
                    address=data.get("location", {}).get("address", ""),
                    coordinates=Coordinates(
                        latitude=data.get("location", {}).get(
                            "latitude", coordinates.latitude
                        ),
                        longitude=data.get("location", {}).get(
                            "longitude", coordinates.longitude
                        ),
                    ),
                    distance=data.get("distance", 0),
                    gojekUrl=f"https://gofood.co.id/en/{service_area}/restaurant/{data.get('id', '')}",
                    aiDescription=selected.get("explanation", ""),
                    popularItems=popular_items,
                    openNow=True,
                    hours={},
                )

                restaurants.append(restaurant)
                logger.debug(f"Added restaurant {data.get('name')} to recommendations")

    # Create the response with match score
    match_score = analysis.get("match_score", 0.7)
    logger.debug(f"Using match score from analysis: {match_score}")

    response = RecommendationsResponse(restaurants=restaurants, matchScore=match_score)
    logger.info(
        f"Created response with {len(restaurants)} restaurants and match score {match_score}"
    )

    return response, session_id
