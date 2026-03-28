"""Domain events — асинхронная коммуникация между модулями.

Другие модули подписываются на события через listeners.
Уменьшает coupling между доменами.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ExampleItemCreated:
    """Событие: новый элемент создан.

    Другие модули могут реагировать на это событие
    через listeners (src/{other_domain}/listeners.py).
    """

    item_id: int
    name: str
    created_at: datetime
