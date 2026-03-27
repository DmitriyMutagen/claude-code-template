# Plan: MCP Servers Audit + Bug Fix

## Context
Дмитрий добавил 12 новых MCP серверов для маркетплейсов (Ozon ×4, WB ×4, YM ×4) с суммарно 526+ инструментами.
Задача: аудит + исправление всех найденных багов. MarketAI интеграция — отдельная задача на потом.
Решение принято: только фикс багов (Фаза 3 интеграция исключена).

**Расположение серверов**: `/Users/Dmitrij/Documents/mcp servers/servers/`
**Общая библиотека**: `/Users/Dmitrij/Documents/mcp servers/libs/shared/src/mcp_shared/`

---

## Итоги аудита (Phase 1 результаты)

### Сводная таблица багов

| Сервер | CRIT | HIGH | MED | LOW | Итого |
|--------|------|------|-----|-----|-------|
| ozon-seller + ozon-operations + ozon-ads + ozon-logistics | 0 | 2 | 3 | 1 | 6 |
| wb-content + wb-marketplace + wb-analytics + wb-ads | 2 | 3 | 5 | 5 | 15 |
| ym-catalog + ym-orders + ym-analytics + ym-comms + ym-api | 3 | 5 | 8 | 4 | 20 |
| **ИТОГО** | **5** | **10** | **16** | **10** | **41** |

> Примечание: `"pluse"` в wb-ads/keywords_search.py — НЕ баг. WB API сам требует эту опечатку.
> Примечание: `client._request("DELETE", ...)` — корректно, проходит через circuit breaker. Нужно добавить `delete()` метод для консистентности.

---

## Фаза 1: Исправление багов (приоритет: CRIT → HIGH → MED)

### 1.1 Shared Library — добавить `delete()` метод

**Файл**: `libs/shared/src/mcp_shared/http_client.py`
**Проблема**: `BaseHTTPClient` не имеет публичного `delete()` метода, что вынуждает код вызывать `_request("DELETE", ...)` напрямую.
**Фикс**: добавить метод после `patch()` (строка 100):
```python
async def delete(self, path: str, params: dict | None = None, data: dict | None = None) -> dict:
    kwargs: dict = {}
    if params:
        kwargs["params"] = params
    if data:
        kwargs["json"] = data
    return await self._request("DELETE", path, **kwargs)
```

**Затронутые серверы после добавления**: ym-analytics/tools/outlets.py:81,126 и все future DELETE-вызовы.

---

### 1.2 Ozon серверы — 6 багов

**CRIT**: нет

**HIGH-1**: `ozon-operations/src/ozon_operations/tools/finance.py:61`
Тип: `ValueError` при нечисловых строках
```python
# Было:
ids = [int(x.strip()) for x in product_ids.split(",")]
# Надо:
ids = [int(x.strip()) for x in product_ids.split(",") if x.strip().lstrip("-").isdigit()]
```

**HIGH-2**: `ozon-operations/src/ozon_operations/tools/analytics.py:96`
Тот же паттерн — `int(s.strip())` без валидации.
Фикс аналогичный — добавить guard `.isdigit()`.

**MED-1**: `ozon-ads/src/ozon_ads/server.py:162`
Lambda в async-контексте — заменить на `async def _call()`.

**MED-2 & MED-3**: `ozon-operations/src/ozon_operations/tools/returns.py:24,44`
`err_response(error)` без кода → `err_response(error, "INVALID_JSON")`.

**LOW**: Health check в ozon-seller и ozon-logistics использует `/v2/product/info/list` с пустым телом — нестабильный индикатор. Заменить на более легкий эндпоинт или добавить `ozon-operations` health check.

---

### 1.3 WB серверы — 15 багов

**CRIT-1**: `wb-marketplace/tools/orders.py:55`
Параметр `type: str` затеняет Python builtin.
```python
# Было: async def wb_order_sticker(order_id: int, type: str = "svg")
# Надо: async def wb_order_sticker(order_id: int, sticker_type: str = "svg")
# + params={"type": sticker_type, ...}
```

**CRIT-2**: `wb-analytics/tools/questions.py:82`
`feedbacks._request("DELETE", ...)` — после добавления `delete()` в BaseHTTPClient заменить на `feedbacks.delete(...)`.

**HIGH-1**: `wb-content/client.py:41`
Требует верификации: WB Content API (статистика товаров, медиа) требует `Authorization: Bearer {token}`, а не raw token.
```python
# Проверить: нужен ли Bearer для конкретных content-api эндпоинтов
return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
```

**HIGH-2**: `wb-marketplace/server.py:75`
Дублирование headers — убрать `headers=self.headers` из вызова request, так как AsyncClient уже имеет эти headers.

**HIGH-3**: `wb-analytics/server.py:39`
Нет проверки наличия токена при старте.
```python
if not settings.wb_api_token:
    logger.error("WB_API_TOKEN not set — all requests will fail with 401")
```

**MED-1**: `wb-content/tools/media.py:25`
`Content-Type: multipart/form-data` задан, но бинарный контент не передаётся.
Либо реализовать реальный upload через httpx multipart, либо пометить как TODO и убрать некорректный заголовок.

**MED-2 и остальные MED/LOW**: Консистентность response envelope (`{"ok": True}` vs `{"status": "ok"}`), error code consistency, retry_after math cleanup.

---

### 1.4 YM серверы — 20 багов

**CRIT-1** (3 конфига): `ym-orders/config.py:14`, `ym-analytics/config.py:14`, `ym-comms/config.py:14`
Hardcoded `ym_business_id: str = "35517383"` — Дмитриев ID как дефолт.
```python
# Во всех трёх файлах:
ym_business_id: str = ""  # убрать дефолт
```

