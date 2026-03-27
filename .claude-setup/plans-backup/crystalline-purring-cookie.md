# MarketAI — Масштабный план улучшений v2.0

## Context

3 параллельных агента провели полный аудит проекта:
- **Backend**: 202 endpoints, 43 модели, 1734 строки тестов, 4 TODO, критические дыры в WB-связке
- **MCP серверы**: 27 серверов обнаружено (science-api, ozon-api, wb-api, ym-api, marketai-db + 22 других)
- **Frontend**: 22 страницы 100% готовы, но нет ErrorBoundary, нет code splitting, 27x `any` типов

Цель: устранить все баги, ускорить сервис, интегрировать MCP-серверы в AI-движок, запустить новые фичи — параллельно, командой агентов.

---

## Критические баги (найденные аудитом)

### Frontend
1. **Нет global ErrorBoundary** — одна ошибка убивает весь app
2. **Хардкод "DM" вместо инициалов пользователя** — Layout.tsx:317, 539
3. **Нет code splitting** — все 22 страницы грузятся сразу (медленный FCP)
4. **27x `any` типов** — AuthContext, Analytics, Admin, Services

### Backend
5. **WB product_id не линкуется** — 69K отзывов без привязки к товарам (0% cross-sell для WB)
6. **activity_logger не вызывается** — инфраструктура готова, но вызовы не добавлены в роутеры
7. **Dashboard TODO** — счётчик responses per marketplace не реализован

### MCP Серверы
8. **science-api: баг operator precedence** в pubmed.py:29 — proxy transport всегда применяется (неправильная логика)
9. **science-api: глобальный SUPPLEMENT_DB state** — перезагружается при двойном вызове register()
10. **ozon-api: OAuth2 токены в plain memory** — нет шифрования (нормально для dev, риск для prod)

---

## Стратегия: 4 параллельных спринта

### Sprint A — Критические баги (немедленно)
### Sprint B — Производительность (параллельно с A)
### Sprint C — Интеграция MCP серверов в AI-движок
### Sprint D — Новые фичи (на инфраструктуре из A+B+C)

---

## Sprint A: Критические баги

### A1. Frontend: ErrorBoundary + Code Splitting + Types
**Агент**: `frontend-engineer`
**Файлы**:
- `frontend-react/src/App.tsx` — добавить `<ErrorBoundary>` wrapper
- `frontend-react/src/components/ErrorBoundary.tsx` — создать компонент
- `frontend-react/src/App.tsx` — `React.lazy()` + `Suspense` для всех 22 страниц
- `frontend-react/src/components/Layout.tsx:317,539` — заменить "DM" на `user.full_name?.substring(0,2).toUpperCase()`
- `frontend-react/src/api/services.ts` — заменить `any` на типизированные интерфейсы

**Цель**: 0 `any` + ErrorBoundary + lazy loading = стабильное, быстрое frontend

### A2. Backend: WB product_id linking
**Агент**: `python-developer`
**Файлы**:
- `src/connectors/wb/sync.py` — добавить поиск `product_id` по `sku` при синке отзывов
- `src/api/routers/sync.py` — endpoint для backfill существующих 69K отзывов
- `tests/test_wb_product_linking.py` — тест

**Цель**: WB отзывы должны иметь `product_id` → cross-sell начнёт работать для WB

### A3. Backend: Activity logging wiring
**Агент**: `python-developer`
**Файлы**:
- `src/api/routers/auth_router.py` — `log_activity("login")`, `log_activity("register")`
- `src/api/routers/sync.py` — `log_activity("sync_started")`, `log_activity("sync_completed")`
- `src/api/routers/reviews.py` — `log_activity("response_sent")`
- `src/services/excel_export.py` — `log_activity("export")`
- `src/api/routers/subscriptions.py` — `log_activity("plan_upgraded")`

**Цель**: Полный audit trail действий пользователей

