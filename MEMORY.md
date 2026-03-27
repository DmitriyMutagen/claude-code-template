# [PROJECT_NAME] — Memory

## Project State
- **Current phase**: Initial setup
- **Last completed**: Project scaffold
- **Next action**: Define requirements
- **Blockers**: None

## Key Facts
- Tech stack: [Python/TypeScript] + [FastAPI/Next.js]
- Database: PostgreSQL
- Deploy: Docker → VPS 94.198.219.232

## Lessons Learned
<!-- Updated automatically by session-summarizer hook -->
<!-- Format: YYYY-MM-DD | What happened | What we learned -->

## Testing Infrastructure (2026-03-27)
- Elite testing stack deployed: pytest + schemathesis + deepeval + hypothesis + respx
- 35 типов тестов проанализированы, 8 приоритетных выбраны для внедрения
- requirements-test.txt создан как шаблон для всех проектов
- pyproject.toml testing config добавлен во все проекты
- tests/ структура: unit/ integration/ e2e/ ai_quality/
- Deployment scripts: ~/.claude/deploy-testing.sh, ~/.claude/deploy-project-rules.sh
- PROMPT_TESTING_TZ.md — промпт для настройки тестов в каждом проекте
- /infra-doctor skill — CTO-level инфра аудит по цепочке

## Session History
- 2026-03-27: Mega session — infra bugs fixed, testing strategy deployed
