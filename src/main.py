"""Application factory — connects all domain routers."""
import os
import sentry_sdk
from fastapi import FastAPI

from src.shared.config import settings

# Sentry SDK — ОБЯЗАТЕЛЬНО в каждом entry point
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
    )


def create_app() -> FastAPI:
    """Create FastAPI application with all domain routers."""
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
    )

    # Import and include domain routers
    from src.example_domain.router import router as example_router
    app.include_router(example_router, prefix="/api/v1")

    @app.get("/health", summary="Health check")
    async def health():
        """Health endpoint — ОБЯЗАТЕЛЬНО в каждом сервисе."""
        return {"status": "ok", "environment": settings.ENVIRONMENT}

    return app


app = create_app()
