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

## Custom MCP Servers (2026-03-28)

### Security Scanner MCP (бесплатный аналог Snyk)
- **Путь**: ~/Documents/mcp servers/security-scanner-mcp/
- **Файлы**: server.py, requirements.txt, README.md
- **6 tools**: scan_dependencies (pip-audit), scan_code_security (bandit), scan_secrets (detect-secrets), scan_docker (trivy), full_security_audit, check_requirements_vulnerabilities
- **Зависимости**: fastmcp>=3.0, pip-audit, bandit, detect-secrets (installed), trivy (brew install trivy)
- **Подключён**: ~/.claude/settings.json → security-scanner

### VPS Monitor MCP (бесплатный аналог Datadog)
- **Путь**: ~/Documents/mcp servers/servers/vps-monitor/
- **Файлы**: src/vps_monitor/ (server.py, ssh.py, settings.py, fmt.py, tools/*.py)
- **8 tools**: check_server_health, check_docker_containers, check_nginx_status, check_postgres, check_disk_usage, check_logs, check_security, full_server_report
- **Зависимости**: fastmcp>=3.1, paramiko>=3.4, pydantic-settings>=2.0
- **SSH**: root@94.198.219.232 (key: ~/.ssh/id_ed25519)
- **Подключён**: ~/.claude/settings.json → vps-monitor

### Исследование платных MCP (2026-03-27)
- TestSprite ($19-69/мес) — AI тестирование, ВЕРДИКТ: НЕ СТОИТ (false positives, cloud-only, сырой)
- Snyk ($25/мес) — security, ВЕРДИКТ: заменён Security Scanner MCP (бесплатно)
- Datadog ($15/мес) — monitoring, ВЕРДИКТ: заменён VPS Monitor MCP (бесплатно)
- Composio (free) — 850+ интеграций, ВЕРДИКТ: пока не нужен (13 MCP уже покрывают)
- **Вывод**: платные MCP = 5-15% удобства за $50-300/мес, не оправдано

### Рекомендованные бесплатные инструменты
- pip-audit — уязвимости Python deps (CVE)
- bandit — SAST для Python
- detect-secrets — утечки ключей в коде
- trivy — Docker/IaC/deps scanning
- semgrep — pattern-based SAST
- Uptime Kuma — мониторинг доступности (docker)

## Session History
- 2026-03-27: Mega session — infra bugs fixed, testing strategy deployed
- 2026-03-28: Deep research платных MCP + build Security Scanner MCP + VPS Monitor MCP

## Skolkovo Deep Audit (2026-03-28)
- 10 агентов параллельно: backend, frontend, tests, production, product, live walkthrough, business logic, CTO 7-zone, infra doctor, SEO
- 150 запланированных фич найдено, сверено с реальностью
- Scoreboard: 24/35 (69%) — продвинутый прототип
- 15 ночных задач настроены в night-queue.json
- Skolkovo добавлен в sleepless config
- Full audit: ~/Documents/skolkovo/docs/FULL_AUDIT_2026-03-28.md

## Changelog
- 2026-03-27: feat: elite-prompts v2 + infra-doctor v2 + cheatsheet HTML + checkpoint
- 2026-03-28: feat: 2 custom MCP servers (security-scanner + vps-monitor) built and connected
- 2026-03-28: audit: Skolkovo 360° audit (10 agents) + 15 night tasks configured
- 2026-03-28: MEGA NIGHT: 16 modules built for Skolkovo — auth, 6 science DBs, MCP server, labels, billing, compliance checker, reverse engineering, real company data import. 16 branches ready to merge.
