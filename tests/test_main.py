"""
Tests for main.py endpoints
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
import os


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_endpoint_returns_success(self, client):
        """Test that root endpoint returns 200 status"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK

    def test_root_endpoint_returns_correct_message(self, client):
        """Test that root endpoint returns correct message"""
        response = client.get("/")
        data = response.json()

        assert "message" in data
        assert data["message"] == "Welcome to FastAPI Boilerplate"
        assert "docs" in data
        assert data["docs"] == "/docs"
        assert "health" in data
        assert data["health"] == "/health"
        assert "status" in data
        assert data["status"] == "/status"

    def test_root_endpoint_response_structure(self, client):
        """Test that root endpoint response matches schema"""
        response = client.get("/")
        data = response.json()

        required_fields = ["message", "docs", "health", "status"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
            assert isinstance(data[field], str), f"Field {field} should be a string"


class TestHealthEndpoint:
    """Tests for the health check endpoint"""

    def test_health_endpoint_returns_success(self, client, mock_telemetry):
        """Test that health endpoint returns 200 status"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

    def test_health_endpoint_returns_healthy_status(self, client, mock_telemetry):
        """Test that health endpoint returns healthy status"""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)

    def test_health_endpoint_increments_counter(self, client, mock_telemetry):
        """Test that health endpoint increments the metrics counter"""
        client.get("/health")

        # Verify that the counter's add method was called
        assert mock_telemetry.add.called
        call_args = mock_telemetry.add.call_args

        # Check the arguments: first should be the increment value (1)
        # second should be the attributes dict
        assert call_args[0][0] == 1
        assert "endpoint" in call_args[0][1]
        assert call_args[0][1]["endpoint"] == "/health"
        assert "status" in call_args[0][1]
        assert call_args[0][1]["status"] == "healthy"

    def test_health_endpoint_timestamp_format(self, client, mock_telemetry):
        """Test that health endpoint returns valid ISO timestamp"""
        response = client.get("/health")
        data = response.json()

        # Check timestamp is ISO format (contains T and Z or timezone info)
        timestamp = data["timestamp"]
        assert "T" in timestamp  # ISO format has T separator
        # Should be able to parse as ISO format
        from datetime import datetime

        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            # Try without Z
            datetime.fromisoformat(timestamp)


class TestStatusEndpoint:
    """Tests for the status endpoint"""

    def test_status_endpoint_returns_success(self, client, env_setup):
        """Test that status endpoint returns 200 status"""
        response = client.get("/status")
        assert response.status_code == status.HTTP_200_OK

    def test_status_endpoint_returns_correct_fields(self, client, env_setup):
        """Test that status endpoint returns all required fields"""
        response = client.get("/status")
        data = response.json()

        required_fields = ["status", "application", "version", "environment", "timestamp"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
            assert isinstance(data[field], str), f"Field {field} should be a string"

    def test_status_endpoint_values(self, client, env_setup):
        """Test that status endpoint returns correct values"""
        response = client.get("/status")
        data = response.json()

        assert data["status"] == "operational"
        assert data["application"] == "FastAPI Boilerplate"
        assert data["version"] == "1.0.0"
        assert data["environment"] == "test"  # Set by env_setup fixture

    def test_status_endpoint_timestamp_format(self, client, env_setup):
        """Test that status endpoint returns valid ISO timestamp"""
        response = client.get("/status")
        data = response.json()

        # Check timestamp is ISO format
        timestamp = data["timestamp"]
        assert "T" in timestamp
        from datetime import datetime

        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            datetime.fromisoformat(timestamp)

    def test_status_endpoint_default_environment(self, client):
        """Test that status endpoint uses default environment when not set"""
        # Ensure ENVIRONMENT is not set
        if "ENVIRONMENT" in os.environ:
            original_env = os.environ["ENVIRONMENT"]
            del os.environ["ENVIRONMENT"]

        try:
            response = client.get("/status")
            data = response.json()
            assert data["environment"] == "development"  # Default value
        finally:
            # Restore original environment if it existed
            if "original_env" in locals():
                os.environ["ENVIRONMENT"] = original_env


class TestOpenAPIDocumentation:
    """Tests for OpenAPI/Swagger documentation"""

    def test_openapi_schema_exists(self, client):
        """Test that OpenAPI schema endpoint exists"""
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK

    def test_openapi_schema_structure(self, client):
        """Test that OpenAPI schema has correct structure"""
        response = client.get("/openapi.json")
        schema = response.json()

        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        assert schema["info"]["title"] == "FastAPI Boilerplate"
        assert schema["info"]["version"] == "1.0.0"

    def test_openapi_paths_defined(self, client):
        """Test that all endpoints are defined in OpenAPI schema"""
        response = client.get("/openapi.json")
        schema = response.json()

        paths = schema["paths"]
        assert "/" in paths
        assert "/health" in paths
        assert "/status" in paths

    def test_docs_endpoint_exists(self, client):
        """Test that Swagger UI endpoint exists"""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK

    def test_redoc_endpoint_exists(self, client):
        """Test that ReDoc endpoint exists"""
        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK


class TestAppConfiguration:
    """Tests for FastAPI app configuration"""

    def test_app_title(self, client):
        """Test that app has correct title"""
        from main import app

        assert app.title == "FastAPI Boilerplate"

    def test_app_version(self, client):
        """Test that app has correct version"""
        from main import app

        assert app.version == "1.0.0"

    def test_app_tags_defined(self, client):
        """Test that OpenAPI tags are defined"""
        from main import app

        assert app.openapi_tags is not None
        assert len(app.openapi_tags) == 3  # root, health, status

        tag_names = [tag["name"] for tag in app.openapi_tags]
        assert "root" in tag_names
        assert "health" in tag_names
        assert "status" in tag_names


class TestErrorHandling:
    """Tests for error handling"""

    def test_404_for_nonexistent_endpoint(self, client):
        """Test that nonexistent endpoints return 404"""
        response = client.get("/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_method_not_allowed(self, client):
        """Test that POST to GET-only endpoints returns 405"""
        response = client.post("/health")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