### A4. MCP: science-api bug fix
**Агент**: `python-developer`
**Файл**: `/Users/Dmitrij/Documents/mcp servers/servers/science-api/src/science_api/clients/pubmed.py:29`
```python
# БЫЛО (баг оператора):
transport = ... if proxy and "socks" in proxy.lower() or (proxy and "http" in proxy.lower()) else None
# СТАЛО (правильно):
transport = ... if (proxy and ("socks" in proxy.lower() or "http" in proxy.lower())) else None
```
Также: перевести `SUPPLEMENT_DB` в lazy init в `nutrition.py:20-32`

---

## Sprint B: Производительность

### B1. Frontend: useMemo/useCallback + React.memo
**Агент**: `frontend-engineer`
**Файлы**: Analytics.tsx, Chats.tsx, Reviews.tsx (самые тяжёлые страницы)
- Обернуть дорогие вычисления в `useMemo`
- Обернуть callback-handlers в `useCallback`
- `React.memo` для list item компонентов

### B2. Backend: Materialized view для dashboard
**Агент**: `python-developer`
**Цель**: Ускорить Dashboard на 10x при >100K отзывов
```sql
CREATE MATERIALIZED VIEW mv_shop_daily_stats AS
SELECT shop_id, marketplace, DATE_TRUNC('day', review_date)::date AS day,
       COUNT(*) AS total_reviews, ROUND(AVG(rating)::numeric,2) AS avg_rating,
       COUNT(*) FILTER (WHERE status='responded') AS responded_count
FROM reviews GROUP BY 1,2,3;
CREATE UNIQUE INDEX ON mv_shop_daily_stats (shop_id, marketplace, day);
```
- Новая миграция `013_materialized_views.py`
- Cron refresh через ARQ каждые 5 минут
- Обновить `src/api/routers/dashboard.py` — использовать MV вместо raw queries

### B3. Backend: Параллельный sync
**Агент**: `python-developer`
**Файл**: `src/services/sync_engine.py`
- Сейчас: последовательные UPSERT батчи по 500 строк
- Стать: `asyncio.gather()` для параллельного синка по разным marketplace
- Ожидаемый прирост: 3x быстрее при синке нескольких магазинов

### B4. Backend: Tests для sync workflow
**Агент**: `tester`
**Создать**: `tests/test_sync_workflow.py`
- Тест end-to-end синка Ozon отзывов
- Тест product_id linkage (WB)
- Тест circuit breaker поведения
- Тест idempotency (повторный sync не дублирует данные)

---

## Sprint C: MCP → AI-движок интеграция

### C1. Science-API в AI engine (самое ценное)
**Агент**: `ai-engineer`
**Концепция**: При генерации ответа на отзыв — вызываем science-api для получения PubMed цитат

**Новый модуль**: `src/ai/science_enrichment.py`
```python
async def get_scientific_context(ingredients: list[str]) -> dict:
    """Query science-api MCP tools for ingredient research."""
    # Через subprocess MCP call или HTTP bridge
    ...
```

**Архитектура**: Либо через stdio-вызов MCP, либо через FastAPI proxy endpoint
- Предпочтительно: HTTP bridge `src/services/science_bridge.py` — FastAPI sub-app на порту 8001
- Вызывает science-api MCP tools через subprocess
- Кэш в Redis (24h TTL, key=f"science:{ingredient}:{focus}")

**Интеграция в engine.py**:
- Шаг 3 (PubMed search) → заменить прямой BioPython вызов на science_bridge.get_pubmed()
- Добавить safety_check через `openfda_search` (OpenFDA adverse events)
- Добавить DSLD поиск (NIH supplement labels)

### C2. marketai-db → Admin Dashboard
**Агент**: `python-developer`
**Цель**: Admin monitoring page использует marketai-db MCP инструменты напрямую

**Новый endpoint**: `GET /admin/mcp-stats`
- Вызывает marketai_review_stats, marketai_sync_freshness, marketai_shop_comparison
- Возвращает агрегат для AdminMonitoring.tsx

