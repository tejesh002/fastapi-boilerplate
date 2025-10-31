"""
FastAPI Boilerplate
Main application file with health and status routes
"""
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from config.telemetry import setup_telemetry
from services.home_service import get_root_response
from services.health_service import get_health_response
from services.status_service import get_status_response
from models.schemas import RootResponse, HealthResponse, StatusResponse

# Enhanced FastAPI app configuration
app = FastAPI(
    title="FastAPI Boilerplate",
    description="""
    A production-ready FastAPI boilerplate with:
    
    * **Health Checks**: Monitor application health
    * **Status**: Get detailed application status
    * **Observability**: Integrated OpenTelemetry for tracing and metrics
    
    ## Features
    
    * FastAPI with automatic API documentation
    * OpenTelemetry integration for distributed tracing
    * Prometheus metrics export
    * Health and status endpoints
    """,
    version="1.0.0",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "root",
            "description": "Root endpoint providing API information and available routes",
        },
        {
            "name": "health",
            "description": "Health check endpoints for monitoring and observability",
        },
        {
            "name": "status",
            "description": "Status endpoints providing detailed application information",
        },
    ],
)

# Configure OpenTelemetry
_, health_endpoint_counter = setup_telemetry(app, service_name="fastapi-app")


@app.get(
    "/",
    tags=["root"],
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
    """
    Root endpoint that provides information about the API.

    Returns basic information including links to documentation and other endpoints.
    """
    return get_root_response()


@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Health check endpoint for monitoring application health and metrics tracking",
    response_model=HealthResponse,
    responses={
        200: {
            "description": "Application is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "healthy", "timestamp": "2024-01-01T00:00:00.000000"}
                }
            },
        }
    },
)
async def health_check():
    """
    Health check endpoint for monitoring.

    This endpoint:
    * Returns the current health status of the application
    * Tracks metrics via OpenTelemetry
    * Used by monitoring systems and load balancers
    """
    return get_health_response(health_endpoint_counter)


@app.get(
    "/status",
    tags=["status"],
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
    """
    Detailed status endpoint.

    Returns comprehensive information about the application including:
    * Operational status
    * Application name and version
    * Current environment
    * Timestamp
    """
    return get_status_response()


def custom_openapi():
    """Custom OpenAPI schema generator"""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
