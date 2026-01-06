"""Shared pytest fixtures for fast-llms-txt tests."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.fixtures.sample_app import create_sample_app


@pytest.fixture
def sample_app() -> FastAPI:
    """Create a fresh sample FastAPI app instance."""
    return create_sample_app()


@pytest.fixture
def sample_client(sample_app: FastAPI) -> TestClient:
    """Create a TestClient for the sample app."""
    return TestClient(sample_app)
