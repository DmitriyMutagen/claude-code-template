---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

# Project Coding Standards

## Python
- Strict type hints everywhere
- async/await for I/O operations
- SQLAlchemy 2.0 style (select() not query())
- Pydantic for input/output validation
- tenacity retry for external API calls (3 attempts, exponential backoff)
- Timeouts: API 30s, AI 60s, DB 10s

## Testing
- pytest with asyncio_mode = "auto"
- New feature = new test (minimum)
- Bug fix = regression test FIRST (TDD)
- Use httpx.AsyncClient for API tests

## Error Handling
- Never bare except without logging
- Use Sentry for error tracking
- Parameterized SQL queries only
