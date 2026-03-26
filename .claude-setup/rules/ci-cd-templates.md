# CI/CD Templates — Global Standards

## GitHub Actions: Python Backend (FastAPI)
```yaml
name: CI
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports: ['5432:5432']
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
      redis:
        image: redis:7
        ports: ['6379:6379']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Lint
        run: ruff check . --output-format=github
      - name: Security scan
        run: pip install semgrep && semgrep --config=auto --error src/
      - name: Tests
        run: pytest tests/ -v --tb=short --junitxml=test-results.xml
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: test-results.xml

  ai-review:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    permissions:
      pull-requests: write
      contents: read
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: |
            Review this PR. Focus on:
            - Security vulnerabilities (OWASP Top 10)
            - Clean Architecture boundary violations
            - Python async/await correctness
            - Missing error handling
            - Performance (N+1 queries, missing indexes)
            Rate overall quality 1-10.
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## GitHub Actions: TypeScript Frontend (Next.js/React)
```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check
      - run: npm run test -- --run
      - run: npm run build
```

## Deploy Script Pattern (deploy.py)
Every project should have a unified deploy script:
```python
#!/usr/bin/env python3
"""Unified deploy script. Usage: python deploy.py [staging|prod] [--rollback]"""
# 1. Run tests
# 2. Build
# 3. Deploy (Docker push / Vercel / rsync)
# 4. Health check
# 5. Notify Telegram
# 6. If health check fails → auto-rollback
```

## Pre-commit Config (.pre-commit-config.yaml)
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```
