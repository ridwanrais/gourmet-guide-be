from fastapi import APIRouter, HTTPException, status
from src.domain.value_objects import (
    AddressRequest, CoordinatesRequest, CoordinatesResponse, 
    AddressResponse, ErrorResponse, ErrorDetail
)
from src.application.services import geocode_address_service, reverse_geocode_service
from src.utils.error_handlers import ErrorHandlers

router = APIRouter(prefix="/location", tags=["location"])


@router.post("/geocode", response_model=CoordinatesResponse, responses={400: {"model": ErrorResponse}})
async def geocode_address(request: AddressRequest):
    """
    Convert a text address to geographic coordinates.
    
    In a real implementation, this would call a geocoding service like Google Maps,
    Mapbox, or OpenStreetMap. For this example, we'll return mock data.
    """
    try:
        # Call the application service to geocode the address
        return await geocode_address_service(request.address)
            
    except ValueError as e:
        ErrorHandlers.handle_invalid_address(e)
    except Exception as e:
        ErrorHandlers.handle_server_error(e)


@router.post("/reverse-geocode", response_model=AddressResponse, responses={400: {"model": ErrorResponse}})
async def reverse_geocode_coordinates(request: CoordinatesRequest):
    """
    Convert geographic coordinates to a text address.
    
    In a real implementation, this would call a reverse geocoding service.
    For this example, we'll return mock data.
    """
    try:
        # Call the application service to reverse geocode the coordinates
        return await reverse_geocode_service(request.latitude, request.longitude)
            
    except Exception as e:
        ErrorHandlers.handle_invalid_coordinates(e)
