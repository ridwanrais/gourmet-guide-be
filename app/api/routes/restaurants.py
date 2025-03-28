from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.restaurants import RecommendationRequest, RecommendationsResponse, Restaurant, Coordinates, FoodItem
from app.schemas.common import ErrorResponse, ErrorDetail
from app.db.database import get_db
from app.models.timeseries import RestaurantRecommendation
from app.workflows.restaurant_recommendation import run_restaurant_recommendation_workflow
import json
import uuid
from datetime import datetime

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.post("/recommendations", response_model=RecommendationsResponse, responses={400: {"model": ErrorResponse}})
async def get_restaurant_recommendations(
    request: RecommendationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized restaurant recommendations based on location and preferences.
    
    This endpoint uses LangGraph to process the user's query and generate restaurant recommendations.
    The results are stored in TimescaleDB for future reference and analytics.
    """
    try:
        # Generate a session ID for tracking this recommendation request
        session_id = str(uuid.uuid4())
        
        # Run the restaurant recommendation workflow using LangGraph
        result = run_restaurant_recommendation_workflow(
            location=request.location,
            preference=request.preference,
            user_id=request.userId
        )
        
        # Extract recommendations from the workflow result
        # In a real application, we would parse and validate the recommendations
        # For this example, we'll create mock data based on the workflow
        
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
        
        # Store the recommendation in TimescaleDB for analytics and history
        db_recommendation = RestaurantRecommendation(
            session_id=session_id,
            user_id=request.userId,
            location=request.location,
            preference=request.preference,
            recommendations=json.dumps([{
                "id": r.id,
                "name": r.name,
                "rating": r.rating,
                "cuisineTypes": r.cuisineTypes
            } for r in restaurants]),
            match_score=response.matchScore
        )
        
        db.add(db_recommendation)
        await db.commit()
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                message="Invalid request parameters",
                details=str(e),
                code="INVALID_REQUEST"
            ).dict()
        )
