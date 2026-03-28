# MarketAI Enterprise Development Stack

> Полный справочник инструментов, подходов и инфраструктуры для enterprise-уровня разработки в одиночку.
> Применимо к любому сложному проекту. Проверено на 102K+ строк кода.

---

## 1. AI-агент: Claude Code (Opus 4.6)

**Роль**: Главный AI-агент для разработки, рефакторинга, архитектуры, дебага.

| Параметр | Значение |
|----------|---------|
| Модель | Claude Opus 4.6 (1M контекст) |
| Среда | VS Code Extension + Terminal |
| Контекст | 1M токенов (самый большой на рынке) |
| Режимы | Plan Mode, Agent Teams, Background agents |

**Ключевые файлы конфигурации**:
- `CLAUDE.md` — инструкции для AI в корне проекта
- `.claude/settings.json` — пермишены, хуки, MCP серверы
- `.claude/agents/` — кастомные суб-агенты
- `.claude/plans/` — файлы планов

**Best practice (по Boris Cherny, создатель Claude Code)**:
- 5 параллельных сессий в терминале
- Opus с thinking для всего (меньше руления = быстрее)
- CLAUDE.md обновлять при каждой ошибке Claude
- PostToolUse хук для автоформатирования

---

## 2. Serena MCP — Семантическая навигация по коду

**Роль**: LSP-сервер через MCP, даёт AI понимание кода на уровне AST (не текстовый поиск).

| Параметр | Значение |
|----------|---------|
| Версия | 0.1.4 |
| Языки | Python + TypeScript |
| Backend | LSP (Language Server Protocol) |
| Проекты | marketai, content_factory, soulway-b2b |

**Конфигурация**:
- `~/.serena/serena_config.yml` — глобальные настройки + список проектов
- `.serena/project.yml` — настройки проекта (языки, таймауты)
- `.serena/memories/` — онбординг-память проекта

**Ключевые инструменты Serena**:
```
find_symbol          — поиск класса/функции по имени (AST)
find_referencing_symbols — все места использования символа
get_symbols_overview — обзор классов/функций файла
replace_symbol_body  — замена тела функции/класса
search_for_pattern   — regex-поиск по проекту
```

**Memory-файлы (записаны при онбординге)**:
| Файл | Содержимое |
|------|-----------|
| `project_overview` | Назначение, стек, архитектура |
| `suggested_commands` | Команды запуска, тестов, деплоя |
| `code_style` | Конвенции кодирования |
| `task_completion` | Чеклист завершения задачи |
| `codebase_structure` | Дерево проекта |
| `global/dmitrij_workflow` | Общие конвенции для всех проектов |

**Как подключить к новому проекту**:
```bash
# 1. Активировать проект
mcp__plugin_serena_serena__activate_project({project: "/path/to/project"})

# 2. Выполнить онбординг
mcp__plugin_serena_serena__onboarding()

# 3. Записать memory-файлы
mcp__plugin_serena_serena__write_memory({memory_name: "project_overview", content: "..."})
```

---

## 3. MCP-серверы маркетплейсов (810 инструментов)

**Роль**: Прямой доступ к API Ozon, Wildberries, Yandex Market из Claude Code.

| Группа | Серверы | Инструментов |
|--------|---------|-------------|
| Монолит | marketplace-api | 47 |
| Ozon | ozon-api, ozon-ads, ozon-logistics, ozon-operations, ozon-seller | 209 |
| WB | wb-api, wb-content, wb-ads, wb-analytics, wb-marketplace | 256 |
| YM | ym-api, ym-catalog, ym-analytics, ym-orders, ym-comms | 195 |
| MarketAI | marketai-db, science-api | 48 |
| Serena | plugin:serena | 27 |
| **ИТОГО** | **19 серверов** | **810+** |

**Конфигурация**: `.mcp.json` в корне проекта

---

## 4. Sentry — Мониторинг ошибок

**Роль**: Автоматический сбор ошибок, трейсов, профилей из продакшена.

