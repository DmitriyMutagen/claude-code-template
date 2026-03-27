# Plan: MCP Servers Monorepo — Marketplace API Server

## Context

Дмитрий строит MCP-серверы для Claude Code, чтобы агент имел полный доступ к API маркетплейсов (Ozon, Wildberries, Yandex Market). Уже существуют production-ready async клиенты в проекте MarketAI (`~/Documents/marketai/marketai/src/connectors/{ozon,wb,yandex}/`), которые будут портированы. Есть 3 npx MCP-сервера (базовые), которые будут заменены одним кастомным.

**Стек**: Python + FastMCP 3.x + uv workspace + Pydantic V2
**Репо**: github.com/DmitriyMutagen/mcp-servers (новый)

---

## Phase 1: Инициализация проекта (Foundation)

### 1.1 Git + GitHub
- `git init` в `/Users/Dmitrij/Documents/mcp servers/`
- Создать `.gitignore` (Python, .env, __pycache__, .venv, *.egg-info, .ruff_cache, .pytest_cache)
- Создать GitHub repo `mcp-servers` через `gh repo create`
- Настроить remote origin

### 1.2 Структура monorepo
```
mcp-servers/
├── .github/workflows/ci.yml
├── .gitignore
├── .env.example
├── .env                          # gitignored
├── CLAUDE.md                     # Инструкции для Claude Code
├── pyproject.toml                # Root workspace config
├── libs/
│   └── shared/
│       ├── pyproject.toml
│       └── src/mcp_shared/
│           ├── __init__.py
│           ├── http_client.py    # Base async httpx + retry + circuit breaker
│           ├── logging.py        # stderr-only logging
│           └── config.py         # Pydantic Settings base
├── servers/
│   ├── marketplace-api/          # ПЕРВЫЙ СЕРВЕР
│   │   ├── pyproject.toml
│   │   └── src/marketplace_api/
│   │       ├── __init__.py
│   │       ├── server.py         # FastMCP entry point
│   │       ├── config.py         # Marketplace credentials
│   │       ├── clients/          # HTTP клиенты (порт из MarketAI)
│   │       │   ├── __init__.py
│   │       │   ├── ozon.py
│   │       │   ├── wb.py
│   │       │   └── yandex.py
│   │       ├── tools/            # MCP tools (46 штук)
│   │       │   ├── __init__.py
│   │       │   ├── ozon_products.py
│   │       │   ├── ozon_orders.py
│   │       │   ├── ozon_stocks.py
│   │       │   ├── ozon_prices.py
│   │       │   ├── ozon_reviews.py
│   │       │   ├── ozon_analytics.py
│   │       │   ├── wb_products.py
│   │       │   ├── wb_orders.py
│   │       │   ├── wb_stocks.py
│   │       │   ├── wb_prices.py
│   │       │   ├── wb_reviews.py
│   │       │   ├── wb_analytics.py
│   │       │   ├── ym_products.py
│   │       │   ├── ym_orders.py
│   │       │   ├── ym_stocks.py
│   │       │   ├── ym_reviews.py
│   │       │   └── ym_analytics.py
│   │       └── resources/        # API docs как MCP resources
│   │           ├── __init__.py
│   │           └── api_docs.py
│   ├── content-factory/          # SLOT (future)
│   │   └── .gitkeep
│   ├── analytics/                # SLOT (future)
│   │   └── .gitkeep
│   └── n8n-workflows/            # SLOT (future)
│       └── .gitkeep
├── scripts/
│   ├── dev.sh                    # Запуск в dev-режиме
│   └── register.sh               # Вывод JSON для settings.json
└── tests/
    ├── conftest.py
    └── test_marketplace_api/
        ├── test_ozon_tools.py
        ├── test_wb_tools.py
        └── test_ym_tools.py
```

### 1.3 Root pyproject.toml
```toml
[project]
name = "mcp-servers"
version = "0.1.0"
requires-python = ">=3.11"

[tool.uv.workspace]
members = ["libs/*", "servers/*"]

[dependency-groups]
dev = ["pytest>=8.0", "pytest-asyncio>=0.24", "ruff>=0.9"]
```

### 1.4 CLAUDE.md для проекта
- Правила разработки MCP серверов
- STDIO: никогда print/console.log в stdout
- Нейминг tools: `{marketplace}_{noun}_{verb}`
- Max 50 tools на сервер
- Pydantic Field(description=...) на каждом параметре

---

## Phase 2: Shared Library (libs/shared)

### 2.1 Портировать из MarketAI
- **Источник**: `~/Documents/marketai/marketai/src/connectors/`
- `http_client.py` — базовый async httpx клиент с retry (tenacity), exponential backoff
- `logging.py` — stderr-only logger (logging.basicConfig(stream=sys.stderr))
- `config.py` — BaseSettings с env_file поддержкой

