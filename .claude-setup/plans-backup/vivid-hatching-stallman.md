# Plan: MarketAI Production Sprint (updated 2026-03-25)

## Context

MarketAI — SaaS для автоответов на отзывы маркетплейсов (Ozon, WB, YM).
**Статус**: LLM переключен на Polza.ai (DeepSeek V3.2), работает. Нужен финальный спринт до продакшена.

### Что СДЕЛАНО (не делать повторно)
- ✅ Polza.ai интеграция в engine.py (2-3 сек, ~0.006 руб/ответ)
- ✅ Per-rating auto mode (auto_reply_service.py — полностью работает)
- ✅ Scientific RAG 8 источников (scientific_rag.py)
- ✅ OTVETO полный реверс-инжиниринг (257 GraphQL ops, 47 fragments)
- ✅ StoreSettings модель — все поля уже есть
- ✅ Массовое тестирование 20 кейсов (19/20 passed)

### Что НЕ СДЕЛАНО (текущий спринт)

## Sprint Tasks (приоритет: P0 → P1 → P2)

### P0 — Быстрые фиксы (15 мин, запускать первыми)

#### Fix 1: ODS Factsheets URL (5 мин)
- Файл: `src/ai/ods_factsheets.py` строка 129
- Проблема: `https://ods.od.nih.gov/api/factsheet/{slug}.xml` → 301/404
- Фикс: изменить на `https://ods.od.nih.gov/factsheets/{slug}/` + парсить HTML вместо XML
  ИЛИ добавить `follow_redirects=True` к httpx клиенту

#### Fix 2: engine.py missing RAG flags (5 мин)
- Файл: `src/ai/engine.py` строки 438-455, ~1361, ~1567
- Проблема: `build_scientific_context()` вызывается без `enable_nccih` и `enable_openalex`
- Фикс: добавить два параметра в каждый из 3 вызовов:
  ```python
  enable_nccih=_prc.get("enable_nccih", True),
  enable_openalex=_prc.get("enable_openalex", True),
  ```

#### Fix 3: USDA API key (5 мин)
- Файл: `.env` строка 98
- Проблема: `USDA_API_KEY=DEMO_KEY` — rate limit быстро
- Фикс: получить ключ на https://api.nal.usda.gov/support/signup (бесплатно)

### P0 — Верификация чатов (30 мин)
- Проверить end-to-end: покупатель пишет чат → AI генерирует ответ → отправляется
- Тест через `mcp__marketplace-api__ozon_chats_list` и `mcp__marketplace-api__ozon_chat_history`
- Убедиться что `available_products` передаётся в чат-пайплайн (bug был раньше)
- Файл: `src/ai/engine.py` метод `generate_chat_response` (~строка 1300)

### P0 — SEO в ответах (30 мин)
- Добавить SEO-блок в промпты для маркетплейс-поиска
- Файл: `src/ai/prompts.py`
- Логика: брать 2-3 ключевых слова из `product.attributes` или названия товара
- Вставлять органично в конец ответа (не спамом)
- Пример: "Наш [название товара] — отличный выбор для [use_case]"

### P0 — CTA оптимизация (30 мин)
- Текущий CTA дублировался (баг пофикшен ранее)
- Проверить что CTA разный для Ozon/WB/YM
- Добавить CTA про чат с нутрициологом/тренером для консультации
- Файл: `src/ai/prompts.py` секция CTA

### P1 — UnifiedGenerator (опционально, 2-3 часа)
- Файл: `src/ai/unified_generator.py` (NEW, ~250 строк)
- Коллапсировать 3 пайплайна (review/chat/question) в один метод
- Входная точка: `generate(request: GenerationRequest) -> GenerationResponse`
- Полностью переиспользовать: scientific_rag.py, cross_sell.py, guardrails.py, connectors/
- **НЕ делать если нет времени** — текущий engine.py работает, это рефактор

### P1 — Deploy Prep (1 день)
- Docker Compose для продакшена (отдельный от dev)
- Env vars template (.env.production.example)
- TimeWeb VPS: минимум 2 CPU, 4GB RAM, 40GB SSD
- Nginx конфиг для FastAPI + Vite SPA

### P1 — Telegram Auth (1 день)
- Логин по токену как у OTVETO
- Эндпоинт: `POST /auth/telegram` с токеном в теле
- Хранить telegram_id в User модели
- Файл: `src/api/auth.py` + `src/api/models.py`

### P2 — Billing (2-3 дня)
- Тарифы: Free (100 ответов/мес) / Basic (5000) / Pro (безлимит)
- Интеграция с ЮKassa или Stripe
- Файл: `src/api/routers/billing.py` (новый)

## Verification
- Тест после фиксов: запустить `pytest tests/ -v` (должно быть 764+ passed)
- Scientific RAG тест: `python3 -c "from src.ai.scientific_rag import build_scientific_context; ..."`
  Ожидаем: PubMed ✅, USDA ✅, ODS ✅, NCCIH ✅ (сейчас ODS и USDA падают)
- Чаты: через MCP marketplace-api проверить real chats
- E2E: создать тестовый отзыв → автогенерация → статус APPROVED (auto mode)

## Key Files
- `src/ai/engine.py` — 1687 строк, Polza.ai + fallback chain
- `src/ai/scientific_rag.py` — 8 источников, build_scientific_context()
- `src/ai/ods_factsheets.py` — BUG строка 129 (URL формат)
- `src/ai/prompts.py` — промпты, CTA, SEO добавлять сюда
- `src/services/auto_reply_service.py` — per-rating mode (работает)
- `src/api/models.py` — StoreSettings строки 601-751 (все поля есть)
- `.env` — USDA_API_KEY=DEMO_KEY (заменить)

## Reuse (не трогать)
- `src/ai/cross_sell.py` — stock check пофикшен
- `src/ai/guardrails.py` — quality gate
- `src/connectors/` — все коннекторы МП
- `src/tasks/scheduler.py` — планировщик

## Production Server
- IP: 72.56.121.84 (TimeWeb VPS)
- SSH: root@72.56.121.84
- Закрытые порты: 53413, 3389, 25, 465, 587, 389, 2525
- Нужно проверить: CPU, RAM, disk, OS — рекомендовать апгрейд под MarketAI

## Execution Mode
- Team Mode (параллельные агенты через tmux)
- Порядок: P0 баги → браузерные тесты → SEO/CTA → деплой на сервер
- Браузерные тесты ОБЯЗАТЕЛЬНЫ перед деплоем
