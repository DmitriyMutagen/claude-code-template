# Plan: Finish Claude Code Setup — 3 Remaining Tasks

## Context
Максимизация Claude Code: установлены все плагины, 2400 скиллов, 18 MCP серверов, 12 агентов, 5 команд, camoufox + browser-use + playwright-extra. Осталось 3 финишных задачи оптимизации.

## Task 1: Pre-cache npm MCP packages
**Цель**: Первый запуск MCP сервера с ~30s → ~2s
**Действие**: `npx -y <package> --help` для всех npm MCP серверов из settings.json
**Пакеты** (8 штук):
- `@modelcontextprotocol/server-filesystem`
- `@modelcontextprotocol/server-memory`
- `@modelcontextprotocol/server-sequential-thinking`
- `@modelcontextprotocol/server-github`
- `@modelcontextprotocol/server-puppeteer`
- `@playwright/mcp`
- `@browsermcp/mcp@latest`
- `mcp-server-docker`

## Task 2: Add ~/.npm-global to PATH
**Цель**: playwright-extra + stealth доступны глобально
**Файл**: `~/.zshrc` или `~/.bash_profile`
**Строка**: `export NODE_PATH="$HOME/.npm-global/lib/node_modules:$NODE_PATH"`

## Task 3: Final verification + summary
**Действия**:
- `ls ~/.claude/agents/` → 12 файлов
- `ls ~/.claude/commands/` → 5 файлов
- `jq . ~/.claude/settings.json` → valid JSON, 18 MCP серверов
- Сводный отчёт пользователю

## Verification
После всех 3 задач:
- `node -e "require('@playwright/mcp')"` → без ошибки (пакет закэширован)
- `echo $NODE_PATH` → содержит `~/.npm-global/lib/node_modules`
- Все агенты/команды/серверы на месте
