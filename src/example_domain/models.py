"""SQLAlchemy models for this domain ONLY."""
from sqlalchemy import Column, Integer, String, DateTime, func

from src.shared.database import Base


class ExampleItem(Base):
    """Example domain entity."""

    __tablename__ = "example_items"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
