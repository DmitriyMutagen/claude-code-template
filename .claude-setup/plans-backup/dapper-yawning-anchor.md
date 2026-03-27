# План: Ultimate Power-User Claude Code Setup для /ассистент

## Контекст

Директория `/Users/Dmitrij/Documents/ассистент/` — пустая, новая. Цель: настроить её как
флагманское рабочее пространство для разработки сложных проектов в режиме code-cowork.
Глобально уже есть 14 плагинов (playwright, firecrawl, github, context7, qodo, notion и др.),
2000+ скиллов, прав доступа достаточно. Нужно добавить: CLAUDE.md, агентов, MCP-серверы,
хуки, структуру проекта, git.

---

## Что создаём (10 файлов + git init)

### 1. `/Users/Dmitrij/Documents/ассистент/CLAUDE.md`
Мастер-конфиг (~250 строк). Разделы:
- **Identity**: старший AI-коворкер, автономный, действует без лишних переспросов
- **Workflow канон**: Think → Plan → Execute → Reflect
- **Tool priority**: Read>cat, Grep>grep, Edit>sed, Write>echo — всегда дедикейтед тулы
- **Параллелизм**: один message = несколько tool_calls если независимы
- **Multi-agent**: когда запускать фоновых агентов, когда worktree-изоляцию
- **Memory protocol**: читать MEMORY.md перед задачей, писать после
- **Git safety**: конкретные файлы, не `git add .`, heredoc commits, никогда --no-verify
- **Context management**: файлы >400 строк → рефактор; CLAUDE.md <300 строк
- **Браузер**: использовать playwright snapshot, не screenshot, для надёжных селекторов
- **Язык**: отвечать на языке пользователя (русский)
- **Стиль**: коротко, конкретно, без воды, без эмодзи

### 2. `/Users/Dmitrij/Documents/ассистент/AGENTS.md`
Правила для всех субагентов:
- Выбор модели: Opus 4.6 для архитектуры/сложного кода, Sonnet 4.6 для исполнения,
  Haiku 4.5 для простых задач/review
- Агент всегда читает CLAUDE.md и AGENTS.md первым делом
- Возвращает структурированный результат (что сделано, что не сделано, блокеры)
- Не коммитит без явной команды

### 3. `/Users/Dmitrij/Documents/ассистент/.claude/settings.local.json`
MCP серверы для этого проекта:
```json
{
  "mcpServers": {
    "agent-memory": {
      "type": "stdio",
      "command": "node",
      "args": ["/Users/Dmitrij/.agent/skills/skills/agent-memory/build/index.js"]
    },
    "sequential-thinking": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "fetch": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    }
  }
}
```
(serena добавим отдельно если потребуется — зависит от наличия авторизации)

### 4. `.claude/agents/researcher.md`
```yaml
---
name: researcher
description: Веб-исследование, поиск документации, анализ конкурентов
model: claude-sonnet-4-6
background: true
---
```
Инструкция: использует WebSearch + Context7 + Firecrawl, возвращает структурированный отчёт,
не модифицирует файлы.

### 5. `.claude/agents/browser-bot.md`
```yaml
---
name: browser-bot
description: Браузерная автоматизация, скрапинг, UI-тестирование
model: claude-sonnet-4-6
background: true
---
```
Инструкция: приоритет `preview_snapshot` над screenshot, явно проверяет результат каждого
действия, не принимает cookies/permissions без указания.

### 6. `.claude/agents/parallel-coder.md`
```yaml
---
name: parallel-coder
description: Параллельная реализация фич, рефакторинг, изолированно от основной ветки
model: claude-sonnet-4-6
background: true
isolation: worktree
---
```
Инструкция: работает в worktree, не мержит сам, возвращает diff + описание изменений.

### 7. `.claude/agents/reviewer.md`
```yaml
---
name: reviewer
description: Code review, проверка безопасности, качества, OWASP
model: claude-haiku-4-5-20251001
background: true
isolation: worktree
---
```
Инструкция: проверяет OWASP Top 10, возвращает numbered list проблем с severity.

### 8. `.claude/launch.json`
Шаблоны dev-серверов для типичных проектов:
```json
{
  "version": "0.0.1",
  "configurations": [
    { "name": "FastAPI", "runtimeExecutable": "uvicorn", "runtimeArgs": ["main:app", "--reload"], "port": 8000 },
    { "name": "Next.js", "runtimeExecutable": "npm", "runtimeArgs": ["run", "dev"], "port": 3000 },
    { "name": "Telegram Bot", "runtimeExecutable": "python", "runtimeArgs": ["bot.py"], "port": 8080 }
  ]
}
```

### 9. `/Users/Dmitrij/Documents/ассистент/.gitignore`
Стандартный: .env*, __pycache__, node_modules, .venv, *.pyc, .DS_Store, dist/, build/,
.claude/worktrees/, secrets/

### 10. Инициализация git + начальный коммит
```bash
git init
git branch -M main
git add CLAUDE.md AGENTS.md .gitignore .claude/
git commit -m "chore: init power-user claude code workspace"
```

### 11. `/Users/Dmitrij/.claude/projects/-Users-Dmitrij-Documents----------/memory/MEMORY.md`
Создать файл памяти для проекта с:
- Путь к проекту ассистент
- Список активных MCP-серверов
- Паттерны агентной работы
- Список наиболее полезных скиллов для этого воркспейса

---

## Структура директорий после выполнения

```
/Users/Dmitrij/Documents/ассистент/
├── CLAUDE.md                    # мастер-конфиг ≤250 строк
├── AGENTS.md                    # правила для субагентов
├── .gitignore
├── .claude/
│   ├── settings.local.json      # MCP серверы
│   ├── launch.json              # dev servers
│   └── agents/
│       ├── researcher.md        # фоновый исследователь
│       ├── browser-bot.md       # браузерная автоматизация
│       ├── parallel-coder.md    # параллельный кодер (worktree)
│       └── reviewer.md          # code reviewer (worktree, haiku)
└── .git/
```

---

## Порядок выполнения

1. Создать `.gitignore` и `git init`
2. Создать `.claude/settings.local.json` (MCP)
3. Создать `.claude/launch.json`
4. Создать 4 агента в `.claude/agents/`
5. Создать `AGENTS.md`
6. Создать `CLAUDE.md` (самый важный файл)
7. Создать/обновить `MEMORY.md` для проекта
8. `git add` + первый коммит

---

## Верификация

После выполнения:
1. `cat CLAUDE.md` — убедиться что ≤250 строк, все разделы есть
2. `ls .claude/agents/` — 4 агента на месте
3. Запустить новую сессию Claude Code в этой директории — должны появиться MCP tools
   (agent-memory, sequential-thinking, fetch) в Tool Use
4. Тест агента: `/researcher` или явный Agent tool с `subagent_type: researcher`
5. Тест браузера: playwright snapshot через browser-bot
