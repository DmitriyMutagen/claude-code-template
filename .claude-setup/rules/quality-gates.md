# Quality Gates — Global Rules (ALL Projects)

## Pre-Code Checklist (before writing ANY code)
1. Read MEMORY.md — understand project context and past decisions
2. Check Sentry for active errors (org: aragant, region: de.sentry.io)
3. Run existing tests BEFORE making changes
4. Activate Serena project if not already done

## Code Quality Standards
- Python: strict type hints, async/await, SQLAlchemy 2.0 style
- TypeScript: strict mode, no `any`, proper interfaces
- External API calls: tenacity retry (3 attempts, exponential backoff)
- Timeouts: API 30s, AI 60s, DB 10s
- Avoid N+1: selectinload/joinedload
- UPSERT for idempotent sync
- Don't create httpx client per request — reuse

## Commit Standards
- Conventional Commits: feat/fix/refactor/docs/test/chore
- Co-authored-by for AI commits
- Never skip pre-commit hooks
- Never force-push to main/master

## Security Baseline (EVERY project)
- Secrets in .env only, never in code
- .env*.local in .gitignore
- Input validation on ALL user inputs (Pydantic/Zod)
- SQL parameterized queries only
- CORS whitelist, not wildcard
- Rate limiting on public endpoints
- JWT with proper expiration
- HTTPS only in production

## AI Code Review (CI)
- CodeRabbit Free on all GitHub repos
- Claude Code Action on PRs for critical projects
- Semgrep for SAST
- ruff + ast-grep in pre-commit

## Testing Requirements
- New feature = new tests (minimum)
- Bug fix = regression test FIRST (TDD Red-Green-Refactor)
- Critical paths: E2E with Playwright
- API endpoints: integration tests with httpx
- AI pipeline: output quality tests with scoring
