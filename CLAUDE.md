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

## Architecture
Clean Architecture:
- `src/core/` — business logic, domain
- `src/api/` — HTTP endpoints
- `src/connectors/` — external API integrations
- `src/models/` — data models (SQLAlchemy)
- `src/utils/` — shared utilities

## Running
```bash
docker compose up -d          # start services
pip install -r requirements.txt  # local dev
pytest tests/ -v               # run tests
ruff check . --fix            # lint
```

## Current Sprint
[What's being worked on NOW]

## Known Issues
[Active bugs, tech debt]

## Self-Learning System
This project is connected to the self-learning system:
- CL v2.1 auto-captures observations via hooks
- Session summaries saved to ~/.claude/memory/decay-7d/
- /daily-review analyzes work patterns
- /good-morning provides morning briefing
