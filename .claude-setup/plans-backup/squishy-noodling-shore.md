# Plan: MCP Server Audit, Hardening & MarketAI Integration

## Context

MarketAI (SaaS для ответов на отзывы маркетплейсов) и MCP сервер `marketplace-api` (46 инструментов для Ozon/WB/YM) дублируют логику API-клиентов. MCP сервер содержит 10 проблем (нет валидации, нет circuit breaker, нет тестов). MarketAI уже имеет `MCPClientManager` (`src/mcp_client.py`), но MCP не активирован (`MCP_ENABLED=False`). Цель: захардить MCP, протестировать, интегрировать в MarketAI, предложить новые возможности.

---

## Phase 1: MCP Server Hardening (10 фиксов)

### 1.1 JSON Input Validation
- **Файл**: NEW `servers/marketplace-api/src/marketplace_api/tools/_utils.py`
- Функция `safe_json_parse(raw: str, context: str) -> tuple[dict|list, str|None]` — обёртка json.loads с try-except
- **Modify**: 8 tool-файлов с `json.loads` (ozon_products, ozon_stocks, ozon_prices, wb_products, wb_stocks, wb_prices, ym_products, ym_stocks) — заменить голый `json.loads` на `safe_json_parse`

### 1.2 Error Envelope
- **Файл**: `_utils.py` (тот же)
- Функции `ok_response(data)` и `err_response(error, code)` → JSON строка `{"ok": true, "data": {...}}` / `{"ok": false, "error": "...", "code": "..."}`
- **Modify**: все 17 tool-файлов — обернуть return в `ok_response()`, except-блоки в `err_response()`

### 1.3 Circuit Breaker
- **Файл**: NEW `libs/shared/src/mcp_shared/circuit_breaker.py`
- Портировать `CircuitBreaker` из MarketAI (`src/connectors/circuit_breaker.py`, 95 строк, 0 внешних зависимостей)
- **Modify**: `clients/ozon.py`, `clients/wb.py`, `clients/yandex.py` — добавить `self._cb = CircuitBreaker(name=..., failure_threshold=5, recovery_timeout=60)` и обернуть `_request()` через `self._cb.call()`

### 1.4 Auth Error Fast-Fail + Logging
- **Modify**: все 3 клиента — добавить `logger.error("Check API credentials")` при 401/403
- Текущий код УЖЕ не ретраит 401/403 (поднимает `OzonAPIError` → не в `retry_if_exception_type`), но лог неинформативен

### 1.5 Rate Limit Improvements
- **Modify**: `clients/ozon.py` — при 429 парсить `Retry-After` header, если есть
- **Modify**: `clients/wb.py` — при 429 увеличить backoff до min=5s (WB имеет 3 RPS лимит)
- **Modify**: `clients/yandex.py` — 420 handling уже есть, оставить

### 1.6 HTTP Client Shutdown
- **Modify**: `server.py` — добавить `atexit` handler + `@mcp.on_event("shutdown")` (если FastMCP поддерживает) для корректного `await client.close()`

### 1.7 WB Pagination Fix
- **Modify**: `tools/wb_products.py` — добавить `cursor_json: str = ""` параметр в `wb_cards_list`, пробросить в клиент

### 1.8 Hardcoded Defaults
- **Modify**: `config.py` — `wb_seller_id: str = ""`, `ym_business_id: str = ""`
- **Modify**: `server.py` — добавить warning в stderr если credentials пустые

### 1.9 Request Logging
- **Modify**: все 3 клиента — добавить `logger.info("-> %s %s", method, path)` и `logger.info("<- %s %s %dms", method, path, elapsed)` в `_request()`

### 1.10 Metrics Tool
- **Файл**: NEW `tools/system.py` — MCP tool `marketplace_api_health()` → статус подключений, кол-во вызовов, состояние circuit breaker

---

## Phase 2: Testing MCP Server

### 2.1 Test Infrastructure
- **Файл**: NEW `tests/conftest.py` — фикстуры с mock-клиентами (respx для httpx mocking)
- **Dependencies**: добавить `respx`, `pytest`, `pytest-asyncio` в pyproject.toml [dev]

### 2.2 Client Tests (18 тестов)
- NEW `tests/test_ozon_client.py` — 6 тестов: success, 429 retry, 401 fast-fail, 500 retry+CB, empty response, close()
- NEW `tests/test_wb_client.py` — 6 тестов: аналогично
- NEW `tests/test_ym_client.py` — 6 тестов: аналогично + 420 handling

### 2.3 Tool Tests (15 тестов)
- NEW `tests/test_ozon_tools.py` — 5 тестов: reviews_list, review_reply, products_list, invalid JSON, error envelope
- NEW `tests/test_wb_tools.py` — 5 тестов: аналогично
- NEW `tests/test_ym_tools.py` — 5 тестов: аналогично

### 2.4 Live Smoke Test
- NEW `tests/test_integration.py` (`@pytest.mark.integration`, skip by default)
- Тестирует read-only операции с реальным API: `ozon_products_list(limit=1)`, `wb_cards_list(limit=1)`, `ym_offers_list(limit=1)`

---

## Phase 3: MarketAI MCP Integration

