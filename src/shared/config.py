"""Application configuration via Pydantic Settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    APP_NAME: str = "MyProject"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/db"
    REDIS_URL: str = "redis://localhost:6379"
    SENTRY_DSN: str = ""
    SECRET_KEY: str = "change-me-in-production"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
