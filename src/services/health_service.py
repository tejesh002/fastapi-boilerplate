"""
Health service
Handles health check endpoint logic
"""
from fastapi.responses import JSONResponse
from datetime import datetime


def get_health_response(health_counter=None):
    """
    Returns health check response and increments health counter metric

    Args:
        health_counter: Optional health endpoint counter metric

    Returns:
        JSONResponse: Health check status
    """
    # Increment the health endpoint counter metric if provided
    if health_counter:
        health_counter.add(1, {"endpoint": "/health", "status": "healthy"})

    return JSONResponse(content={"status": "healthy", "timestamp": datetime.utcnow().isoformat()})
