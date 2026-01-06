"""Sample FastAPI app for testing llms.txt generation."""

from enum import Enum
from typing import Annotated

from fastapi import FastAPI, Query, Path, Body, Header
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class Address(BaseModel):
    """User address model."""
    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City name")
    country: str = Field(default="USA", description="Country code")
    postal_code: str | None = Field(None, description="Postal/ZIP code")


class UserBase(BaseModel):
    """Base user model for creation."""
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: str = Field(..., description="User's email address")
    role: UserRole = Field(default=UserRole.USER, description="User's role")
    tags: list[str] = Field(default_factory=list, description="User tags for categorization")
    address: Address | None = Field(None, description="User's address")


class User(UserBase):
    """User model with ID."""
    id: str = Field(..., description="Unique user identifier")
    created_at: str = Field(..., description="ISO timestamp of creation")


class UserUpdate(BaseModel):
    """Model for partial user updates."""
    name: str | None = Field(None, description="User's full name")
    email: str | None = Field(None, description="User's email address")
    role: UserRole | None = Field(None, description="User's role")


class PaginatedUsers(BaseModel):
    """Paginated list of users."""
    items: list[User] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether more pages exist")


class Post(BaseModel):
    """Blog post model."""
    id: str = Field(..., description="Unique post identifier")
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content in markdown")
    author_id: str = Field(..., description="ID of the post author")
    published: bool = Field(default=False, description="Publication status")


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict | None = Field(None, description="Additional error details")


def create_sample_app() -> FastAPI:
    """Create and configure the sample FastAPI application."""
    app = FastAPI(
        title="Sample API",
        description="A sample API demonstrating various OpenAPI features.\n\nThis API includes:\n- User management\n- Blog posts\n- Authentication",
        version="1.0.0",
    )

    # Users endpoints
    @app.get(
        "/users",
        tags=["Users"],
        summary="List users",
        description="Retrieve a paginated list of all users. Supports filtering by role and searching by name.",
        response_model=PaginatedUsers,
        responses={
            401: {"model": ErrorResponse, "description": "Unauthorized"},
        },
    )
    def list_users(
        page: Annotated[int, Query(ge=1, description="Page number")] = 1,
        per_page: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
        role: Annotated[UserRole | None, Query(description="Filter by user role")] = None,
        search: Annotated[str | None, Query(description="Search by name (partial match)")] = None,
        x_api_key: Annotated[str, Header(description="API key for authentication")] = "",
    ) -> PaginatedUsers:
        return PaginatedUsers(items=[], total=0, page=page, per_page=per_page, has_next=False)

    @app.get(
        "/users/{user_id}",
        tags=["Users"],
        summary="Get user",
        description="Retrieve a specific user by their ID.",
        response_model=User,
        responses={
            404: {"model": ErrorResponse, "description": "User not found"},
        },
    )
    def get_user(
        user_id: Annotated[str, Path(description="The unique user identifier")],
    ) -> User:
        return User(
            id=user_id,
            name="Test",
            email="test@example.com",
            role=UserRole.USER,
            created_at="2024-01-01T00:00:00Z",
        )

    @app.post(
        "/users",
        tags=["Users"],
        summary="Create user",
        description="Create a new user account.",
        response_model=User,
        status_code=201,
        responses={
            400: {"model": ErrorResponse, "description": "Invalid input"},
            409: {"model": ErrorResponse, "description": "Email already exists"},
        },
    )
    def create_user(
        user: Annotated[UserBase, Body(description="User data to create")],
    ) -> User:
        return User(
            id="new-id",
            **user.model_dump(),
            created_at="2024-01-01T00:00:00Z",
        )

    @app.patch(
        "/users/{user_id}",
        tags=["Users"],
        summary="Update user",
        description="Partially update an existing user. Only provided fields will be updated.",
        response_model=User,
        responses={
            404: {"model": ErrorResponse, "description": "User not found"},
        },
    )
    def update_user(
        user_id: Annotated[str, Path(description="The unique user identifier")],
        user: Annotated[UserUpdate, Body(description="Fields to update")],
    ) -> User:
        return User(
            id=user_id,
            name=user.name or "Test",
            email=user.email or "test@example.com",
            role=user.role or UserRole.USER,
            created_at="2024-01-01T00:00:00Z",
        )

    @app.delete(
        "/users/{user_id}",
        tags=["Users"],
        summary="Delete user",
        description="Permanently delete a user account.",
        status_code=204,
        responses={
            404: {"model": ErrorResponse, "description": "User not found"},
        },
    )
    def delete_user(
        user_id: Annotated[str, Path(description="The unique user identifier")],
    ) -> None:
        pass

    # Posts endpoints
    @app.get(
        "/posts",
        tags=["Posts"],
        summary="List posts",
        description="Retrieve all blog posts.",
        response_model=list[Post],
    )
    def list_posts(
        published_only: Annotated[bool, Query(description="Only return published posts")] = False,
    ) -> list[Post]:
        return []

    @app.get(
        "/posts/{post_id}",
        tags=["Posts"],
        summary="Get post",
        response_model=Post,
    )
    def get_post(
        post_id: Annotated[str, Path(description="The post ID")],
    ) -> Post:
        return Post(
            id=post_id,
            title="Test",
            content="Content",
            author_id="author-1",
        )

    @app.get(
        "/users/{user_id}/posts",
        tags=["Posts"],
        summary="Get user's posts",
        description="Retrieve all posts authored by a specific user.",
        response_model=list[Post],
    )
    def get_user_posts(
        user_id: Annotated[str, Path(description="The user ID")],
    ) -> list[Post]:
        return []

    # System endpoints
    @app.get(
        "/health",
        tags=["System"],
        summary="Health check",
        description="Check if the API is running.",
    )
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


# Convenience: create a default instance
sample_app = create_sample_app()
