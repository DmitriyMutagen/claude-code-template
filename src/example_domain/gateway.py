"""Gateway — публичный интерфейс домена для других модулей.

Другие модули вызывают ТОЛЬКО gateway, никогда service/repository напрямую.
Pattern: Netflix Dispatch (gateway.py per module).
"""
from sqlalchemy.ext.asyncio import AsyncSession

from src.example_domain.service import ExampleService
from src.example_domain.schemas import ExampleItemDTO


class ExampleGateway:
    """Public API of the Example domain.

    Usage from other modules:
        gateway = ExampleGateway(session)
        items = await gateway.get_items()
    """

    def __init__(self, session: AsyncSession):
        self._service = ExampleService(session)

    async def get_items(self) -> list[ExampleItemDTO]:
        """Получить все элементы."""
        return await self._service.get_items()

    async def create_item(self, name: str) -> ExampleItemDTO:
        """Создать новый элемент."""
        return await self._service.create_item(name)
