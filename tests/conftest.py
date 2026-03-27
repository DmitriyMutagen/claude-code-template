"""
Elite Test Configuration — conftest.py
Shared fixtures for unit, integration, E2E, and AI quality tests.

Usage:
  pytest tests/ -v                    # all tests
  pytest tests/ -m unit               # only unit
  pytest tests/ -m "not slow"         # skip slow
  pytest tests/ -n auto               # parallel
  pytest tests/ --cov=src/            # with coverage
"""

import os

import pytest
from httpx import ASGITransport, AsyncClient

# ═══ Environment ═══
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test_db")
os.environ.setdefault("DATABASE_URL_SYNC", "postgresql+psycopg2://test:test@localhost:5432/test_db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-do-not-use-in-prod")
os.environ.setdefault("SENTRY_DSN", "")


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Async HTTP client for API integration tests."""
    from src.api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ═══ Markers (register in pyproject.toml) ═══
# @pytest.mark.unit        — pure logic, no I/O, <0.1s
# @pytest.mark.integration — needs DB/Redis, <1s
# @pytest.mark.e2e         — browser tests (Playwright), <30s
# @pytest.mark.ai          — LLM quality tests (slow, costs $)
# @pytest.mark.slow        — any test > 10 seconds
