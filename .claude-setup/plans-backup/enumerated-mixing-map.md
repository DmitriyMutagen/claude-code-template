# Plan: MCP Server for МойСклад (MoySklad) API

## Context

Дмитрий использует МойСклад как ERP/складскую систему для всех бизнесов (Aragant/SoulWay, Bio-STM/Bionovacia, маркетплейсы WB/Ozon). Нужен полный MCP-сервер в монорепо `mcp servers/`, чтобы Claude Code мог управлять товарами, заказами, складом, документами и аналитикой через МойСклад API.

**API**: JSON API 1.2 (REMAP), Base URL: `https://api.moysklad.ru/api/remap/1.2/`
**Auth**: Bearer token
**Rate limits**: 100 req/5 sec, 5 parallel per user, 20 per account

---

## Architecture

Новый сервер `servers/moysklad-api/` по образцу `servers/marketplace-api/`. Переиспользуем shared-библиотеку (`mcp_shared`): pagination, circuit breaker, config, logging.

### Directory Structure

```
servers/moysklad-api/
├── pyproject.toml
├── src/moysklad_api/
│   ├── __init__.py
│   ├── __main__.py               # python -m moysklad_api.server
│   ├── server.py                 # FastMCP setup + tool registration
│   ├── config.py                 # Settings(BaseConfig) — MOYSKLAD_TOKEN from .env
│   ├── client.py                 # MoySkladClient (httpx + retry + circuit breaker)
│   └── tools/
│       ├── __init__.py           # register_all()
│       ├── _utils.py             # ok_response, err_response, format_entity
│       ├── products.py           # Товары, услуги, комплекты, модификации
│       ├── counterparties.py     # Контрагенты, организации, договоры
│       ├── orders.py             # Заказы покупателей/поставщиков
│       ├── documents.py          # Отгрузки, приёмки, платежи, счета
│       ├── warehouse.py          # Склады, оприходование, списание, перемещение
│       ├── stock.py              # Остатки, отчёты по остаткам
│       ├── finances.py           # Платежи, валюты, цены, скидки
│       ├── reports.py            # Прибыльность, продажи, dashboard
│       └── settings.py           # Проекты, каналы продаж, сотрудники, настройки
└── tests/
    └── test_client.py
```

---

## Tools (45 tools, grouped by domain)

### Products (8 tools)
| Tool | Endpoint | Description |
|------|----------|-------------|
| `ms_products_list` | GET /entity/product | Список товаров (auto-paginate) |
| `ms_product_get` | GET /entity/product/{id} | Получить товар по ID |
| `ms_product_create` | POST /entity/product | Создать товар |
| `ms_product_update` | PUT /entity/product/{id} | Обновить товар |
| `ms_assortment_list` | GET /entity/assortment | Полный ассортимент (товары+услуги+комплекты) |
| `ms_variants_list` | GET /entity/variant | Модификации товаров |
| `ms_product_folders_list` | GET /entity/productfolder | Группы товаров |
| `ms_services_list` | GET /entity/service | Список услуг |

### Counterparties (5 tools)
| Tool | Endpoint | Description |
|------|----------|-------------|
| `ms_counterparties_list` | GET /entity/counterparty | Список контрагентов |
| `ms_counterparty_get` | GET /entity/counterparty/{id} | Получить контрагента |
| `ms_counterparty_create` | POST /entity/counterparty | Создать контрагента |
| `ms_organizations_list` | GET /entity/organization | Свои юрлица |
| `ms_employees_list` | GET /entity/employee | Список сотрудников |

### Orders (6 tools)
| Tool | Endpoint | Description |
|------|----------|-------------|
| `ms_customer_orders_list` | GET /entity/customerorder | Заказы покупателей |
| `ms_customer_order_get` | GET /entity/customerorder/{id} | Заказ покупателя по ID |
| `ms_customer_order_create` | POST /entity/customerorder | Создать заказ покупателя |
| `ms_purchase_orders_list` | GET /entity/purchaseorder | Заказы поставщикам |
| `ms_purchase_order_get` | GET /entity/purchaseorder/{id} | Заказ поставщику по ID |
| `ms_purchase_order_create` | POST /entity/purchaseorder | Создать заказ поставщику |

### Documents (8 tools)
| Tool | Endpoint | Description |
|------|----------|-------------|
| `ms_demands_list` | GET /entity/demand | Отгрузки |
| `ms_demand_create` | POST /entity/demand | Создать отгрузку |
| `ms_supplies_list` | GET /entity/supply | Приёмки |
| `ms_supply_create` | POST /entity/supply | Создать приёмку |
| `ms_invoices_out_list` | GET /entity/invoiceout | Счета покупателям |
| `ms_invoices_in_list` | GET /entity/invoicein | Счета поставщиков |
| `ms_sales_returns_list` | GET /entity/salesreturn | Возвраты покупателей |
| `ms_purchase_returns_list` | GET /entity/purchasereturn | Возвраты поставщикам |

### Warehouse (5 tools)
| Tool | Endpoint | Description |
|------|----------|-------------|
| `ms_stores_list` | GET /entity/store | Список складов |
| `ms_enter_create` | POST /entity/enter | Оприходование |
| `ms_loss_create` | POST /entity/loss | Списание |
| `ms_move_create` | POST /entity/move | Перемещение |
| `ms_inventory_list` | GET /entity/inventory | Инвентаризации |

