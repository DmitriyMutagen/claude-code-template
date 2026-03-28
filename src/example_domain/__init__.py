"""Example Domain — replace with your business domain.

Public API: use ONLY gateway, events, schemas, and router.
NEVER import models, service, or repository from outside this module.
"""
from src.example_domain.gateway import ExampleGateway
from src.example_domain.events import ExampleItemCreated
from src.example_domain.schemas import ExampleItemDTO
from src.example_domain.router import router

__all__ = [
    "ExampleGateway",      # Sync communication
    "ExampleItemCreated",  # Async events
    "ExampleItemDTO",      # Data transfer
    "router",              # HTTP endpoints
]
