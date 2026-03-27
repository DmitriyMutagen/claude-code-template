# WB Content Factory — Глобальный План Развития

## Контекст

WB Content Factory — система генерации SEO-контента для маркетплейсов (WB, Ozon, Yandex Market).
**Текущее состояние:** 11,673 LOC, 28 модулей, 51 товар обработан из 175.
**Проблемы:** Dify Docker не запущен, Neo4j не развёрнут, LLM медленный (150-200с local), нет MCP серверов для автоматизации, скиллы не подключены.

**Цель плана:** Превратить проект в полностью автоматизированную фабрику контента с MCP серверами, AI-скиллами и интеграциями.

---

## Фаза 1: Permissions & Базовая настройка Claude Code

### 1.1 Убрать подтверждения (полный доступ)

**Файл:** `~/.claude/settings.json`
```json
{
  "skipDangerousModePermissionPrompt": true,
  "permissions": {
    "allow": [
      "Bash(python3 *)", "Bash(pip *)", "Bash(npm *)", "Bash(npx *)",
      "Bash(git *)", "Bash(docker *)", "Bash(docker-compose *)",
      "Bash(uvicorn *)", "Bash(pytest *)", "Bash(cd *)", "Bash(ls *)",
      "Bash(cat *)", "Bash(mkdir *)", "Bash(cp *)", "Bash(mv *)",
      "Bash(touch *)", "Bash(chmod *)", "Bash(curl *)", "Bash(wget *)",
      "Bash(which *)", "Bash(echo *)", "Bash(export *)", "Bash(source *)",
      "Bash(uv *)", "Bash(smithery *)",
      "Read", "Edit", "MultiEdit", "Write", "Glob", "Grep",
      "WebFetch", "WebSearch", "NotebookEdit"
    ],
    "deny": [
      "Bash(rm -rf /)", "Bash(sudo rm -rf *)", "Bash(format *)"
    ]
  }
}
```

**Команда запуска:**
```bash
claude --dangerously-skip-permissions
```

### 1.2 Project-level settings

**Файл:** `wb_content_factory/.claude/settings.json`
```json
{
  "permissions": {
    "allow": [
      "Bash(python3 -m src.*)",
      "Bash(python3 src/*)",
      "Bash(pytest *)",
      "Bash(pip install *)",
      "Bash(docker compose *)",
      "Read", "Edit", "Write", "Glob", "Grep"
    ]
  }
}
```

---

## Фаза 2: Установка MCP серверов из Smithery

### 2.1 Текущие MCP серверы (уже установлены)
- `n8n` — workflow automation
- `filesystem` — файловые операции
- `fetch` — HTTP запросы
- `sequential-thinking` — цепочки рассуждений
- `memory` — persistent memory
- `puppeteer` — browser automation
- `brave-search` — веб-поиск

### 2.2 Новые MCP серверы для установки

**Файл для обновления:** `wb_content_factory/.claude/settings.json` или `claude_mcp.json`

| # | Сервер | Команда установки | Зачем |
|---|--------|-------------------|-------|
| 1 | **Google Sheets MCP** | `npx @smithery/cli@latest install @smithery/google-sheets-mcp` | Прямая работа с таблицами продуктов/результатов |
| 2 | **Neo4j MCP** | `npx @smithery/cli@latest install neo4j-mcp-server` | Граф знаний товаров (2,505 узлов) |
| 3 | **Telegram MCP** | `npx @smithery/cli@latest install mcp-communicator-telegram` | Уведомления о batch processing |
| 4 | **Dify MCP** | `npx @smithery/cli@latest install dify-mcp-server` | RAG запросы к Knowledge Base |
| 5 | **PostgreSQL MCP** | `npx @smithery/cli@latest install @modelcontextprotocol/server-postgres` | Dify PostgreSQL backend |
| 6 | **Firecrawl MCP** | `npx @smithery/cli@latest install firecrawl-mcp` | Парсинг страниц конкурентов |
| 7 | **Exa Search MCP** | `npx @smithery/cli@latest install exa-mcp-server` | SEO-исследование ключевых слов |
| 8 | **Tavily MCP** | `npx @smithery/cli@latest install tavily-mcp` | Deep research для контента |

**Шаги:**
```bash
# Установка Smithery CLI
npm install -g @smithery/cli

# Интерактивная установка
npx @smithery/cli@latest setup

# Или ручная установка каждого:
npx @smithery/cli@latest install <server-name> --client claude
```

### 2.3 Обновлённый claude_mcp.json (целевая конфигурация)