| Параметр | Значение |
|----------|---------|
| SDK | sentry-sdk 2.54.0 |
| Интеграции | FastAPI, SQLAlchemy |
| Traces | 10% sampling |
| Profiling | 5% sampling |
| Тариф | Free (5K ошибок/мес) |

**Конфигурация**:
- `marketai/.env`: `SENTRY_DSN=https://...`
- `src/api/main.py:25-44`: инициализация SDK
- Дашборд: [aragant.sentry.io](https://aragant.sentry.io)

**Что даёт**:
- Автоматический сбор всех exceptions с контекстом
- Трейсы по запросам (где тормозит)
- Группировка ошибок по типу
- Алерты при новых ошибках
- Release tracking по версиям

---

## 5. ast-grep — Структурный поиск по коду

**Роль**: Поиск и замена кода по AST-паттернам, а не по тексту.

| Параметр | Значение |
|----------|---------|
| Версия | 0.42.0 |
| Установка | `brew install ast-grep` |
| Команда | `sg` |

**Примеры использования**:
```bash
# Найти все вызовы get_current_user
sg -p '$X.get_current_user' marketai/src/

# Найти все async def с декоратором @router
sg -p '@router.$METHOD($ARGS) async def $NAME($PARAMS):' marketai/src/

# Найти все httpx.AsyncClient() без timeout
sg -p 'httpx.AsyncClient()' marketai/src/
```

**Зачем**: grep ищет текст, ast-grep ищет структуру. На 100K+ строках разница критична.

---

## 6. Pre-commit хуки (ruff)

**Роль**: Автоматический линтинг и форматирование при каждом `git commit`.

| Параметр | Значение |
|----------|---------|
| ruff | v0.15.5 (линтер + форматтер) |
| pre-commit | v4.5.1 |
| Хуки | ruff (--fix) + ruff-format |

**Конфигурация**: `marketai/.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

**Что делает**: Каждый `git commit` автоматически:
1. Проверяет Python-код на ошибки (ruff lint)
2. Автоисправляет что может (--fix)
3. Форматирует код (ruff format)
4. Блокирует коммит если есть неисправимые проблемы

---

## 7. PostToolUse хук — Автоформатирование

**Роль**: После каждого Edit/Write от Claude Code автоматически запускается ruff format.

**Конфигурация**: `.claude/settings.json`
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "cd /path/to/project && python -m ruff format --quiet . 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

**Зачем**: Claude Code генерирует код, который не всегда отформатирован идеально. Хук фиксит это автоматически — по образцу Бориса Черни.

---

## 8. Суб-агенты (по паттерну Boris Cherny)

**Роль**: Специализированные AI-агенты для конкретных задач.

| Агент | Файл | Роль |
|-------|------|------|
| verify-app | `.claude/agents/verify-app.md` | E2E верификация (тесты, билд, импорты, миграции) |
| code-simplifier | `.claude/agents/code-simplifier.md` | Чистка кода после реализации |
| showrunner | `.claude/agents/showrunner.md` | Оркестратор команды агентов |
| python-developer | `.claude/agents/python-developer.md` | Backend FastAPI разработчик |
| frontend-engineer | `.claude/agents/frontend-engineer.md` | React/TypeScript разработчик |
| qa-tester | `.claude/agents/qa-tester.md` | QA тестирование |
| ai-engineer | `.claude/agents/ai-engineer.md` | AI pipeline, промпты, RAG |
| devops-engineer | `.claude/agents/devops-engineer.md` | Docker, деплой, мониторинг |

**Как вызвать**: Через Agent tool с `subagent_type` или через Agent Teams.

---

## 9. Основной Tech Stack проекта

### Backend
| Компонент | Технология | Версия |
|-----------|-----------|--------|
| API Framework | FastAPI | latest |
| ORM | SQLAlchemy 2.0 (async) | latest |
| Database | PostgreSQL 16 + pgvector | 16 |
| Cache/Queue | Redis 7 + Celery | 7 |
| Auth | JWT (python-jose) + bcrypt | - |
| Migrations | Alembic | latest |
| HTTP Client | httpx + aiohttp | - |
| Retry | tenacity | - |
| AI Models | OpenRouter + Anthropic + Local LLM | - |
| Science | BioPython (PubMed), USDA, OpenFDA | - |
| Payments | YooKassa | - |
| Monitoring | Sentry + Prometheus + Grafana | - |

### Frontend
| Компонент | Технология | Версия |
|-----------|-----------|--------|
| Framework | React | 19 |
| Build | Vite | 6 |
| UI Library | MUI (Material UI) | 6 |
| Language | TypeScript | 5.7 |
| Routing | react-router-dom | 7 |
| Charts | Recharts | 2.15 |
| HTTP | axios | 1.7 |
| E2E Tests | Playwright | 1.58 |

---

## 10. Паттерны разработки (лучшие практики 2026)

### Из сетапа Бориса Черни (создатель Claude Code)
1. **Параллельные сессии** — 5+ агентов одновременно
2. **Opus с thinking** для всех задач
3. **CLAUDE.md** обновлять при каждой ошибке
4. **PostToolUse хук** для автоформатирования
5. **verify-app** агент перед каждым шипом
6. **Sentry + Slack + BigQuery** через MCP

### Из курса IndyDevDan (Agentic Engineer)
1. **Planning-First** — агенты создают план ДО выполнения
2. **Closed Loop Prompts** — самокорректирующиеся системы
3. **ZTE (Zero-Touch Engineering)** — кодовая база шипит себя сама

### Из подхода Addy Osmani (Google Cloud AI)
1. **80% планирование, 20% выполнение**
2. **Agent Teams по слоям** — frontend, backend, тесты
3. **Competing hypotheses** — параллельный дебаг

### Из Anthropic 2026 Report
1. **Rakuten**: 12.5M строк, 99.9% точность за 7 часов
2. **Multi-agent** — норма, а не эксперимент
3. **60% работы** через AI, 0-20% полностью делегируемо

---

## 11. Быстрый старт для нового проекта

### Чеклист настройки инфраструктуры
```
1. [ ] Создать CLAUDE.md с описанием проекта, стека, конвенций
2. [ ] Активировать Serena: activate_project + onboarding + write_memory
3. [ ] Добавить .serena/project.yml с нужными языками
4. [ ] Скопировать суб-агенты в .claude/agents/ (verify-app, code-simplifier)
5. [ ] Настроить .claude/settings.json (пермишены, PostToolUse хук)
6. [ ] Добавить pre-commit с ruff: .pre-commit-config.yaml
7. [ ] Подключить Sentry (DSN в .env)
8. [ ] Установить ast-grep (brew install ast-grep)
9. [ ] Настроить MCP серверы в .mcp.json (если нужны внешние API)
10. [ ] Первый коммит с инфраструктурой
```

### Минимальный набор файлов
```
project/
├── CLAUDE.md                    # AI-инструкции
├── .claude/
│   ├── settings.json            # Пермишены + хуки
│   └── agents/
│       ├── verify-app.md        # Верификация
│       └── code-simplifier.md   # Чистка кода
├── .serena/
│   └── project.yml              # Serena конфиг (языки)
├── .pre-commit-config.yaml      # ruff lint + format
├── .mcp.json                    # MCP серверы (если нужны)
├── .env                         # Секреты (SENTRY_DSN, API keys)
└── .gitignore                   # .env, .venv, __pycache__
```

---

## 12. Источники и ссылки

| Ресурс | URL |
|--------|-----|
| Boris Cherny workflow | howborisusesclaudecode.com |
| IndyDevDan курсы | agenticengineer.com |
| Addy Osmani: Agent Teams | addyosmani.com/blog/claude-code-agent-teams/ |
| Anthropic 2026 Report | resources.anthropic.com/2026-agentic-coding-trends-report |
| Serena MCP | github.com/oraios/serena |
| ast-grep | ast-grep.github.io |
| ruff | docs.astral.sh/ruff |
| Sentry | docs.sentry.io |

---

*Документ создан: 2026-03-23 | MarketAI v1.7.0+ | 102K+ строк кода*
*Автор: Claude Code (Opus 4.6) для Дмитрия Гагауза (Aragant.group)*
