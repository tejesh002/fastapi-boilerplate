"""Application middleware registration utilities."""

from fastapi import FastAPI

from .compression import add_compression_middleware
from .cors import add_cors_middleware
from .request_timing import add_process_time_middleware

__all__ = ["register_middlewares"]


def register_middlewares(app: FastAPI) -> None:
    """Register all application middlewares."""
    add_cors_middleware(app)
    add_compression_middleware(app)
    add_process_time_middleware(app)
