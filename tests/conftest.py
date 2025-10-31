"""
Pytest configuration and fixtures
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import sys
import os

# Add src to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def mock_telemetry():
    """Mock telemetry setup to avoid initializing OpenTelemetry in tests"""
    # Remove main and config modules from cache to ensure fresh import with mocks
    modules_to_remove = []
    for key in list(sys.modules.keys()):
        if (
            key in ("main", "config", "config.telemetry")
            or key.startswith("main.")
            or key.startswith("config.")
        ):
            modules_to_remove.append(key)

    for module in modules_to_remove:
        if module in sys.modules:
            del sys.modules[module]

    with patch("config.telemetry.setup_telemetry") as mock_setup:
        mock_counter = MagicMock()
        mock_setup.return_value = (MagicMock(), mock_counter)
        yield mock_counter


@pytest.fixture
def client(mock_telemetry):
    """Create a test client for the FastAPI app"""
    # Import here to ensure mocks are in place
    # The mock_telemetry fixture ensures main is re-imported with mocks
    import main

    # Patch the health_endpoint_counter in the main module to use our mock
    main.health_endpoint_counter = mock_telemetry

    return TestClient(main.app)


@pytest.fixture
def env_setup(monkeypatch):
    """Set up environment variables for testing"""
    monkeypatch.setenv("ENVIRONMENT", "test")
    yield
    monkeypatch.delenv("ENVIRONMENT", raising=False)
