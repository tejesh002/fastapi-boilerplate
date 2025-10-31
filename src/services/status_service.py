"""
Status service
Handles status check endpoint logic
"""
from fastapi.responses import JSONResponse
from datetime import datetime
import os


def get_status_response():
    """
    Returns detailed status response

    Returns:
        JSONResponse: Detailed status information
    """
    return JSONResponse(
        content={
            "status": "operational",
            "application": "FastAPI Boilerplate",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
