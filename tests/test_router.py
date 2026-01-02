"""Tests for the router module."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fast_llms_txt import create_llms_txt_router


class TestCreateLlmsTxtRouter:
    """Tests for create_llms_txt_router function."""

    def test_default_path(self):
        """Test that default path is /llms.txt."""
        app = FastAPI(title="Test API")
        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt")

        assert response.status_code == 200

    def test_custom_path(self):
        """Test custom endpoint path."""
        app = FastAPI(title="Test API")
        app.include_router(create_llms_txt_router(app, path="/docs.txt"))

        client = TestClient(app)
        response = client.get("/docs.txt")

        assert response.status_code == 200

    def test_with_prefix(self):
        """Test router with prefix."""
        app = FastAPI(title="Test API")
        app.include_router(create_llms_txt_router(app), prefix="/api/v1/docs")

        client = TestClient(app)
        response = client.get("/api/v1/docs/llms.txt")

        assert response.status_code == 200

    def test_content_type(self):
        """Test that response content type is text/plain."""
        app = FastAPI(title="Test API")
        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt")

        assert "text/plain" in response.headers["content-type"]

    def test_returns_markdown(self):
        """Test that response contains markdown content."""
        app = FastAPI(title="Test API", description="A test API")

        @app.get("/users")
        def list_users():
            """List all users."""
            return []

        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt")

        assert "# Test API" in response.text
        assert "> A test API" in response.text
        assert "GET /users" in response.text

    def test_endpoint_not_in_schema(self):
        """Test that llms.txt endpoint is not included in OpenAPI schema."""
        app = FastAPI(title="Test API")
        app.include_router(create_llms_txt_router(app))

        schema = app.openapi()

        assert "/llms.txt" not in schema.get("paths", {})

    def test_reflects_app_changes(self):
        """Test that generated content reflects current app state."""
        app = FastAPI(title="Test API")
        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)

        # Initially no endpoints
        response1 = client.get("/llms.txt")
        assert "/users" not in response1.text

        # Add an endpoint
        @app.get("/users")
        def list_users():
            return []

        # Clear cached schema
        app.openapi_schema = None

        response2 = client.get("/llms.txt")
        assert "/users" in response2.text

    def test_with_tags(self):
        """Test that tags are properly reflected."""
        app = FastAPI(title="Test API")

        @app.get("/users", tags=["Users"])
        def list_users():
            return []

        @app.get("/posts", tags=["Posts"])
        def list_posts():
            return []

        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt")

        assert "## Users" in response.text
        assert "## Posts" in response.text

    def test_with_parameters(self):
        """Test that parameters are included."""
        app = FastAPI(title="Test API")

        @app.get("/users")
        def list_users(limit: int = 10, offset: int = 0):
            return []

        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt")

        assert "limit" in response.text
        assert "offset" in response.text

    def test_detailed_spec_link(self):
        """Test that detailed spec links are included for each endpoint."""
        app = FastAPI(title="Test API")

        @app.get("/users/{user_id}")
        def get_user(user_id: int):
            return {"id": user_id}

        @app.post("/users")
        def create_user():
            return {}

        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt")

        assert "[Detailed spec](/llms.txt/paths/GET/users/{user_id})" in response.text
        assert "[Detailed spec](/llms.txt/paths/POST/users)" in response.text

    def test_detailed_spec_link_custom_path(self):
        """Test that detailed spec links use the correct custom path."""
        app = FastAPI(title="Test API")

        @app.get("/items")
        def list_items():
            return []

        app.include_router(create_llms_txt_router(app, path="/docs.txt"))

        client = TestClient(app)
        response = client.get("/docs.txt")

        assert "[Detailed spec](/docs.txt/paths/GET/items)" in response.text


class TestOperationEndpoint:
    """Tests for the /llms.txt/paths/{method}/{path} endpoint."""

    def test_operation_endpoint_returns_json(self):
        """Test that valid method+path returns JSON."""
        app = FastAPI(title="Test API")

        @app.get("/users/{user_id}")
        def get_user(user_id: int):
            """Get a user by ID."""
            return {"id": user_id}

        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt/paths/GET/users/{user_id}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert data["method"] == "GET"
        assert data["path"] == "/users/{user_id}"
        assert data["summary"] == "Get User"

    def test_operation_endpoint_path_not_found(self):
        """Test that invalid path returns 404."""
        app = FastAPI(title="Test API")

        @app.get("/users")
        def list_users():
            return []

        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt/paths/GET/nonexistent")

        assert response.status_code == 404

    def test_operation_endpoint_method_not_found(self):
        """Test that valid path but wrong method returns 404."""
        app = FastAPI(title="Test API")

        @app.get("/users")
        def list_users():
            return []

        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt/paths/POST/users")

        assert response.status_code == 404

    def test_operation_endpoint_refs_resolved(self):
        """Test that $refs are fully resolved in the response."""
        from pydantic import BaseModel

        app = FastAPI(title="Test API")

        class User(BaseModel):
            id: int
            name: str

        @app.get("/users/{user_id}", response_model=User)
        def get_user(user_id: int):
            return {"id": user_id, "name": "Test"}

        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt/paths/GET/users/{user_id}")

        assert response.status_code == 200
        data = response.json()

        # Check that no $ref keys exist in the response
        def has_ref(obj):
            if isinstance(obj, dict):
                if "$ref" in obj:
                    return True
                return any(has_ref(v) for v in obj.values())
            if isinstance(obj, list):
                return any(has_ref(item) for item in obj)
            return False

        assert not has_ref(data), "Response should not contain any $ref keys"

    def test_operation_endpoint_nested_refs(self):
        """Test that deeply nested refs are resolved."""
        from pydantic import BaseModel

        app = FastAPI(title="Test API")

        class Address(BaseModel):
            street: str
            city: str

        class User(BaseModel):
            id: int
            address: Address

        @app.post("/users", response_model=User)
        def create_user(user: User):
            return user

        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)
        response = client.get("/llms.txt/paths/POST/users")

        assert response.status_code == 200
        data = response.json()

        # Verify the nested Address schema is resolved
        request_body = data.get("requestBody", {})
        content = request_body.get("content", {}).get("application/json", {})
        schema = content.get("schema", {})
        properties = schema.get("properties", {})

        # Address should be fully resolved with its properties
        address_prop = properties.get("address", {})
        assert "properties" in address_prop, "Nested Address schema should be resolved"
        assert "street" in address_prop["properties"]
        assert "city" in address_prop["properties"]

    def test_operation_endpoint_case_insensitive_method(self):
        """Test that method matching is case insensitive."""
        app = FastAPI(title="Test API")

        @app.get("/users")
        def list_users():
            return []

        app.include_router(create_llms_txt_router(app))

        client = TestClient(app)

        # Test lowercase
        response = client.get("/llms.txt/paths/get/users")
        assert response.status_code == 200

        # Test uppercase
        response = client.get("/llms.txt/paths/GET/users")
        assert response.status_code == 200