### C3. ozon-api + wb-api → product sync fix
**Агент**: `python-developer`
**Цель**: При sync отзывов — использовать ozon-api MCP для получения product_id по external_id

Сейчас в `src/connectors/ozon/` делается прямой API вызов.
Опционально: перевести на ozon-api MCP server (унификация, circuit breaker из shared lib).

**Решение**: Создать `src/services/mcp_bridge.py` — синхронный HTTP proxy для MCP tools

---

## Sprint D: Новые фичи

### D1. Mailings Frontend
**Агент**: `frontend-engineer`
Backend `mailings_service.py` уже готов. Frontend `Mailings.tsx` существует (845 LOC).
**Нужно**: Проверить интеграцию с backend, добавить missing API calls, протестировать.

### D2. Telegram Bot активация
**Агент**: `python-developer`
Backend `telegram_bot.py` (614 LOC) уже написан.
**Нужно**:
- Добавить endpoint `POST /webhooks/telegram` в main.py
- Настроить polling vs webhook режим
- Интегрировать с activity_logger
- Уведомления о новых отзывах → Telegram

### D3. AI-категоризация отзывов
**Агент**: `ai-engineer`
**Концепция**: Автоматически тегировать отзывы при AI-генерации ответа
- Новое поле `Review.tags: list[str]` — миграция 014
- Prompt для AI: "Выведи теги из отзыва: качество, цена, доставка, состав, побочные эффекты, ..."
- Frontend фильтр по тегам в Reviews.tsx
- Dashboard: топ-10 тегов за период

### D4. Шаблоны ответов (200+ для BAД-ниши)
**Агент**: `ai-engineer` + `python-developer`
**Архитектура**:
- Новая таблица `ResponseTemplate` (category, rating_min, rating_max, tone, text, uses_count)
- Миграция 015
- Endpoint `GET /templates?rating=1&marketplace=ozon` → список шаблонов
- Frontend: выбор шаблона в Reviews перед отправкой
- Предзаполнить 50 шаблонов для старта (BAД/витамины/протеин тематика)

---

## Новые MCP серверы (рекомендации)

### MCP-1: `notification-service` (WebSocket push)
**Проблема**: Сейчас frontend поллит каждые 30-60 секунд. Неэффективно.
**Решение**: WebSocket MCP server → push уведомления о новых отзывах/чатах в реальном времени
**Стек**: FastMCP + WebSockets + Redis pub/sub

### MCP-2: `template-library` (управление шаблонами)
**Цель**: Библиотека ответов для BAД-ниши, поиск по тематике, рейтингу, тональности
**Tools**: `template_search`, `template_create`, `template_vote`, `template_get_top`

### MCP-3: `chrome-extension-sync` (Chrome Extension backend)
**Цель**: API для Chrome Extension, которое будет парсить отзывы прямо с WB/Ozon страниц
**Tools**: `extension_submit_review`, `extension_get_draft_response`, `extension_send_response`

---

## Команда агентов

```
┌─────────────────────────────────────────────────────────────┐
│                    SHOWRUNNER (оркестратор)                  │
└──┬────────────┬──────────────┬──────────────┬───────────────┘
   │            │              │              │
   ▼            ▼              ▼              ▼
frontend-  python-      ai-engineer      tester
engineer   developer
   │            │              │              │
   A1,B1,D1    A2,A3,B2,     C1,D3,D4      B4 +
   D2 frontend  B3,C2,C3,     AI features   QA-testing
               D2 backend
```

**Параллельные запуски**:
- **Batch 1** (немедленно): A1 + A2 + A3 + A4 (все независимы)
- **Batch 2** (после Batch 1): B1 + B2 + B3 + C1 (performance + MCP integration)
- **Batch 3** (после Batch 2): D1 + D2 + D3 + D4 (новые фичи)
- **MCP servers** (параллельно с Batch 2): notification-service + template-library

