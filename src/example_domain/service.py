"""Business logic for this domain. Internal — use contracts.py externally."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.example_domain.models import ExampleItem
from src.example_domain.schemas import ExampleItemDTO


class ExampleService:
    """Implementation of ExampleServiceProtocol."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_items(self) -> list[ExampleItemDTO]:
        """Получить все элементы."""
        result = await self.session.execute(select(ExampleItem))
        items = result.scalars().all()
        return [ExampleItemDTO.from_orm(item) for item in items]

    async def create_item(self, name: str) -> ExampleItemDTO:
        """Создать новый элемент."""
        item = ExampleItem(name=name)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return ExampleItemDTO.from_orm(item)