**CRIT-2**: `ym-catalog/tools/offer_mappings.py:113`
Использует `/v1/` эндпоинт для barcode generation, все другие используют `/v2/`.
Фикс: заменить на `/v2/businesses/{ym.bid}/offer-mappings/barcodes/generate`.

**CRIT-3**: `ym-analytics/tools/outlets.py:81,126`
`client._request("DELETE", ...)` → после добавления `delete()` заменить на `client.delete(...)`.

**HIGH-1**: `ym-orders/tools/shipments.py:31`
`PUT` вместо `POST` для list/query эндпоинта `/first-mile/shipments`.
Фикс: `client.post(...)`.

**HIGH-2**: `ym-api/clients/partner.py:196`
Пагинация через `page` (int) вместо `pageToken` (string).
YM API использует cursor-based pagination. Рефакторинг: заменить `page`/`pageSize` на `pageToken`.

**HIGH-3**: `ym-catalog/tools/campaigns.py:52`
`POST` для auth token info эндпоинта — должен быть `GET`.
Верифицировать с YM docs, скорее всего: `client.get("/v2/auth/token")`.

**MED-1 (3 штуки)**: Hardcoded бизнес ID убраны выше в CRIT.

**MED-2**: `ym-orders/tools/order_delivery.py:27,37,45`
Документация говорит `DD-MM-YYYY`, но YM требует `YYYY-MM-DD`.
Исправить docstrings, добавить конвертацию или валидацию.

**MED-3**: `ym-analytics/tools/bids.py:19,37`
Нет валидации структуры bids (должны быть int в копейках, > 0).

**HIGH-4,5 / LOW**: Несогласованность naming `get_questions` vs POST-метод, comment про 120s сон.

---

## Фаза 2: Архитектурные улучшения (после фикса багов)

### 2.1 Унификация HTTP клиентов

**Проблема**: WB серверы используют разные подходы:
- wb-content: собственный `WBContentClient`
- wb-marketplace: клиент прямо в server.py
- wb-analytics/wb-ads: `BaseHTTPClient` из shared lib

**Решение**: Перевести wb-content и wb-marketplace на `BaseHTTPClient` из mcp_shared. Это даёт:
- Единый retry/circuit breaker для всех
- Один код для поддержки

**Файлы**: `wb-content/client.py`, `wb-marketplace/server.py`

### 2.2 Стандартизация response envelope

**Проблема**: wb-analytics использует `{"status": "ok"}` vs остальные `{"ok": True}`.

**Решение**: Обновить `wb-analytics/tools/_utils.py` чтобы использовал тот же формат что `wb-content`, `wb-marketplace`.

### 2.3 Валидация конфигурации при старте

Добавить в `BaseConfig` (mcp_shared/config.py) или в каждый `server.py` — логирование warning если критические поля пустые (токены, IDs).

---

## Файлы для изменения (по приоритету)

### Шаг 1 — Shared lib (1 файл)
- `libs/shared/src/mcp_shared/http_client.py` — добавить `delete()` метод

### Шаг 2 — Критические YM фиксы (4 файла)
- `servers/ym-orders/src/ym_orders/config.py` — убрать hardcoded business_id
- `servers/ym-analytics/src/ym_analytics/config.py` — то же
- `servers/ym-comms/src/ym_comms/config.py` — то же
- `servers/ym-catalog/src/ym_catalog/tools/offer_mappings.py:113` — /v1/ → /v2/

### Шаг 3 — Критические WB фиксы (3 файла)
- `servers/wb-marketplace/src/wb_marketplace/tools/orders.py:55` — rename `type` param
- `servers/wb-analytics/src/wb_analytics/tools/questions.py:82` — `_request("DELETE")` → `delete()`
- `servers/ym-analytics/src/ym_analytics/tools/outlets.py:81,126` — аналогично

### Шаг 4 — HIGH фиксы YM/WB (5 файлов)
- `servers/ym-orders/src/ym_orders/tools/shipments.py:31` — PUT → POST
- `servers/ym-catalog/src/ym_catalog/tools/campaigns.py:52` — POST → GET
- `servers/wb-analytics/src/wb_analytics/server.py:39` — token validation
- `servers/wb-marketplace/src/wb_marketplace/server.py:75` — remove dup headers
- `servers/wb-content/src/wb_content/client.py:41` — verify Bearer prefix

### Шаг 5 — HIGH фиксы Ozon (2 файла)
- `servers/ozon-operations/src/ozon_operations/tools/finance.py:61`
- `servers/ozon-operations/src/ozon_operations/tools/analytics.py:96`

### Шаг 6 — MED фиксы (10+ файлов)
- YM date format docs (ym-orders delivery tools)
- WB response envelope standardization (wb-analytics _utils.py)
- Returns error codes (ozon-operations returns.py)
- Ozon-ads lambda → async def

### Шаг 7 — MarketAI интеграция
- `src/api/routers/admin.py` — MCP status endpoint
- `src/tasks/marketplace_monitor.py` — autonomous monitor
- `frontend-react/src/pages/AdminMonitoring.tsx` — MCP tab

---

## Верификация после исправлений

1. **Unit тесты**: `cd "/Users/Dmitrij/Documents/mcp servers" && uv run pytest tests/ -v`
2. **Запуск сервера**: `uv run --project servers/ym-orders python -m ym_orders` — должен стартовать без ошибок
3. **Тест DELETE**: вызвать `ym_outlet_delete(outlet_id=999)` — должен использовать `client.delete()`, не упасть
4. **Config validation**: запустить ym-orders без `YM_BUSINESS_ID` env — должен логировать warning
5. **MarketAI tests**: `cd marketai && pytest tests/ -v -k "not ozon_chat"` — должен пройти