### 2.2 Зависимости libs/shared
```
httpx>=0.28
tenacity>=9.0
pydantic>=2.10
pydantic-settings>=2.7
```

---

## Phase 3: Marketplace API Server

### 3.1 Портировать клиенты
**Источники**:
- `~/Documents/marketai/marketai/src/connectors/ozon/client.py` → `clients/ozon.py`
- `~/Documents/marketai/marketai/src/connectors/wb/client.py` → `clients/wb.py`
- `~/Documents/marketai/marketai/src/connectors/yandex/client.py` → `clients/yandex.py`

Адаптация: заменить imports на mcp_shared, убрать зависимости от MarketAI

### 3.2 Config (Pydantic Settings)
```python
class Settings(BaseSettings):
    ozon_client_id: str = ""
    ozon_api_key: str = ""
    wb_api_token: str = ""
    wb_seller_id: str = "544455"
    ym_oauth_token: str = ""
    ym_campaign_id: str = ""
    ym_business_id: str = "35517383"
    model_config = {"env_file": ".env", "extra": "ignore"}
```

### 3.3 Server entry point (FastMCP)
```python
mcp = FastMCP("marketplace-api", version="0.1.0")
# Register tools from each module
# mcp.run(transport="stdio")
```

### 3.4 Tools (46 штук, до лимита 50)

**Ozon (17)**: products_list, product_get, product_update, orders_list, order_get, stocks_get, stocks_update, prices_get, prices_update, reviews_list, review_reply, questions_list, question_reply, chats_list, chat_history, chat_send, analytics_get

**Wildberries (16)**: cards_list, card_get, card_update, orders_list, order_get, stocks_get, stocks_update, prices_get, prices_update, feedbacks_list, feedback_reply, questions_list, question_reply, chats_list, chat_messages, analytics_get

**Yandex Market (13)**: offers_list, offer_cards_get, offer_update, orders_list, order_get, stocks_get, stocks_update, reviews_list, review_reply, questions_list, question_reply, chats_list, chat_send

### 3.5 Паттерн регистрации tools
```python
# tools/ozon_products.py
def register(mcp: FastMCP, client: OzonClient):
    @mcp.tool()
    async def ozon_products_list(limit: int = 100, last_id: str = "") -> str:
        """List Ozon products with cursor pagination..."""
        return json.dumps(await client.list_products(limit, last_id))
```

### 3.6 Зависимости marketplace-api
```
fastmcp>=3.1
mcp-shared  # workspace
```

---

## Phase 4: Регистрация и тестирование

### 4.1 Регистрация в Claude Code
Добавить в `~/.claude/settings.json` → `mcpServers`:
```json
"marketplace-api": {
    "command": "uv",
    "args": ["run", "--project", "/Users/Dmitrij/Documents/mcp servers/servers/marketplace-api", "python", "-m", "marketplace_api.server"],
    "env": { "OZON_CLIENT_ID": "2003894", ... }
}
```

### 4.2 .env.example
```
OZON_CLIENT_ID=
OZON_API_KEY=
WB_API_TOKEN=
WB_SELLER_ID=544455
YM_OAUTH_TOKEN=
YM_CAMPAIGN_ID=
YM_BUSINESS_ID=
```

### 4.3 Smoke test
- `uv run --project servers/marketplace-api python -m marketplace_api.server` — должен запуститься без ошибок
- MCP Inspector: `npx @modelcontextprotocol/inspector`
- В Claude Code: проверить что 46 tools видны

---

## Phase 5: GitHub

### 5.1 Создание репо
```bash
gh repo create DmitriyMutagen/mcp-servers --private --source .
git add . && git commit -m "init: MCP servers monorepo with marketplace-api"
git push -u origin main
```

### 5.2 CI (GitHub Actions)
- Lint (ruff check + ruff format --check)
- Tests (pytest)
- На push в main и PRs

---

## Порядок реализации (Step by Step)

1. **git init + .gitignore + root pyproject.toml** — каркас monorepo
2. **libs/shared/** — базовые утилиты (logging, http_client, config)
3. **servers/marketplace-api/pyproject.toml + config.py + server.py** — скелет сервера
4. **clients/{ozon,wb,yandex}.py** — порт HTTP клиентов из MarketAI
5. **tools/** — реализация 46 инструментов (Ozon → WB → YM)
6. **resources/api_docs.py** — API документация как ресурсы
7. **CLAUDE.md + .env.example** — документация проекта
8. **Регистрация в settings.json** — подключение к Claude Code
9. **tests/** — базовые тесты
10. **GitHub repo + push** — финал

## Verification

- `uv sync` без ошибок
- `uv run ruff check .` — 0 ошибок
- `uv run pytest` — тесты проходят
- Сервер запускается: `uv run --project servers/marketplace-api python -m marketplace_api.server`
- В Claude Code видны все 46 tools
- Вызов `ozon_products_list` возвращает данные
