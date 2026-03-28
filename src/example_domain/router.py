"""FastAPI router for this domain."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.database import get_session
from src.example_domain.service import ExampleService
from src.example_domain.schemas import ExampleItemDTO, CreateExampleItemRequest

router = APIRouter(prefix="/example", tags=["example"])


@router.get(
    "/",
    response_model=list[ExampleItemDTO],
    summary="List all items",
    description="Получить список всех элементов домена.",
)
async def list_items(session: AsyncSession = Depends(get_session)):
    """Список всех элементов."""
    service = ExampleService(session)
    return await service.get_items()


@router.post(
    "/",
    response_model=ExampleItemDTO,
    summary="Create item",
    description="Создать новый элемент.",
)
async def create_item(
    request: CreateExampleItemRequest,
    session: AsyncSession = Depends(get_session),
):
    """Создать элемент."""
    service = ExampleService(session)
    return await service.create_item(request.name)
