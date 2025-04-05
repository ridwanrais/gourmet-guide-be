from fastapi import HTTPException, status

from src.domain.value_objects import ErrorDetail


class ErrorHandlers:
    @staticmethod
    def handle_invalid_address(e: Exception):
        """Handle invalid address errors"""
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                message="Invalid address supplied",
                details=str(e),
                code="INVALID_ADDRESS",
            ).dict(),
        )

    @staticmethod
    def handle_invalid_coordinates(e: Exception):
        """Handle invalid coordinates errors"""
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                message="Invalid coordinates supplied",
                details=str(e),
                code="INVALID_COORDINATES",
            ).dict(),
        )

    @staticmethod
    def handle_server_error(e: Exception):
        """Handle general server errors"""
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorDetail(
                message="An error occurred while processing the request",
                details=str(e),
                code="SERVER_ERROR",
            ).dict(),
        )

    @staticmethod
    def handle_invalid_preferences(e: Exception):
        """Handle invalid preferences errors"""
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                message="Invalid preferences supplied",
                details=str(e),
                code="INVALID_PREFERENCES",
            ).dict(),
        )

    @staticmethod
    def handle_invalid_request(e: Exception):
        """Handle general invalid request errors"""
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                message="Invalid request parameters",
                details=str(e),
                code="INVALID_REQUEST",
            ).dict(),
        )
