"""
FastAPI Boilerplate
Main application file with health and status routes
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import os

app = FastAPI(
    title="FastAPI Boilerplate",
    description="A production-ready FastAPI boilerplate",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(content={
        "message": "Welcome to FastAPI Boilerplate",
        "docs": "/docs",
        "health": "/health",
        "status": "/status"
    })


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.get("/status")
async def status_check():
    """Detailed status endpoint"""
    return JSONResponse(content={
        "status": "operational",
        "application": "FastAPI Boilerplate",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat()
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

