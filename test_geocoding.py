import asyncio

from src.application.services import (geocode_address_service,
                                      reverse_geocode_service)


async def test_geocoding():
    """Test the geocoding service with a real address"""
    try:
        print("Testing geocoding service...")

        # Test forward geocoding
        address = "Jakarta, Indonesia"
        print(f"Geocoding address: {address}")
        result = await geocode_address_service(address)
        print(f"Result: {result}")

        # Test reverse geocoding using the coordinates we got
        print("\nTesting reverse geocoding service...")
        lat, lon = result.latitude, result.longitude
        print(f"Reverse geocoding coordinates: {lat}, {lon}")
        address_result = await reverse_geocode_service(lat, lon)
        print(f"Result: {address_result}")

        print("\nGeocoding tests completed successfully!")
    except Exception as e:
        print(f"Error during testing: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_geocoding())