---

## Файлы требующие изменений

### Backend (src/)
- `src/api/main.py` — webhook endpoint для Telegram
- `src/api/routers/auth_router.py` — activity logging
- `src/api/routers/sync.py` — activity logging + parallel batches
- `src/api/routers/reviews.py` — activity logging + tag filter
- `src/api/routers/dashboard.py` — materialized view usage
- `src/api/routers/admin.py` — mcp-stats endpoint
- `src/api/models.py` — Review.tags field, ResponseTemplate model
- `src/ai/engine.py` — science_enrichment integration
- `src/ai/science_enrichment.py` — НОВЫЙ: science-api bridge
- `src/services/mcp_bridge.py` — НОВЫЙ: MCP HTTP proxy
- `src/connectors/wb/sync.py` — product_id linking fix
- `src/services/activity_logger.py` — wire up calls

### Frontend (frontend-react/src/)
- `src/App.tsx` — ErrorBoundary + React.lazy
- `src/components/ErrorBoundary.tsx` — НОВЫЙ компонент
- `src/components/Layout.tsx` — fix avatar initials
- `src/pages/Analytics.tsx`, `Chats.tsx`, `Reviews.tsx` — useMemo/useCallback
- `src/api/services.ts` — replace `any` types

### Alembic migrations
- `013_materialized_views.py` — mv_shop_daily_stats
- `014_review_tags.py` — Review.tags jsonb field
- `015_response_templates.py` — ResponseTemplate table

### MCP servers
- `/mcp servers/servers/science-api/src/science_api/clients/pubmed.py:29` — proxy bug fix
- `/mcp servers/servers/science-api/src/science_api/tools/nutrition.py:20-32` — lazy init

---

## Верификация

```bash
# После Sprint A:
cd marketai/marketai
pytest tests/ -v -k "not test_ozon_chat" --tb=short
# Ожидаем: 388+ passed (больше из-за новых тестов), 0 failed

# Frontend build:
cd frontend-react && npm run build
# Ожидаем: 0 TS errors, bundle < 2MB initial

# WB product linking:
/opt/homebrew/opt/postgresql@16/bin/psql -U marketai -d marketai \
  -c "SELECT COUNT(*) FROM reviews WHERE marketplace='wb' AND product_id IS NOT NULL;"
# Ожидаем: >0 (было 0)

# Science-api:
cd /Users/Dmitrij/Documents/mcp\ servers/servers/science-api
python -c "from science_api.clients.pubmed import PubMedClient; print('OK')"
# Ожидаем: OK без ошибок

# MCP integration:
docker-compose up -d && uvicorn src.api.main:app --port 8000
curl http://localhost:8000/health
# Ожидаем: {"status":"ok","db":"connected","redis":"connected"}
```

---

## Ожидаемые результаты

| Метрика | До | После |
|---------|-----|-------|
| WB cross-sell охват | 0% (69K отзывов) | >90% |
| Dashboard load time | ~800ms | ~100ms (materialized view) |
| Frontend initial bundle | ~5MB | ~1.5MB (code splitting) |
| Activity audit trail | 0% действий | 100% ключевых действий |
| Science citations в ответах | Только PubMed | PubMed + OpenFDA + DSLD + ODS |
| Crash resilience | Одна ошибка = белый экран | ErrorBoundary показывает UI |
| WS polling overhead | 30-60s intervals | WebSocket push (0 overhead) |

---

## Порядок выполнения

1. **Создать branch**: `feature/v2-improvements`
2. **Batch 1** — 4 агента параллельно: `showrunner` → A1, A2, A3, A4
3. **Batch 2** — 4 агента параллельно: B1, B2, B3, C1
4. **Batch 3** — 4 агента параллельно: D1, D2, D3, D4
5. **QA** — `tester` + `qa-tester` финальный прогон
6. `/checkpoint` — сохранить прогресс
