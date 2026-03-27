# MarketAI v2.0 — MCP Integration & Platform Evolution Plan

## Context

MarketAI v1.7.0+ — SaaS для автоматизации ответов на отзывы маркетплейсов (Ozon, WB, YM) с AI.
Дмитрий разделил единый `marketplace-api` MCP сервер на 3 отдельных: `ozon-api`, `wb-api`, `ym-api` — каждый с рекламными API и исправлениями. Нужен полный аудит, фикс багов, интеграция в MarketAI, и новые фичи (реклама, кросс-аналитика).

**Текущее состояние:** 462K+ отзывов, 354 продукта, 713 тестов, 28 коммитов на `feature/stabilization-billing-onboarding`.

---

## Phase 1: MCP Server Bug Fixes [CRITICAL, ~1-2 дня]

### 1.1 Ozon Performance API token refresh bug
- **Файл:** `/Users/Dmitrij/Documents/mcp servers/servers/ozon-api/src/ozon_api/clients/performance.py`
- **Проблема:** При 401 токен обновляется, но tenacity не перезапускает запрос — он падает
- **Фикс:** После рефреша токена бросать retryable exception (`httpx.TransportError("Token expired")`), чтобы tenacity повторил запрос с новым токеном
- **Размер:** S
- **Проверка:** Unit test — mock 401, затем 200. Verify retry + success

### 1.2 YM 120-секундный blocking sleep
- **Файл:** `/Users/Dmitrij/Documents/mcp servers/servers/ym-api/src/ym_api/clients/partner.py`
- **Проблема:** `await asyncio.sleep(120)` на статус 420 блокирует весь MCP сервер на 2 минуты
- **Фикс:** Заменить на `raise httpx.TransportError("YM 420 rate limit")` — tenacity сделает exponential backoff (5-60s, 4 попытки)
- **Размер:** S
- **Проверка:** Mock 420 → verify нет длинного sleep, retry работает

### 1.3 Error response truncation (все серверы)
- **Файлы:**
  - `/Users/Dmitrij/Documents/mcp servers/libs/shared/src/mcp_shared/http_client.py`
  - `ozon-api/.../clients/seller.py`, `performance.py`
  - `ym-api/.../clients/partner.py`
- **Проблема:** `resp.text[:500]` обрезает отладочную инфу
- **Фикс:** Увеличить до 2000 chars, полный body хранить в `APIError.response_body`
- **Размер:** S

### 1.4 Circuit breaker для всех MCP серверов
- **Файлы:** `mcp_shared/http_client.py` + все client файлы (6+)
- **Фикс:** Добавить `circuit_breaker_name` параметр в `BaseHTTPClient.__init__`, обернуть `_request` в `self._cb.call()`. Для Ozon seller/performance — добавить вручную
- **Размер:** M
- **Проверка:** После 5 ошибок — circuit открывается, fast-fail. После recovery — half-open

---

## Phase 2: MCP Server Hardening [HIGH, ~2-3 дня]

### 2.1 Configurable timeouts
- **Файл:** `mcp_shared/config.py` → TimeoutConfig class
- Default: 30s, Analytics: 60s, Ads stats: 45s, Bulk: 90s
- Каждый tool передаёт нужный timeout в client
- **Размер:** M

### 2.2 Health metrics & observability
- **Новый файл:** `mcp_shared/metrics.py` — MetricsCollector (in-memory)
  - `record_request(endpoint, latency_ms, status_code)`
  - `get_stats()` → error rates, avg latency, p95
- Интеграция в `BaseHTTPClient._request` — авто-запись метрик
- Обновить `*_health_check` tools → возвращать circuit breaker states + latency stats
- **Размер:** M

### 2.3 Rate limit prediction
- **Новый файл:** `mcp_shared/rate_limiter.py` — sliding window counter
- WB: 3 RPS, YM: custom (420 handling), Ozon: 50 RPM
- Проактивный wait вместо "ударился в лимит и ретрай"
- **Размер:** M

---

## Phase 3: MarketAI Integration [HIGH, ~4-5 дней]

### 3.1 MCP config activation
- **Файл:** `marketai/src/config.py`
- Добавить: `MCP_OZON_ENABLED`, `MCP_WB_ENABLED`, `MCP_YM_ENABLED` (bool)
- **Новый файл:** `marketai/mcp_servers.json` — конфиг 3 серверов (command, args, env)
- Обновить `MCP_ENABLED=True` в `.env`
- **Размер:** S

### 3.2 MCP Facade Service
- **Новый файл:** `marketai/src/services/mcp_facade.py`
- Тонкая обёртка над MCPClientManager с бизнес-методами:
  - `get_ozon_ads_campaigns()`, `get_wb_ads_campaigns()`
  - `get_cross_marketplace_analytics(date_from, date_to)` — параллельные вызовы всех 3 MP
  - `get_marketplace_health()` — статусы всех серверов
  - `get_real_time_product(marketplace, product_id)` — live данные продукта
