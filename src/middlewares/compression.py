"""Response compression middleware configuration."""

from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware


def add_compression_middleware(app: FastAPI, minimum_size: int = 1024) -> None:
    """Attach gzip compression middleware with sensible defaults."""
    app.add_middleware(GZipMiddleware, minimum_size=minimum_size)
