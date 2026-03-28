"""Pydantic schemas for API input/output validation."""
from pydantic import BaseModel
from datetime import datetime


class ExampleItemDTO(BaseModel):
    """Data Transfer Object for ExampleItem."""

    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class CreateExampleItemRequest(BaseModel):
    """Input for creating an item."""

    name: str
