# Example Domain

## Ответственность
Управление элементами [описание бизнес-логики].

## Публичный API (gateway.py)
- ExampleGateway.get_items() → list[ExampleItemDTO]
- ExampleGateway.create_item(name) → ExampleItemDTO

## Events (events.py)
- ExampleItemCreated — событие при создании элемента

## Зависимости
- shared/database — DB sessions
- shared/config — Settings

## Кто зависит от нас
- Никто пока (пример)

## Файлы (Vertical Slice)
- `gateway.py` — публичный интерфейс (Gateway pattern)
- `events.py` — domain events для async коммуникации
- `contracts.py` — Protocol (альтернатива Gateway, для strict DI)
- `models.py` — SQLAlchemy ORM (PRIVATE, не импортировать снаружи)
- `schemas.py` — Pydantic DTOs
- `service.py` — бизнес-логика (PRIVATE)
- `router.py` — FastAPI endpoints

## Тесты
```bash
pytest src/example_domain/tests/ -v
```
