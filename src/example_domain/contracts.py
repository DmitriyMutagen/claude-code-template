"""Public contracts (Protocol) for this domain.

Other domains MUST import ONLY from this file, never from internal modules.
"""
from typing import Protocol

from src.example_domain.schemas import ExampleItemDTO


class ExampleServiceProtocol(Protocol):
    """Public interface of the Example domain."""

    async def get_items(self) -> list[ExampleItemDTO]: ...
    async def create_item(self, name: str) -> ExampleItemDTO: ...