### Stock & Reports (6 tools)
| Tool | Endpoint | Description |
|------|----------|-------------|
| `ms_stock_all` | GET /report/stock/all | Остатки по всем товарам |
| `ms_stock_by_store` | GET /report/stock/bystore | Остатки по складам |
| `ms_report_profit` | GET /report/profit/byproduct | Прибыльность по товарам |
| `ms_report_sales` | GET /report/sales/plotseries | Показатели продаж |
| `ms_report_dashboard` | GET /report/dashboard | Дашборд (сводка) |
| `ms_report_money` | GET /report/money/plotseries | Движение денег |

### Finances (4 tools)
| Tool | Endpoint | Description |
|------|----------|-------------|
| `ms_payments_in_list` | GET /entity/paymentin | Входящие платежи |
| `ms_payments_out_list` | GET /entity/paymentout | Исходящие платежи |
| `ms_payment_in_create` | POST /entity/paymentin | Создать входящий платёж |
| `ms_payment_out_create` | POST /entity/paymentout | Создать исходящий платёж |

### Settings (3 tools)
| Tool | Endpoint | Description |
|------|----------|-------------|
| `ms_projects_list` | GET /entity/project | Проекты |
| `ms_currencies_list` | GET /entity/currency | Валюты |
| `ms_company_settings` | GET /entity/companysettings | Настройки компании |

**Total: 45 tools** (under 50 limit)

---

## Client Implementation

### `client.py` — MoySkladClient

```python
class MoySkladClient:
    BASE_URL = "https://api.moysklad.ru/api/remap/1.2"

    def __init__(self, token: str):
        self.token = token
        self._client: httpx.AsyncClient | None = None
        self._cb = CircuitBreaker(name="moysklad", failure_threshold=5, recovery_timeout=60)

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip",
        }

    # Methods: get(), post(), put(), delete()
    # Auto-retry (3 attempts, exponential 2-10s)
    # Circuit breaker wrapping
    # Rate limit: respect 429 + Retry-After
    # Timeout: 30s
```

### Pagination

МойСклад uses **offset/limit** pattern → reuse `paginate_offset` from `mcp_shared.pagination`:
- `limit` default: 1000 (max allowed)
- `offset`: auto-incremented
- Total items from `meta.size`
- Safety: `max_pages=50`

---

## Files to Create

| # | File | Purpose |
|---|------|---------|
| 1 | `servers/moysklad-api/pyproject.toml` | Package config, deps: fastmcp, mcp-shared |
| 2 | `servers/moysklad-api/src/moysklad_api/__init__.py` | Package init |
| 3 | `servers/moysklad-api/src/moysklad_api/__main__.py` | Entry point |
| 4 | `servers/moysklad-api/src/moysklad_api/config.py` | Settings (MOYSKLAD_TOKEN) |
| 5 | `servers/moysklad-api/src/moysklad_api/client.py` | HTTP client with retry+CB |
| 6 | `servers/moysklad-api/src/moysklad_api/server.py` | FastMCP setup + registration |
| 7 | `servers/moysklad-api/src/moysklad_api/tools/__init__.py` | register_all() |
| 8 | `servers/moysklad-api/src/moysklad_api/tools/_utils.py` | Response helpers |
| 9 | `servers/moysklad-api/src/moysklad_api/tools/products.py` | 8 tools |
| 10 | `servers/moysklad-api/src/moysklad_api/tools/counterparties.py` | 5 tools |
| 11 | `servers/moysklad-api/src/moysklad_api/tools/orders.py` | 6 tools |
| 12 | `servers/moysklad-api/src/moysklad_api/tools/documents.py` | 8 tools |
| 13 | `servers/moysklad-api/src/moysklad_api/tools/warehouse.py` | 5 tools |
| 14 | `servers/moysklad-api/src/moysklad_api/tools/stock.py` | 6 tools |
| 15 | `servers/moysklad-api/src/moysklad_api/tools/finances.py` | 4 tools |
| 16 | `servers/moysklad-api/src/moysklad_api/tools/settings.py` | 3 tools |

### Files to Modify

| # | File | Change |
|---|------|--------|
| 17 | `pyproject.toml` (root) | Add `servers/moysklad-api` to workspace members |
| 18 | `.env` | Add `MOYSKLAD_TOKEN=bb403ab0cada855017c9ed5553f1b4e4da35c175` |

---

## Reusable Components (from libs/shared/)

- `mcp_shared.pagination.paginate_offset` — offset/limit auto-pagination
- `mcp_shared.circuit_breaker.CircuitBreaker` — fault tolerance
- `mcp_shared.config.BaseConfig` — env var loading via Pydantic
- `mcp_shared.logging.get_logger` — stderr-only logging

---

## Safety Rules

1. **Мутации (create/update/delete)** — каждый tool чётко описывает что делает; Claude не вызовет случайно
2. **Rate limiting** — 100 req/5s, встроим в клиент через throttle
3. **Pagination** — все list-tools с auto-paginate + max_items параметр
4. **Secrets** — токен ТОЛЬКО в .env, NEVER в коде

---

## Verification

1. `uv sync` — установка зависимостей
2. `uv run --project servers/moysklad-api python -m moysklad_api.server` — запуск сервера
3. Проверить что токен работает: `ms_company_settings` → должен вернуть настройки компании
4. `ms_products_list` → список товаров
5. `ms_stock_all` → остатки
6. `ms_customer_orders_list` → заказы
7. `ms_report_dashboard` → сводка по бизнесу
8. После проверки — добавить сервер в Claude Code settings как MCP server