### Стратегия: MCP как дополнительный канал, НЕ замена коннекторов

MarketAI connectors СОХРАНЯЮТСЯ для sync engine (multi-tenant, circuit breaker, typed dataclasses, UPSERT). MCP используется для:
1. Claude Code прямого доступа к маркетплейсам
2. Real-time данных в AI engine (запрос актуальных цен/остатков)
3. Admin мониторинг через MCP health check

### 3.1 MCP Config Activation
- **Modify**: `marketai/.env` — `MCP_ENABLED=true`
- **Файл**: NEW `marketai/mcp_servers.json` — конфигурация marketplace-api сервера с env vars

### 3.2 MCP Marketplace Service
- **Файл**: NEW `marketai/src/services/mcp_marketplace_service.py`
- `MCPMarketplaceService` — facade для вызова MCP tools из AI engine
- Методы: `get_realtime_stock(sku)`, `get_latest_reviews(marketplace, limit)`, `check_price(product_id)`
- Graceful fallback на данные из БД при MCP недоступности

### 3.3 Admin MCP Status
- **Modify**: `src/api/routers/admin.py` — endpoint `GET /admin/mcp-status` → список серверов, статус подключения, доступные tools
- **Modify**: `frontend-react/src/pages/AdminMonitoring.tsx` — таб "MCP Servers" с индикаторами

---

## Phase 4: Code Structure Improvements

### 4.1 Sync Freshness Check (опционально)
- **Modify**: `src/services/sync_engine.py` — перед полным sync проверить через MCP `ozon_reviews_list(limit=1)` и сравнить с последним `external_id` в БД. Если совпадает — skip sync cycle. Экономит API квоты.

### 4.2 Product Enrichment via MCP
- `src/services/product_enrichment.py` уже обращается к коннекторам за атрибутами товара. Можно добавить альтернативный путь через MCP tool `ozon_product_get` для одиночных товаров (когда connector instance не доступен).

---

## Phase 5: New Features

### 5.1 Cross-Marketplace Price/Stock Comparison
- **Файл**: NEW `servers/marketplace-api/src/marketplace_api/tools/cross_marketplace.py`
- Tools: `cross_price_compare(sku)`, `cross_stock_compare(sku)` — запрашивает все 3 маркетплейса параллельно

### 5.2 Autonomous Review Monitor Script
- **Файл**: NEW `marketai/scripts/mcp_review_monitor.py`
- Standalone скрипт: MCP → непрочитанные отзывы → AI генерация → Telegram approval → MCP reply
- Может запускаться через cron или Claude Code loop

### 5.3 MCP Skills for Claude Code
- NEW `~/.claude/skills/marketplace-monitor.md` — скилл для Claude Code: мониторинг новых отзывов через MCP
- NEW `~/.claude/skills/marketplace-analytics.md` — скилл для аналитики через MCP tools

---

## Verification

1. **Phase 1**: `cd "/Users/Dmitrij/Documents/mcp servers" && uv run pytest tests/ -v` — 33+ тестов pass
2. **Phase 2**: `uv run pytest tests/test_integration.py -m integration` — smoke test с реальным API
3. **Phase 3**: Запуск MarketAI → Admin → MCP Status таб показывает "marketplace-api: connected, 46 tools"
4. **Phase 4**: Запуск sync → лог показывает "MCP freshness check: no new reviews, skipping"
5. **Full**: Все 713 существующих тестов MarketAI проходят без изменений

---

## Files Summary

### MCP Server (create/modify)
| Action | File |
|--------|------|
| NEW | `servers/marketplace-api/src/marketplace_api/tools/_utils.py` |
| NEW | `servers/marketplace-api/src/marketplace_api/tools/system.py` |
| NEW | `servers/marketplace-api/src/marketplace_api/tools/cross_marketplace.py` |
| NEW | `libs/shared/src/mcp_shared/circuit_breaker.py` |
| MODIFY | `servers/marketplace-api/src/marketplace_api/config.py` |
| MODIFY | `servers/marketplace-api/src/marketplace_api/server.py` |
| MODIFY | `servers/marketplace-api/src/marketplace_api/clients/ozon.py` |
| MODIFY | `servers/marketplace-api/src/marketplace_api/clients/wb.py` |
| MODIFY | `servers/marketplace-api/src/marketplace_api/clients/yandex.py` |
| MODIFY | All 17 tool files (error envelope + safe_json_parse) |
| NEW | `tests/conftest.py` + 7 test files |

### MarketAI (create/modify)
| Action | File |
|--------|------|
| NEW | `mcp_servers.json` |
| NEW | `src/services/mcp_marketplace_service.py` |
| NEW | `scripts/mcp_review_monitor.py` |
| MODIFY | `.env` (MCP_ENABLED=true) |
| MODIFY | `src/api/routers/admin.py` (+MCP status endpoint) |
| MODIFY | `frontend-react/src/pages/AdminMonitoring.tsx` (+MCP tab) |
| MODIFY | `src/services/sync_engine.py` (freshness check, optional) |

### Skills
| Action | File |
|--------|------|
| NEW | `~/.claude/skills/marketplace-monitor.md` |
| NEW | `~/.claude/skills/marketplace-analytics.md` |
