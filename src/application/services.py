import os
from typing import List, Tuple
from src.application.workflows import get_llm
from src.domain.value_objects import CoordinatesResponse, AddressResponse
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError
import asyncio
from functools import partial
import random

# Initialize the geocoder with a meaningful user agent
geocoder = Nominatim(user_agent="gourmet_guide_api")

# Predefined list of food preference suggestions
FOOD_SUGGESTIONS = [
    "I'm in the mood for something spicy",
    "I want a quick and affordable meal",
    "I'm craving something comforting and hearty",
    "I want a healthy and light option",
    "I'm looking for something vegan-friendly",
    "I want a place with a great atmosphere",
    "I'm in the mood for something sweet",
    "I want a place with quick delivery",
    "I'm craving comfort food",
    "I want something with lots of vegetables",
    "I'm looking for a place with good portion sizes",
    "I want something that's not too heavy",
    "I'm in the mood for street food",
    "I want a place with great reviews",
    "I'm craving something with noodles",
    "I want something that's easy to share",
    "I'm in the mood for something with rice",
    "I want a place with good sides",
    "I'm looking for something with a nice presentation",
    "I want something that's not too spicy"
]

async def generate_food_preference_suggestions(count: int = 5) -> List[str]:
    """
    Generate a list of food preference suggestions.
    
    This function returns a random selection of predefined food preferences.
    """
    # Ensure count is within bounds
    count = min(count, len(FOOD_SUGGESTIONS))
    
    # Return a random selection of suggestions
    return random.sample(FOOD_SUGGESTIONS, count)


async def geocode_address_service(address: str) -> CoordinatesResponse:
    """
    Convert a text address to geographic coordinates using geopy.
    """
    try:
        # Use run_in_executor to run the blocking geocoding operation in a thread pool
        loop = asyncio.get_event_loop()
        # Create a partial function with our parameters
        geocode_func = partial(geocoder.geocode, address, exactly_one=True)
        # Run the function in a thread pool
        location = await loop.run_in_executor(None, geocode_func)

        if location:
            return CoordinatesResponse(
                latitude=location.latitude,
                longitude=location.longitude,
                formattedAddress=location.address
            )
        else:
            raise ValueError(f"Could not geocode address: {address}")
    except (GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError) as e:
        raise ValueError(f"Geocoding service error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error geocoding address: {str(e)}")


async def reverse_geocode_service(latitude: float, longitude: float) -> AddressResponse:
    """
    Convert geographic coordinates to a text address using geopy.
    """
    try:
        # Use run_in_executor to run the blocking reverse geocoding operation in a thread pool
        loop = asyncio.get_event_loop()
        # Create a partial function with our parameters
        reverse_func = partial(geocoder.reverse, (latitude, longitude), exactly_one=True)
        # Run the function in a thread pool
        location = await loop.run_in_executor(None, reverse_func)

        if location:
            # Parse the address components
            address_components = location.raw.get('address', {})

            # Extract relevant address components
            street = address_components.get('road', '')
            house_number = address_components.get('house_number', '')
            city = address_components.get('city', address_components.get('town', address_components.get('village', '')))
            state = address_components.get('state', '')
            country = address_components.get('country', '')
            postal_code = address_components.get('postcode', '')

            # Format the address
            formatted_address = location.address

            return AddressResponse(
                street=f"{house_number} {street}".strip(),
                city=city,
                state=state,
                country=country,
                postalCode=postal_code,
                formattedAddress=formatted_address
            )
        else:
            raise ValueError(f"Could not reverse geocode coordinates: {latitude}, {longitude}")
    except (GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError) as e:
        raise ValueError(f"Geocoding service error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error reverse geocoding coordinates: {str(e)}")
