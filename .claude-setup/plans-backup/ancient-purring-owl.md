# MarketAI — Полный цикл: Ozon API → AI → Публикация

## Контекст

MarketAI — система автоответов на отзывы Ozon. Пайплайн `scripts/pipeline.py` уже создан и протестирован (100 отзывов AI-сгенерированы, экспорт в Sheets работает).

**Новая задача**: полный автоцикл без ручного одобрения:
1. Забрать **неотвеченные** отзывы напрямую из Ozon API (`status=UNPROCESSED`)
2. Сгенерировать AI-ответы
3. Опубликовать ответы обратно на Ozon через `/v1/review/comment/create`

## Готовые компоненты (уже работают)

| Компонент | Описание |
|-----------|----------|
| `scripts/pipeline.py` | AI-генерация + экспорт в Sheets (протестирован, 100+ ответов) |
| `src/connectors/ozon/client.py` | `get_reviews(status="UNPROCESSED")` — неотвеченные с Ozon |
| `src/connectors/ozon/client.py:post_review_comment()` | POST `/v1/review/comment/create` — публикация ответа |
| `src/connectors/ozon/connector.py:send_response()` | Обёртка над post_review_comment |
| `src/tasks/sender.py:send_approved_task()` | Существующий sender (требует is_approved=True) |

## Что делать

### Добавить в `scripts/pipeline.py` флаг `--publish`

Модифицировать `main()` и добавить функцию `publish_to_ozon()`:

```python
# Новый аргумент:
parser.add_argument("--publish", action="store_true",
    help="Fetch from Ozon API (UNPROCESSED) and auto-publish AI responses back")

# Новая функция:
async def publish_to_ozon():
    """
    Полный автоцикл:
    1. client.get_reviews(status="UNPROCESSED") → неотвеченные с Ozon API
    2. Sync to PostgreSQL (upsert)
    3. AI generate for each
    4. client.post_review_comment(external_review_id, ai_draft)
    5. Update review.status = SENT, response.is_sent = True, response.sent_at = now
    """
```

**Реализация:**

```python
async def publish_to_ozon(limit: int, batch_size: int):
    # 1. Получить credentials из БД (Shop)
    async with async_session_factory() as session:
        shop = await session.execute(select(Shop))
        shop = shop.scalars().first()

    # 2. Инициализировать Ozon клиент
    from src.connectors.ozon.client import OzonHTTPClient
    async with OzonHTTPClient(shop.client_id, shop.api_key) as client:

        # 3. Забрать неотвеченные отзывы с Ozon API
        reviews_data = await client.get_all_reviews(status="UNPROCESSED", limit=limit)

        # 4. Upsert в PostgreSQL (обновить/создать записи)
        # ...через existing sync logic...

        # 5. AI генерация (переиспользуем generate_single + save_response)
        engine = AIEngine()
        for batch in batches:
            results = await asyncio.gather(*[generate_single(engine, rd) for rd in batch])
            for res in results:
                await save_response(res["review_id"], res["result"])

        # 6. Публикация на Ozon
        async with async_session_factory() as session:
            responses = await session.execute(
                select(Response).join(Review)
                .where(Response.is_sent == False, Response.ai_draft != None)
            )
            for response in responses.scalars():
                review = await session.get(Review, response.review_id)
                ok = await client.post_review_comment(
                    review_id=review.external_review_id,
                    text=response.ai_draft
                )
                if ok:
                    response.is_sent = True
                    response.sent_at = datetime.now(timezone.utc)
                    review.status = ReviewStatus.SENT
            await session.commit()
```

### CLI использование

```bash
# Взять неотвеченные с Ozon, сгенерировать и опубликовать:
./venv/bin/python scripts/pipeline.py --publish --limit=20

# Только сгенерировать без публикации (как раньше):
./venv/bin/python scripts/pipeline.py --limit=100 --export
```

---

## Ключевые файлы

| Файл | Действие |
|------|----------|
| `marketai/scripts/pipeline.py` | **Изменить** — добавить `--publish` и `publish_to_ozon()` |
| `marketai/src/connectors/ozon/client.py` | Переиспользовать `get_reviews(status="UNPROCESSED")` и `post_review_comment()` |
| `marketai/src/api/models.py` | Без изменений (Review.external_review_id, Response.is_sent) |

## Верификация

1. `./venv/bin/python scripts/pipeline.py --publish --limit=3 --dry-run` → показывает 3 неотвеченных с Ozon
2. `./venv/bin/python scripts/pipeline.py --publish --limit=3` → 3 ответа опубликованы на Ozon
3. Зайти на Ozon Seller → отзывы → убедиться что ответы появились
4. `psql -c "SELECT status FROM reviews WHERE status='sent' LIMIT 5"` → SENT
