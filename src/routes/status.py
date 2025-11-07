"""
Status API routes
"""

from fastapi import APIRouter

from src.models.schemas import StatusResponse
from src.services.status_service import get_status_response


router = APIRouter(tags=["status"])


@router.get(
    "/status",
    summary="Status check",
    description="Detailed status endpoint providing comprehensive application information",
    response_model=StatusResponse,
    responses={
        200: {
            "description": "Detailed application status",
            "content": {
                "application/json": {
                    "example": {
                        "status": "operational",
                        "application": "FastAPI Boilerplate",
                        "version": "1.0.0",
                        "environment": "development",
                        "timestamp": "2024-01-01T00:00:00.000000",
                    }
                }
            },
        }
    },
)
async def status_check():
    """Return detailed application status information."""
    return get_status_response()
