"""E2E test example using Playwright.

Run with: playwright install && pytest tests/e2e/ -v
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:8000"


def test_homepage_loads(page: Page, base_url: str):
    """Verify homepage loads and contains expected content."""
    page.goto(base_url)
    expect(page).to_have_title(/.+/)


def test_health_endpoint_accessible(page: Page, base_url: str):
    """Verify /health endpoint is reachable from browser."""
    response = page.goto(f"{base_url}/health")
    assert response is not None
    assert response.status == 200