Добавить в существующий `claude_mcp.json` новые серверы:
```json
{
  "google-sheets": {
    "command": "npx",
    "args": ["-y", "@smithery/google-sheets-mcp"],
    "env": { "GOOGLE_SERVICE_ACCOUNT_KEY": "<path>" }
  },
  "neo4j": {
    "command": "npx",
    "args": ["-y", "neo4j-mcp-server"],
    "env": { "NEO4J_URL": "bolt://localhost:7687", "NEO4J_USER": "neo4j", "NEO4J_PASSWORD": "<pwd>" }
  },
  "telegram": {
    "command": "npx",
    "args": ["-y", "mcp-communicator-telegram"],
    "env": { "TELEGRAM_BOT_TOKEN": "<token>" }
  },
  "dify": {
    "command": "npx",
    "args": ["-y", "dify-mcp-server"],
    "env": { "DIFY_API_URL": "http://localhost/v1", "DIFY_API_KEY": "<key>" }
  },
  "firecrawl": {
    "command": "npx",
    "args": ["-y", "firecrawl-mcp"],
    "env": { "FIRECRAWL_API_KEY": "<key>" }
  },
  "exa-search": {
    "command": "npx",
    "args": ["-y", "exa-mcp-server"],
    "env": { "EXA_API_KEY": "<key>" }
  }
}
```

---

## Фаза 3: Подключение AI-скиллов

### 3.1 Скиллы для копирования и адаптации

Источник: `/Users/Dmitrij/Documents/Orchestrator/агенты/skills/`
Назначение: `wb_content_factory/.claude/skills/`

**Tier 1 — Критические (подключить сразу):**

| # | Скилл | Источник | Адаптация для WB |
|---|-------|----------|-----------------|
| 1 | **n8n-content-factory** | `skills/n8n-content-factory/SKILL.md` | Переписать: Google Sheet → WB products, WordPress → Marketplace Cards |
| 2 | **copywriting** | `skills/copywriting/SKILL.md` | Добавить: WB-специфичные правила (8 блоков ТЗ, символьные лимиты) |
| 3 | **seo-content-writer** | `skills/seo-content-writer/SKILL.md` | Адаптировать: marketplace SEO (не web SEO), WB ранжирование |
| 4 | **seo-keyword-strategist** | `skills/seo-keyword-strategist/SKILL.md` | Переписать: Yandex Wordstat вместо Google, WB search queries |
| 5 | **rag-engineer** | `skills/rag-engineer/SKILL.md` | Настроить: Dify KB + chunking strategy для транскриптов |
| 6 | **programmatic-seo** | `skills/programmatic-seo/SKILL.md` | Применить: шаблонная генерация 175 SKU с SEO-оценкой |
| 7 | **marketing-psychology** | `skills/marketing-psychology/SKILL.md` | Использовать: JTBD-матрица, PLFS scoring для сегментов |

**Tier 2 — Важные (подключить после Tier 1):**

| # | Скилл | Зачем |
|---|-------|-------|
| 8 | **content-creator** | Brand voice Bionovacia + multi-format export |
| 9 | **googlesheets-automation** | Автоматизация Google Sheets через MCP |
| 10 | **russian-social-publisher** | Публикация в Telegram/VK/Дзен |
| 11 | **n8n-mcp-tools-expert** | Оркестрация n8n workflows |
| 12 | **seo-content-planner** | Контент-план на 175 SKU |
| 13 | **nano-banana-pro** | Генерация изображений для карточек |
| 14 | **seo-content-auditor** | QA-валидация контента |

**Tier 3 — Дополнительные:**

| # | Скилл | Зачем |
|---|-------|-------|
| 15 | **deep-research** | Исследование конкурентов |
| 16 | **seo-authority-builder** | E-E-A-T сигналы |
| 17 | **seo-meta-optimizer** | Meta-теги карточек |
| 18 | **architecture** | Документирование архитектуры |
| 19 | **docs-architect** | Dependency maps |
| 20 | **stitch-ui-design** | Визуальная карта данных |

### 3.2 Создание WB-специфичных скиллов (новые)

**Скилл 1: `wb-marketplace-expert`**
```
wb_content_factory/.claude/skills/wb-marketplace-expert/SKILL.md
```
Содержание: правила WB API, лимиты карточек, SEO-алгоритмы ранжирования, структура 8-блокового ТЗ, формат ContentBrief dataclass.

**Скилл 2: `wb-batch-orchestrator`**
```
wb_content_factory/.claude/skills/wb-batch-orchestrator/SKILL.md
```
Содержание: batch_runner.py логика, pause/resume флаги, Dify workflow integration, error handling patterns.

**Скилл 3: `wb-qa-reviewer`**
```
wb_content_factory/.claude/skills/wb-qa-reviewer/SKILL.md
```
Содержание: qa_reviewer.py правила, SEO-валидация, keyword stuffing detection, format compliance.

### 3.3 Структура директории скиллов

