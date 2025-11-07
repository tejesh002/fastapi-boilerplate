"""
Home/Root service
Handles root endpoint logic
"""

from fastapi.responses import JSONResponse


def get_root_response():
    """
    Returns root endpoint response

    Returns:
        JSONResponse: Root endpoint information
    """
    return JSONResponse(
        content={
            "message": "Welcome to FastAPI Boilerplate",
            "docs": "/docs",
            "health": "/health",
            "status": "/status",
        }
    )
