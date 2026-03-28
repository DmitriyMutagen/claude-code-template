# Example Domain

## Ответственность
Управление элементами [описание бизнес-логики].

## Публичный API (contracts.py)
- ExampleServiceProtocol.get_items() → list[ExampleItemDTO]
- ExampleServiceProtocol.create_item(name) → ExampleItemDTO

## Зависимости
- shared/database — DB sessions
- shared/config — Settings

## Кто зависит от нас
- Никто пока (пример)

## Тесты
```bash
pytest src/example_domain/tests/ -v
```