```
wb_content_factory/.claude/skills/
├── ai-engineer/SKILL.md            # (уже есть, обновить)
├── wb-marketplace-expert/SKILL.md   # НОВЫЙ
├── wb-batch-orchestrator/SKILL.md   # НОВЫЙ
├── wb-qa-reviewer/SKILL.md          # НОВЫЙ
├── copywriting/SKILL.md             # адаптированный
├── seo-content-writer/SKILL.md      # адаптированный
├── seo-keyword-strategist/SKILL.md  # адаптированный
├── rag-engineer/SKILL.md            # адаптированный
├── programmatic-seo/SKILL.md        # адаптированный
├── marketing-psychology/SKILL.md    # адаптированный
├── n8n-content-factory/SKILL.md     # адаптированный
├── content-creator/SKILL.md         # из skills/
├── googlesheets-automation/SKILL.md # из skills/
├── russian-social-publisher/SKILL.md # из skills/
├── n8n-mcp-tools-expert/SKILL.md    # из skills/
├── seo-content-planner/SKILL.md     # из skills/
├── nano-banana-pro/SKILL.md         # из skills/
└── seo-content-auditor/SKILL.md     # из skills/
```

---

## Фаза 4: Обновление ai-engineer скилла

**Файл:** `wb_content_factory/.claude/skills/ai-engineer/SKILL.md`

Обновить с учётом:
- Новых MCP серверов (Neo4j, Google Sheets, Telegram, Dify)
- Списка всех подключённых скиллов
- Текущего состояния проекта (51/175 товаров обработано)
- Инструкций по использованию каждого MCP сервера
- Обновлённого стека (Python 3.11+, новые зависимости)

---

## Фаза 5: Инфраструктурные исправления

### 5.1 Поднять Dify Docker
```bash
cd wb_content_factory && docker compose up -d
# Проверить: curl http://localhost/v1/workflows
```

### 5.2 Развернуть Neo4j
```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5
# Инициализировать схему: deploy/neo4j_schema_init.cypher
```

### 5.3 Обновить Python
```bash
# Проверить текущую версию, при необходимости обновить до 3.11+
python3 --version
# Пересоздать venv если нужно
```

---

## Фаза 6: Интеграция всего вместе

### 6.1 Обновить batch_runner.py
- Заменить LocalLLM → DifyWorkflow (через dify MCP или dify_pipeline.py)
- Добавить Telegram уведомления через MCP
- Добавить Google Sheets синхронизацию через MCP

### 6.2 Обновить pipeline.py
- Использовать Neo4j MCP для graph queries
- Использовать Google Sheets MCP для экспорта
- Добавить QA через wb-qa-reviewer скилл

### 6.3 Создать CLAUDE.md в корне проекта
Файл с инструкциями для Claude Code: какие скиллы использовать, какие MCP доступны, как запускать pipeline.

---

## Порядок выполнения

| Шаг | Действие | Время |
|-----|----------|-------|
| 1 | Настроить permissions (settings.json) | 2 мин |
| 2 | Установить MCP серверы через Smithery CLI | 10 мин |
| 3 | Обновить claude_mcp.json | 5 мин |
| 4 | Скопировать и адаптировать Tier 1 скиллы (7 шт) | 30 мин |
| 5 | Создать 3 новых WB-специфичных скилла | 20 мин |
| 6 | Обновить ai-engineer SKILL.md | 10 мин |
| 7 | Скопировать Tier 2 скиллы (7 шт) | 15 мин |
| 8 | Поднять Dify + Neo4j Docker | 10 мин |
| 9 | Создать CLAUDE.md | 5 мин |
| 10 | Интеграционное тестирование | 15 мин |

**Общее время:** ~2 часа

---

## Верификация

1. **MCP серверы:** `claude /mcp` — проверить все серверы активны
2. **Скиллы:** проверить что `.claude/skills/*/SKILL.md` все доступны
3. **Dify:** `curl http://localhost/v1/workflows` — ответ 200
4. **Neo4j:** `curl http://localhost:7474` — UI доступен
5. **Pipeline тест:** `python3 -m src.pipeline --sku 0` — один товар через полный цикл
6. **Batch тест:** `python3 -m src.batch_runner --pipeline local --limit 3` — 3 товара
7. **Google Sheets:** проверить что данные попали в таблицу
8. **Telegram:** проверить что уведомление пришло

---

## Ключевые файлы для модификации

- `~/.claude/settings.json` — global permissions
- `wb_content_factory/.claude/settings.json` — project permissions
- `claude_mcp.json` — MCP серверы
- `wb_content_factory/.claude/skills/ai-engineer/SKILL.md` — главный скилл
- `wb_content_factory/.claude/skills/` — 18 скиллов (7 адаптированных + 7 copied + 3 новых + 1 обновлённый)
- `wb_content_factory/CLAUDE.md` — инструкции проекта
- `wb_content_factory/src/batch_runner.py` — интеграция MCP
- `wb_content_factory/src/pipeline.py` — интеграция MCP
