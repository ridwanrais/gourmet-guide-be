from pydantic import BaseModel, Field


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
    address: str = Field(..., example="Jakarta, Indonesia")
    city: str = Field(..., example="Jakarta")
    country: str = Field(..., example="Indonesia")