- FastAPI dependency: `get_mcp_facade()`
- **Размер:** L

### 3.3 Admin MCP Status
- **Файл:** `marketai/src/api/routers/admin.py` → `GET /admin/mcp-status`
- **Frontend:** `Admin.tsx` → новый таб "MCP Servers" (статусы, tools count, health)
- **Размер:** S

### 3.4 Activity logging call sites
- **Файлы:** `auth_router.py`, `reviews.py`, `sync.py`, `chats.py`, `ai.py`
- Добавить `await log_activity(db, ...)` в ключевые действия (login, approve, sync, generate)
- Инфра готова (`activity_logger.py`), нужны только вызовы
- **Размер:** S

---

## Phase 4: Remaining Tasks [HIGH, ~3-4 дня]

### 4.1 WB product_id backfill (69K отзывов)
- **Файл:** `marketai/src/tasks/wb_sync.py` (lines 104-119)
- **Root cause:** UPSERT never includes `product_id`. WB API возвращает `productDetails.nmId`
- **Фикс:**
  1. Pre-load product map: `{external_id: product.id}` для shop
  2. Extract `nmId` из feedback, lookup в map
  3. Добавить `product_id` в values + `on_conflict_do_update`
  4. Re-sync WB reviews → автоматически проставит product_id
- **Размер:** M
- **Проверка:** `SELECT COUNT(*) FROM reviews WHERE marketplace='wildberries' AND product_id IS NOT NULL`

### 4.2 Ozon questions re-sync
- **Файл:** `marketai/src/tasks/ozon_sync.py` (или новый `ozon_questions_sync.py`)
- Верифицировать что 358+ questions синхронизированы
- **Размер:** S

### 4.3 Data reconciliation script
- **Новый файл:** `marketai/scripts/reconcile_data.py`
- Сравнивает DB counts vs API counts через MCP tools
- Output: discrepancies per entity per shop
- **Размер:** S

---

## Phase 5: New Features [MEDIUM-HIGH, ~8-12 дней]

### 5.1 Ad Campaign Management Dashboard [NEW MAJOR FEATURE]

**Backend:** `marketai/src/api/routers/advertising.py`
```
GET  /advertising/campaigns              — All campaigns, all MPs
GET  /advertising/campaigns/{id}         — Campaign details
POST /advertising/campaigns/{id}/activate    — Start
POST /advertising/campaigns/{id}/deactivate  — Pause
GET  /advertising/campaigns/{id}/statistics  — Stats
GET  /advertising/campaigns/{id}/keywords    — Keywords
PUT  /advertising/campaigns/{id}/budget      — Budget control
PUT  /advertising/campaigns/{id}/bids        — Bid control
GET  /advertising/analytics                  — Aggregated ad analytics
```

**Data normalizer:** `marketai/src/services/ad_normalizer.py`
- `UnifiedAdCampaign` dataclass — единая схема (id, marketplace, name, status, type, budget, spent, impressions, clicks, ctr, cpc, orders, revenue, roas)
- Маппинг: Ozon states → active/paused, WB statuses (9/11) → active/paused, YM promos → promo

**Frontend:** `frontend-react/src/pages/Advertising.tsx`
- Табы: All / Ozon / WB / YM
- Summary cards: Total spend, Impressions, Clicks, CTR, ROAS
- DataGrid таблица кампаний с сортировкой/фильтрацией
- Campaign detail drawer: stats, keywords, bids, budget editor
- Charts: Spend trend, Impressions/Clicks, CTR comparison (recharts)
- **Auth:** JWT + admin/manager role (бюджетный контроль — sensitive)

**Размер:** L | **Зависимости:** Phase 3.2 (MCP Facade)

### 5.2 Cross-Marketplace Analytics Dashboard [NEW MAJOR FEATURE]

**Backend:** `marketai/src/api/routers/cross_analytics.py`
```
GET /cross-analytics/overview       — Revenue, orders across all MPs
GET /cross-analytics/products       — Top products by revenue
GET /cross-analytics/trends         — Time-series comparison
GET /cross-analytics/review-quality — Rating trends per MP
```
- Параллельные вызовы MCP tools для Ozon/WB/YM analytics
- Redis cache 1h TTL

**Frontend:** `frontend-react/src/pages/CrossAnalytics.tsx`
- Date range picker
- Revenue pie chart (Ozon/WB/YM split)
- Trend chart: 3 линии по revenue
- Product comparison table
- Review quality section

