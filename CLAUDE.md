# [PROJECT_NAME] — Claude Code Configuration

## Overview
[One-line: what this project does and for whom]

## Tech Stack
- **Backend**: Python 3.11+ / FastAPI
- **Database**: PostgreSQL + SQLAlchemy 2.0 (async)
- **Cache**: Redis
- **AI**: OpenRouter / LM Studio (Qwen 2.5)
- **Deploy**: Docker → VPS (94.198.219.232)
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry (org: aragant)

## Architecture: Domain-Driven Modular Monolith

```
src/
  shared/              # Config, DB engine, auth, base models, exceptions
    config.py          # Pydantic Settings (from .env)
    database.py        # AsyncEngine + SessionLocal + Base
    auth.py            # JWT/OAuth middleware
    exceptions.py      # DomainError, NotFoundError, etc.

  {domain}/            # Each domain = self-contained vertical slice
    __init__.py        # Exports ONLY public API (contracts)
    contracts.py       # Protocol classes — PUBLIC interface
    models.py          # SQLAlchemy models for THIS domain
    schemas.py         # Pydantic DTOs (input/output)
    router.py          # FastAPI endpoints
    service.py         # Business logic
    repository.py      # DB queries (optional, for complex domains)
    tasks.py           # Background tasks (Celery/ARQ)
    tests/             # Tests for THIS domain
      test_service.py
      test_router.py
    CLAUDE.md          # Domain description for AI context

  main.py              # App factory — includes all domain routers
```

### Import Rules (BLOCKING)
- **ALLOWED**: `from src.shared.X` (shared → everyone)
- **ALLOWED**: `from src.{domain}.contracts` (through public interface)
- **FORBIDDEN**: `from src.{domain}.service` (direct internal import)
- **FORBIDDEN**: `from src.{domain}.models` (cross-domain model access)

### Adding a New Domain
1. Copy `src/example_domain/` → `src/{new_domain}/`
2. Update models, schemas, contracts, service, router
3. Add CLAUDE.md describing the domain
4. Include router in `src/main.py`
5. Ensure Sentry SDK is in entry points

## Mandatory Tools
- **Serena MCP**: navigation (find_symbol, find_referencing_symbols)
- **Sentry MCP**: monitoring (list_issues, get_issue_details)
- **Context7 MCP**: library docs before using any API

## Running
```bash
docker compose up -d           # start services
pip install -r requirements.txt  # local dev
pytest tests/ -v                # run tests (global)
pytest src/{domain}/tests/ -v   # run tests (single domain)
ruff check . --fix              # lint
```

## Key Commands
- `/modularize` — analyze and migrate to modular structure
- `/infra-doctor` — chain-thinking infrastructure audit
- `/verify` — real verification (not "should work")

## Current Sprint
[What's being worked on NOW]

## Known Issues
[Active bugs, tech debt]
