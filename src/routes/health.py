"""
Health API routes
"""

from fastapi import APIRouter, Request

from src.models.schemas import HealthResponse
from src.services.health_service import get_health_response


router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Health check",
    description="Health check endpoint for monitoring application health and metrics tracking",
    response_model=HealthResponse,
    responses={
        200: {
            "description": "Application is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2024-01-01T00:00:00.000000",
                    }
                }
            },
        }
    },
)
async def health_check(request: Request):
    """Return the current health status and update telemetry metrics."""
    health_counter = getattr(request.app.state, "health_endpoint_counter", None)
    return get_health_response(health_counter)
