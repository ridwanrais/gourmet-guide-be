from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    message: str = Field(..., example="The requested resource was not found.")
    details: Optional[str] = Field(None, example="User not found.")
    code: Optional[str] = Field(None, example="NF_01")


class ErrorResponse(BaseModel):
    error: ErrorDetail


# Location Value Objects
class AddressRequest(BaseModel):
    address: str = Field(..., example="Jakarta, Indonesia")


class CoordinatesRequest(BaseModel):
    latitude: float = Field(..., example=-6.2088)
    longitude: float = Field(..., example=106.8456)


class CoordinatesResponse(BaseModel):
    latitude: float = Field(..., example=-6.2088)
    longitude: float = Field(..., example=106.8456)
    formattedAddress: str = Field(..., example="Jakarta, Indonesia")


class AddressResponse(BaseModel):
    street: Optional[str] = Field(None, example="Jalan Sudirman 123")
    city: Optional[str] = Field(None, example="Jakarta")
    state: Optional[str] = Field(None, example="DKI Jakarta")
    country: Optional[str] = Field(None, example="Indonesia")
    postalCode: Optional[str] = Field(None, example="10110")
    formattedAddress: str = Field(
        ..., example="Jalan Sudirman 123, Jakarta, DKI Jakarta, 10110, Indonesia"
    )


# Preferences Value Objects
class SuggestionsResponse(BaseModel):
    suggestions: List[str] = Field(
        ...,
        example=[
            "I feel like eating something spicy and cheap",
            "Recommend a healthy lunch option",
            "What's a good vegetarian restaurant nearby?",
            "I want something quick and filling",
            "Show me the best-rated restaurants",
        ],
    )


# Restaurant Value Objects
class Coordinates(BaseModel):
    latitude: float = Field(..., example=-6.2088)
    longitude: float = Field(..., example=106.8456)


class RecommendationRequest(BaseModel):
    coordinates: Coordinates = Field(
        ..., description="User's current location coordinates"
    )
    prompt: str = Field(
        ...,
        example="Find me a place to eat! I'm looking for Italian food. Preferably something mid-range, and I'd love outdoor seating with vegetarian options.",
    )
    radius: Optional[float] = Field(
        None, example=5.0, description="Search radius in kilometers"
    )
    limit: Optional[int] = Field(
        None, example=5, description="Maximum number of recommendations to return"
    )
    userId: Optional[str] = Field(
        None,
        example="user123",
        description="Optional user ID for personalized recommendations",
    )


class FoodItem(BaseModel):
    id: str = Field(..., example="item123")
    name: str = Field(..., example="Butter Chicken")
    price: float = Field(..., example=85000)
    description: str = Field(
        ..., example="Tender chicken in a rich, creamy tomato sauce"
    )
    tags: List[str] = Field(..., example=["Spicy", "Popular", "Meat"])
    imageUrl: Optional[str] = Field(
        None, example="https://api.gourmetguide.ai/images/butter-chicken.jpg"
    )


class Restaurant(BaseModel):
    id: str = Field(..., example="rest123")
    name: str = Field(..., example="Spice Garden")
    rating: float = Field(..., example=4.7)
    priceRange: str = Field(..., example="$$")
    cuisineTypes: List[str] = Field(..., example=["Indian", "Spicy", "Vegetarian"])
    address: str = Field(..., example="123 Spice Lane, Jakarta")
    coordinates: Coordinates
    distance: float = Field(
        ..., example=1.2, description="Distance in kilometers from the user's location"
    )
    gojekUrl: str = Field(
        ...,
        example="https://gofood.co.id/en/yogyakarta/restaurant/291b1f35-5f17-4dc7-89c2-27e7deb0e615",
        description="GoFood URL for the restaurant",
    )
    aiDescription: str = Field(
        ...,
        example="Spice Garden stands out for its authentic Indian flavors and generous vegetarian options. Their perfectly balanced spice levels cater to both spice enthusiasts and those who prefer milder tastes. The restaurant's warm ambiance and attentive service make it ideal for both casual dining and special occasions.",
        description="AI-generated description explaining why this restaurant is a good choice based on user preferences",
    )
    popularItems: Optional[List[FoodItem]] = None
    openNow: Optional[bool] = Field(None, example=True)
    hours: Optional[Dict[str, str]] = Field(
        None,
        example={
            "monday": "10:00 AM - 10:00 PM",
            "tuesday": "10:00 AM - 10:00 PM",
            "wednesday": "10:00 AM - 10:00 PM",
            "thursday": "10:00 AM - 10:00 PM",
            "friday": "10:00 AM - 11:00 PM",
            "saturday": "10:00 AM - 11:00 PM",
            "sunday": "11:00 AM - 9:00 PM",
        },
    )


class RecommendationsResponse(BaseModel):
    restaurants: List[Restaurant]
    matchScore: Optional[float] = Field(
        None,
        example=0.92,
        description="How well the recommendations match the user's preferences",
    )
