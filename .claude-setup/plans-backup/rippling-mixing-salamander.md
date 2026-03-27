# Plan: Add 5 global MCP servers to MarketAI project .mcp.json

## Context
MarketAI project `.mcp.json` at `/Users/Dmitrij/Documents/marketai/.mcp.json` has 24 servers but missing key global servers needed for current TODO tasks (browser QA, git push, docs lookup, notifications).

## Changes
**File:** `/Users/Dmitrij/Documents/marketai/.mcp.json`

Add 5 servers to `mcpServers` object:

1. **playwright-headed** — browser QA testing (TODO #1)
2. **context7** — library docs (React, FastAPI, MUI)
3. **telegram-notify** — human-in-the-loop notifications
4. **git** — git operations, push (TODO #4)
5. **github-mcp** — PR/issues management

Configs copied from `~/.claude/settings.json` global config.

## Verification
- JSON valid after edit (`python3 -c "import json; json.load(open('.mcp.json'))"`)
- Restart Claude Code session to pick up new servers
