"""
Pydantic models for API request/response schemas
Used for Swagger/OpenAPI documentation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class RootResponse(BaseModel):
    """Root endpoint response schema"""

    message: str = Field(..., description="Welcome message")
    docs: str = Field(..., description="API documentation endpoint")
    health: str = Field(..., description="Health check endpoint")
    status: str = Field(..., description="Status endpoint")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Welcome to FastAPI Boilerplate",
                "docs": "/docs",
                "health": "/health",
                "status": "/status",
            }
        }


class HealthResponse(BaseModel):
    """Health check response schema"""

    status: str = Field(..., description="Health status", example="healthy")
    timestamp: str = Field(..., description="ISO format timestamp")

    class Config:
        json_schema_extra = {
            "example": {"status": "healthy", "timestamp": "2024-01-01T00:00:00.000000"}
        }


class StatusResponse(BaseModel):
    """Status check response schema"""

    status: str = Field(..., description="Operational status", example="operational")
    application: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Current environment")
    timestamp: str = Field(..., description="ISO format timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "operational",
                "application": "FastAPI Boilerplate",
                "version": "1.0.0",
                "environment": "development",
                "timestamp": "2024-01-01T00:00:00.000000",
            }
        }
