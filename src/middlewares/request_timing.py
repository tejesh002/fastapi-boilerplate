"""Request timing middleware for response headers."""

from __future__ import annotations

import time
from typing import Callable

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class ProcessTimeHeaderMiddleware(BaseHTTPMiddleware):
    """Attach the request processing time in milliseconds to response headers."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:  # type: ignore[override]
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Process-Time-ms"] = f"{process_time_ms:.3f}"
        return response


def add_process_time_middleware(app: FastAPI) -> None:
    """Attach the process time middleware to the application."""
    app.add_middleware(ProcessTimeHeaderMiddleware)