**Размер:** M | **Зависимости:** Phase 3.2

### 5.3 Autonomous Monitoring System

**Файл:** `marketai/src/services/autonomous_monitor.py`
- Background asyncio task (FastAPI lifespan)
- Каждые 5 мин: health check MCP серверов
- Каждые 10 мин: freshness sync_runs per shop
- Каждые 30 мин: unprocessed review backlog
- Каждый час: AI generation success rate
- **Self-healing:** stale sync > 2h → trigger re-sync; MCP down → fallback to connector; AI errors > 10% → alert
- Alerts: `error_logs` table + Telegram notification

**Размер:** M | **Зависимости:** Phase 3.1

---

## MCP Server Audit Summary

| Сервер | Tools | Реклама | Чат | Критичные баги | Статус |
|--------|-------|---------|-----|----------------|--------|
| **ozon-api** | 30+ | Full (campaigns, budget, keywords, bids, stats) | Yes | Token refresh retry bug | Fixable |
| **wb-api** | 40+ | Full (campaigns, budget, keywords, auto-bids, stats) | No | Нет критичных | Good |
| **ym-api** | 25+ | Partial (promos only, no direct ads) | Yes | 120s blocking sleep | Fixable |

### Что покрыто рекламой:
- **Ozon:** Campaign CRUD, Budget get/set, Keywords CRUD, Bids CRUD, Statistics daily/aggregate
- **WB:** Campaign CRUD + start/pause/stop, Budget deposit, Keywords CRUD, Auto-bids, Statistics
- **YM:** Только промо-акции (добавление товаров в промо), НЕТ campaign management

---

## Dependency Graph & Parallelization

```
Phase 1 (bugs) ──────── start immediately, ~1-2 дня
  │  ├── 1.1 Ozon token ──┐
  │  ├── 1.2 YM sleep ────┤ parallel
  │  ├── 1.3 truncation ──┤
  │  └── 1.4 circuit brk ─┘
  ▼
Phase 2 (hardening) ──── depends on 1.3, 1.4
  │
  ▼
Phase 3 (integration) ── depends on Phase 1
  │  ├── 3.1 config ──── no deps
  │  ├── 3.2 facade ──── depends on 3.1
  │  ├── 3.3 admin UI ── depends on 3.1
  │  └── 3.4 activity ── NO deps, parallel with all
  │
  ├──── Phase 4 (remaining) ─── 4.1 WB backfill: START NOW (no MCP dep)
  │                              4.2 Ozon questions: START NOW
  │                              4.3 reconciliation: after 3.2
  ▼
Phase 5 (features) ──── depends on 3.2
  ├── 5.1 Ad Dashboard (L) ── backend ‖ frontend parallel
  ├── 5.2 Cross Analytics (M) ── can parallel with 5.1
  └── 5.3 Monitoring (M) ──── depends on 3.1 only
```

**Можно начать сразу (Phase 1 + 4.1 + 4.2 + 3.4 параллельно).**

---

## Verification Plan

1. **MCP Bug Fixes:** Unit tests для каждого фикса (mock 401/420/500)
2. **Circuit Breaker:** Integration test — 5 failures → open → fast-fail → recovery
3. **MCP Integration:** `MCP_ENABLED=true`, backend start → verify all 3 servers connect
4. **WB Backfill:** SQL query `product_id IS NOT NULL` count before/after
5. **Ad Dashboard:** E2E test — navigate to /advertising, see campaigns
6. **Cross Analytics:** Navigate to /cross-analytics, verify 3 MP data renders
7. **Autonomous Monitor:** Kill MCP server → verify alert in 5 min
8. **Full regression:** `pytest tests/ -v` — all 713+ tests pass

---

## Critical Files Reference

### MCP Servers (to fix):
- `mcp servers/libs/shared/src/mcp_shared/http_client.py` — truncation + circuit breaker
- `mcp servers/servers/ozon-api/src/ozon_api/clients/performance.py` — token retry
- `mcp servers/servers/ym-api/src/ym_api/clients/partner.py` — blocking sleep

### MarketAI (to modify/create):
- `marketai/src/config.py` — MCP config flags
- `marketai/src/mcp_client.py` — existing, activate
- `marketai/src/services/mcp_facade.py` — NEW facade
- `marketai/src/services/ad_normalizer.py` — NEW normalizer
- `marketai/src/services/autonomous_monitor.py` — NEW monitor
- `marketai/src/api/routers/advertising.py` — NEW router
- `marketai/src/api/routers/cross_analytics.py` — NEW router
- `marketai/src/tasks/wb_sync.py` — product_id fix
- `frontend-react/src/pages/Advertising.tsx` — NEW page
- `frontend-react/src/pages/CrossAnalytics.tsx` — NEW page
