"""
Root API routes
"""

from fastapi import APIRouter

from src.models.schemas import RootResponse
from src.services.home_service import get_root_response


router = APIRouter(tags=["root"])


@router.get(
    "/",
    summary="Root endpoint",
    description="Returns welcome message and available API endpoints",
    response_model=RootResponse,
    responses={
        200: {
            "description": "Successful response with API information",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Welcome to FastAPI Boilerplate",
                        "docs": "/docs",
                        "health": "/health",
                        "status": "/status",
                    }
                }
            },
        }
    },
)
async def root():
    """Provide information about the API."""
    return get_root_response()
