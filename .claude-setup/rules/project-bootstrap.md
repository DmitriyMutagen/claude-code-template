# Project Bootstrap — Standards for NEW Projects

## When `/new-project` is called, ALWAYS create:

### Directory Structure
```
project-root/
├── .claude/
│   └── CLAUDE.md          # Project-specific instructions
├── .serena/
│   └── project.yml        # Serena project config
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI pipeline
├── src/
│   ├── core/              # Business logic, domain
│   ├── api/               # HTTP endpoints (FastAPI/Next.js)
│   ├── connectors/        # External API integrations
│   ├── models/            # Data models (SQLAlchemy/Prisma)
│   └── utils/             # Shared utilities
├── tests/
│   ├── test_core/
│   ├── test_api/
│   └── conftest.py        # Shared fixtures
├── docs/
│   ├── adr/               # Architecture Decision Records
│   │   └── ADR_TEMPLATE.md
│   ├── plans/             # Active specs and plans
│   └── done/              # Completed specs (archive)
├── MEMORY.md              # Project memory for Claude
├── .env.example           # Documented env vars (no secrets)
├── .gitignore             # Language-specific + .env*
├── docker-compose.yml     # Local dev services
└── pyproject.toml         # or package.json
```

### Python Project (FastAPI)
```toml
# pyproject.toml essentials
[tool.ruff]
target-version = "py311"
line-length = 120

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### TypeScript Project (Next.js/React)
```json
// package.json essentials
{
  "scripts": {
    "dev": "next dev --turbopack",
    "build": "next build",
    "test": "vitest run",
    "lint": "next lint"
  }
}
```

### GitHub Actions CI Template
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: pytest tests/ -v --tb=short
```

### Project CLAUDE.md Template
```markdown
# [Project Name] — Claude Code Configuration

## Overview
[One-line: what this project does]

## Tech Stack
[Backend/Frontend/DB/AI specifics]

## Architecture
[Clean Architecture diagram or description]

## Key Directories
[src/api/, src/core/, etc. with what's in each]

## Running
[docker-compose up, pip install, npm install, etc.]

## Current Sprint
[What's being worked on NOW]

## Known Issues
[Active bugs, tech debt]
```

### Sentry Integration (from day 1)
- Create project in aragant org
- Add SENTRY_DSN to .env.example
- Install SDK (sentry-sdk for Python, @sentry/nextjs for JS)
- Configure release tracking
