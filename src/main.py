"""
FastAPI Boilerplate
Main application file with health and status routes
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from src.config.telemetry import setup_telemetry
from src.middlewares import register_middlewares
from src.routes import health_router, root_router, status_router

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

# Share telemetry counter with routers via application state
app.state.health_endpoint_counter = health_endpoint_counter

# Register middlewares
register_middlewares(app)

# Register API routers
app.include_router(root_router)
app.include_router(health_router)
app.include_router(status_router)


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
