# Фикс MCP серверов: sentry + Kapture

## Context
При старте Claude Code появляются ошибки:
- "Could not attach to MCP server sentry" — пустой `SENTRY_AUTH_TOKEN`
- "Could not attach to MCP server Kapture Browser Automation" — плагин требует Chrome-расширение Kapture, которое не запущено

## Изменения в ~/.claude/settings.json

### 1. Sentry — удалить запись (нет токена, не используется)
Удалить блок `"sentry"` (строки 428–437):
```json
"sentry": {
  "command": "npx",
  "args": ["-y", "@sentry/mcp-server"],
  "env": { "SENTRY_AUTH_TOKEN": "" }
}
```

### 2. Kapture — отключить через disabledMcpjsonServers
Kapture идёт из плагина `claude-code-setup@claude-plugins-official`. Нужно добавить в корень settings.json:
```json
"disabledMcpjsonServers": ["Kapture Browser Automation"]
```

## Критические файлы
- `~/.claude/settings.json` — единственный файл для изменения

## Проверка
После перезапуска Claude Code ошибки должны исчезнуть.
Kapture можно включить обратно, установив расширение kapture.dev и убрав из disabledMcpjsonServers.
