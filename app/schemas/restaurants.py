from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Coordinates(BaseModel):
    latitude: float = Field(..., example=-6.2088)
    longitude: float = Field(..., example=106.8456)


class RecommendationRequest(BaseModel):
    location: str = Field(..., example="Jakarta, Indonesia")
    preference: str = Field(..., example="I want something spicy and vegetarian")
    coordinates: Optional[Coordinates] = Field(None)
    radius: Optional[float] = Field(None, example=5.0, description="Search radius in kilometers")
    limit: Optional[int] = Field(None, example=5, description="Maximum number of recommendations to return")
    userId: Optional[str] = Field(None, example="user123", description="Optional user ID for personalized recommendations")


class FoodItem(BaseModel):
    id: str = Field(..., example="item123")
    name: str = Field(..., example="Butter Chicken")
    price: float = Field(..., example=85000)
    description: str = Field(..., example="Tender chicken in a rich, creamy tomato sauce")
    tags: List[str] = Field(..., example=["Spicy", "Popular", "Meat"])
    imageUrl: Optional[str] = Field(None, example="https://api.gourmetguide.ai/images/butter-chicken.jpg")


class Restaurant(BaseModel):
    id: str = Field(..., example="rest123")
    name: str = Field(..., example="Spice Garden")
    rating: float = Field(..., example=4.7)
    priceRange: str = Field(..., example="$$")
    cuisineTypes: List[str] = Field(..., example=["Indian", "Spicy", "Vegetarian"])
    address: str = Field(..., example="123 Spice Lane, Jakarta")
    coordinates: Coordinates
    distance: float = Field(..., example=1.2, description="Distance in kilometers from the user's location")
    aiDescription: str = Field(
        ...,
        example="Spice Garden stands out for its authentic Indian flavors and generous vegetarian options. Their perfectly balanced spice levels cater to both spice enthusiasts and those who prefer milder tastes. The restaurant's warm ambiance and attentive service make it ideal for both casual dining and special occasions.",
        description="AI-generated description explaining why this restaurant is a good choice based on user preferences"
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
            "sunday": "11:00 AM - 9:00 PM"
        }
    )


class RecommendationsResponse(BaseModel):
    restaurants: List[Restaurant]
    matchScore: Optional[float] = Field(
        None,
        example=0.92,
        description="How well the recommendations match the user's preferences"
    )
