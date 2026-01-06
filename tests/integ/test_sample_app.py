"""E2E tests validating llms.txt generation against a realistic FastAPI app."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fast_llms_txt import create_llms_txt_router


class TestSampleAppOutput:
    """Tests validating generated output against the sample app fixture."""

    @pytest.fixture
    def client(self, sample_app: FastAPI) -> TestClient:
        """Create a TestClient with the llms.txt router included."""
        sample_app.include_router(create_llms_txt_router(sample_app))
        return TestClient(sample_app)

    @pytest.fixture
    def llms_txt(self, client: TestClient) -> str:
        """Get the generated llms.txt content."""
        response = client.get("/llms.txt")
        assert response.status_code == 200
        return response.text

    def test_api_metadata(self, llms_txt: str):
        """Test that API title and description are present."""
        assert "# Sample API" in llms_txt
        assert "A sample API demonstrating various OpenAPI features" in llms_txt

    def test_all_endpoints_present(self, llms_txt: str):
        """Test that all endpoints from sample app appear in output."""
        endpoints = [
            "GET /users",
            "GET /users/{user_id}",
            "POST /users",
            "PATCH /users/{user_id}",
            "DELETE /users/{user_id}",
            "GET /posts",
            "GET /posts/{post_id}",
            "GET /users/{user_id}/posts",
            "GET /health",
        ]
        for endpoint in endpoints:
            assert endpoint in llms_txt, f"Missing endpoint: {endpoint}"

    def test_tag_grouping(self, llms_txt: str):
        """Test that endpoints are grouped by tags."""
        assert "## Users" in llms_txt
        assert "## Posts" in llms_txt
        assert "## System" in llms_txt

    def test_enum_values_shown(self, llms_txt: str):
        """Test that enum values are displayed."""
        # UserRole enum should show allowed values
        assert "admin" in llms_txt
        assert "user" in llms_txt
        assert "guest" in llms_txt

    def test_query_parameters(self, llms_txt: str):
        """Test that query parameters are documented."""
        # Pagination params from list_users
        assert "page" in llms_txt
        assert "per_page" in llms_txt
        # Filter params
        assert "role" in llms_txt
        assert "search" in llms_txt

    def test_path_parameters(self, llms_txt: str):
        """Test that path parameters are documented."""
        assert "user_id" in llms_txt
        assert "post_id" in llms_txt

    def test_request_body_fields(self, llms_txt: str):
        """Test that request body fields are documented."""
        # UserBase fields from POST /users
        assert "name" in llms_txt
        assert "email" in llms_txt

    def test_nested_model_expansion(self, llms_txt: str):
        """Test that nested models are expanded inline."""
        # Address fields from nested model in UserBase
        assert "street" in llms_txt
        assert "city" in llms_txt
        assert "country" in llms_txt

    def test_response_types(self, llms_txt: str):
        """Test that response types are documented."""
        # PaginatedUsers response
        assert "items" in llms_txt
        assert "total" in llms_txt
        assert "has_next" in llms_txt

    def test_endpoint_descriptions(self, llms_txt: str):
        """Test that endpoint descriptions are present."""
        assert "List users" in llms_txt or "Retrieve a paginated list" in llms_txt
        assert "Create user" in llms_txt or "Create a new user" in llms_txt
        assert "Health check" in llms_txt

    def test_list_response_types(self, llms_txt: str):
        """Test that list/array response types are indicated."""
        # GET /posts returns list[Post]
        assert "Post" in llms_txt
