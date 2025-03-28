from fastapi import APIRouter, HTTPException, status
from app.schemas.location import AddressRequest, CoordinatesRequest, CoordinatesResponse, AddressResponse
from app.schemas.common import ErrorResponse, ErrorDetail

router = APIRouter(prefix="/location", tags=["location"])


@router.post("/geocode", response_model=CoordinatesResponse, responses={400: {"model": ErrorResponse}})
async def geocode_address(request: AddressRequest):
    """
    Convert a text address to geographic coordinates.
    
    In a real implementation, this would call a geocoding service like Google Maps,
    Mapbox, or OpenStreetMap. For this example, we'll return mock data.
    """
    try:
        # Mock implementation - in a real app, this would call a geocoding API
        if not request.address:
            raise ValueError("Address cannot be empty")
        
        # Mock data for Jakarta, Indonesia
        if "jakarta" in request.address.lower():
            return CoordinatesResponse(
                latitude=-6.2088,
                longitude=106.8456,
                formattedAddress="Jakarta, Indonesia"
            )
        # Mock data for Singapore
        elif "singapore" in request.address.lower():
            return CoordinatesResponse(
                latitude=1.3521,
                longitude=103.8198,
                formattedAddress="Singapore"
            )
        # Default mock data
        else:
            return CoordinatesResponse(
                latitude=-6.2088,
                longitude=106.8456,
                formattedAddress=request.address
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                message="Invalid address supplied",
                details=str(e),
                code="INVALID_ADDRESS"
            ).dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorDetail(
                message="An error occurred while processing the request",
                details=str(e),
                code="SERVER_ERROR"
            ).dict()
        )


@router.post("/reverse-geocode", response_model=AddressResponse, responses={400: {"model": ErrorResponse}})
async def reverse_geocode_coordinates(request: CoordinatesRequest):
    """
    Convert geographic coordinates to a text address.
    
    In a real implementation, this would call a reverse geocoding service.
    For this example, we'll return mock data.
    """
    try:
        # Mock implementation - in a real app, this would call a reverse geocoding API
        # Jakarta coordinates (approximate)
        if abs(request.latitude + 6.2088) < 0.1 and abs(request.longitude - 106.8456) < 0.1:
            return AddressResponse(
                address="Jakarta, Indonesia",
                city="Jakarta",
                country="Indonesia"
            )
        # Singapore coordinates (approximate)
        elif abs(request.latitude - 1.3521) < 0.1 and abs(request.longitude - 103.8198) < 0.1:
            return AddressResponse(
                address="Singapore",
                city="Singapore",
                country="Singapore"
            )
        # Default mock data
        else:
            return AddressResponse(
                address=f"Location at {request.latitude}, {request.longitude}",
                city="Unknown City",
                country="Unknown Country"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                message="Invalid coordinates supplied",
                details=str(e),
                code="INVALID_COORDINATES"
            ).dict()
        )
