"""CORS middleware configuration."""

from __future__ import annotations

import os
from typing import Iterable, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def _get_allowed_origins() -> List[str]:
    """Read allowed CORS origins from environment variables."""
    raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    if not raw_origins:
        return ["*"]
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def add_cors_middleware(app: FastAPI) -> None:
    """Attach CORS middleware to the FastAPI application."""
    allow_origins: Iterable[str] = _get_allowed_origins()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(allow_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time-ms"],
    )
