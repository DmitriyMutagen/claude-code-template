# 🧠 Глобальная память Дмитрий Гагауз
_Автообновляется. Git: github.com/DmitriyMutagen/claude-memory_

## 👤 Владелец
- **Имя**: Дмитрий Гагауз (Dmitrij)
- **Email**: gagauzdmitriy@gmail.com
- **Telegram**: @Dimavertut (ID: 926967075)
- **GitHub**: DmitriyMutagen
- **Роль**: Founder, CTO — Aragant.group / SoulWay

## 🏢 Активные проекты

| Проект | Путь | Статус | Последнее |
|--------|------|--------|-----------|
| MCP Servers | ~/Documents/mcp servers | 🟢 ACTIVE | 2026-03-24 — WB Oracle KB 16 JSON 276KB, 4 unpushed |
| SoulWay B2B Hub | ~/Documents/soulway-b2b | 🟢 ACTIVE | 2026-03-19 — 3D сайт, деплой Netlify |
| Aragant (ex-MarketAI) | ~/Documents/marketai/marketai | 🟢 READY TO DEPLOY | v1.8.0, rebrand done, 462K reviews, 102 tests, domains bought |
| B2B Outreach | ~/Documents/Orchestrator/b2b_outreach | 🟡 IN PROGRESS | frontend b2b-dashboard team |
| WB Content Factory | ~/Documents/агенты/wb_content_factory | 🟡 ACTIVE | генерация карточек WB |
| Bionovacia (Skolkovo) | ~/Documents/skolkovo | 🟡 IN PROGRESS | FastAPI+React+Neo4j, 68 тестов фиксятся |
| Bio-STM | bio-stm.ru | 🟡 ACTIVE | WP сайт, научные БАДы |
| Content Factory | ~/Documents/content_factory | 🟢 BUILT | Python, FastAPI :8100, LM Studio, WP+TG publishers |

## 🔑 Инфраструктура (обновлено 2026-03-26)
- **Production VPS**: 94.198.219.232 (SPB, 4CPU/8GB/80GB) — Aragant + Bionovacia + будущие проекты
- **VPN VPS**: 72.56.121.84 (DE, Frankfurt) — Amnezia VPN only
- **TimeWeb API**: account gy040287, token в Credentials.env
- **Deploy**: git push → GitHub Actions → SSH → docker compose (см. ~/.claude/rules/vps-deploy.md)
- **Aragant**: https://aragant.pro (SSL, nginx, Docker) — LIVE ✅
- **PostgreSQL**: localhost:5432 / b2b_intelligence (marketai:marketai)
- **Content Factory**: http://localhost:8100
- **Netlify**: soulway-b2b-hub.netlify.app
- **Claude Code**: v2.1.83
- **MCP серверов**: 9 глобальных
- **Агентов**: 20 активных

## 📋 Последние решения (ADR)

### 2026-03-27 — FULL ARCHITECT INFRASTRUCTURE DEPLOYED
- **Template**: github.com/DmitriyMutagen/claude-code-template (211 файлов, install.sh)
- **Result Verifier**: Stop hook блокирует "готово" без E2E/тестов
- **4 новых rules**: research-before-code, data-correctness, think-ahead, time-estimation
- **MCP Health Check**: 13/14 healthy при старте
- **Process Watchdog**: мониторинг zombie процессов
- **Auto-Checkpoint**: PreCompact → сохраняет перед потерей контекста
- **Mind Maps**: markmap.js HTML генератор (docs/maps/*.html)
- **Gamification v2**: 9 XP rules, 8 achievements, 3 weekly quests
- **FlowWhisper**: 1.25M символов → 15 instincts → permanent/flowwhisper-analysis.md
- **Checkpoint**: ~/.claude/checkpoints/2026-03-27-self-learning-infra.md

### 2026-03-26 — Self-Learning Claude Code System DEPLOYED
- **CL v2.1**: подключён к PreToolUse + PostToolUse hooks, 1569 observations
- **Homunculus**: ~/.claude/homunculus/ — identity.json, projects auto-detected
- **Session Summarizer**: Stop hook → decay-7d/session-YYYY-MM-DD-N.md + auto-populate permanent/
- **Memory Decay**: SessionStart hook → auto-cleanup 7d/30d + promotion
- **Skills**: /daily-review (вечерний обзор) + /good-morning (утренний брифинг)
- **Telegram**: notify script работает, отправляет в @Dimavertut
- **FlowWhisper**: 1.2M символов голосовых логов проанализированы для начальных instincts
- **Projects**: все 6 проектов стандартизированы (MEMORY.md + CLAUDE.md + docs/adr/)

### 2026-03-26 — Aragant DEPLOYED to production + Server migration
- **Aragant LIVE**: https://aragant.pro (SSL, HTTPS, Docker, 4 shops with API keys)
- VPS migrated: old broken (72.56.121.84) → new clean (94.198.219.232, SPB)
- Server hardened: SSH key+watchdog, fail2ban, UFW, QEMU agent, auto-updates
- Main server upgraded: 1CPU/2GB → 4CPU/8GB/80GB (preset 2455, 1800₽/мес)
- German server (72.56.121.84): kept for VPN Amnezia, downgrading to minimum
- CI/CD: GitHub Actions deploy.yml created (push → SSH → docker compose)
- Global deploy rules: ~/.claude/rules/vps-deploy.md (for ALL projects)
- Redis password fix: all connections use REDIS_PASSWORD env var
- Bionovacia also deployed on same server (:8002)
- 25+ frontend bugs fixed by parallel agent (8 commits)

### 2026-03-25 — Claude Code капитальная чистка
- Агенты: 162→20 (142 в ~/.claude/agents/archive/), с 1MB→62KB, ~10k tokens
- Обрезаны жирные агенты (security-auditor 9.5KB→600B, code-reviewer 8.4KB→640B, architect 6.3KB→823B)
- Удалены вредные хуки: auto-pytest на каждый Edit (30s), activity log, test warning
- Убран UserPromptSubmit skill-auto-activate (5s overhead)
- Permissions: убраны 30+ дублей mcp__* (mcp__* wildcard покрывает всё)
- Плагины: 15→6 (оставлены: context7, superpowers, playwright, firecrawl, github, notion)
- Claude Code обновлён 2.1.81→2.1.83
- additionalDirectories упрощены

### 2026-03-19 — Claude Code глобальная конфигурация
- Добавлено 28 глобальных env ключей в settings.json
- Brave Search MCP активирован
- Exa MCP переведён на HTTP transport (все 8 инструментов)

### 2026-03-18 — SoulWay B2B Hub
- Задеплоен на Netlify: soulway-b2b-hub.netlify.app
- Реальные данные API: 461 000+ отзывов, 797M₽ выручка Ozon 2025
- 3D Solar System сцена, 7 глав, React Three Fiber v9
- Bitrix24 интеграция (webhook: soulway.bitrix24.ru)

## 🎯 Текущие приоритеты
1. MCP Servers monorepo — WB Oracle Knowledge Base BUILD (16 JSON, 276KB) — IN PROGRESS
2. WB Oracle Tools Server — 40 tools (validators, calculators) — NEXT
3. Ozon: 52 zero-stock products + 10 neg reviews — URGENT
4. MarketAI sprint (Questions/Chats/AI Engine фиксы)
5. WB Content Factory pipeline
6. B2B Intelligence система

## 🧩 Паттерны работы
- Параллельные агенты для независимых задач
- Team mode для сложных спринтов (tmux backend)
- MEMORY.md в каждом проекте
- docs/plans/ для архитектурных решений
- Git всегда — каждый чекпоинт коммит

## 📁 Структура памяти
```
~/.claude/memory/
├── GLOBAL_MEMORY.md     ← этот файл (глобальный контекст)
├── projects/            ← per-project snapshot
│   ├── soulway-b2b.md
│   ├── marketai.md
│   └── b2b-outreach.md
├── plans/               ← активные планы
│   └── YYYY-MM-DD-*.md
└── decisions/           ← архитектурные решения (ADR)
    └── YYYY-MM-DD-*.md
```

## Auto-snapshot: 2026-03-20 21:50
Project: нэп
CWD: /Users/Dmitrij/Documents/нэп мп
Branch: main
Last commit: cced1f6 checkpoint: полная сессия

### Ключевые результаты сессии:
- Script ID: `1BxcOkqI6-51HrvPqVPfJVbf_Ic29ReGyYvmorUDUsqq9LVblNHmrkGPi` (ПРАВИЛЬНЫЙ!)
- Таблица: `1SbvrOUBrauS5e5Te1CWw3SxMB405nBv6jzrveoXTPu8` (ВБ Дубли НЭП основная)
- 7 листов заполнены с блочной структурой
- WB трафик: реальные данные через RU VLESS proxy
- Скилл "nep-table" создан для Ozon/YM
- Deploy: `/tmp/real_script/` → `clasp push` → `1BxcO...`

## Auto-snapshot: 2026-03-20 23:41
Project: нэп
Status: транскрибация 13/19, 6 тяжёлых видео осталось
Arsenal: 110 MCP, 445 agents, 610+ skills
Next: изучить ВСЕ транскрипции → план → антидубль-скрипт

## Auto-snapshot: 2026-03-24 (Session 3)
Project: mcp-servers (~/Documents/mcp servers)
Branch: main (4 unpushed: e6a9a60..743cae0)
Status: WB Oracle KB built — 16 JSON, 276KB, 2640 lines (was 11/80KB/1185)
Background: Whisper PID 63677 transcribing Эфир 5 (3h14m)
Videos: 5 downloaded to /tmp/oracle_videos/ (2.7GB)
Frames: 276 extracted to /tmp/oracle_frames/, 52 analyzed via Vision
Transcripts: 8 in docs/transcripts/ (558KB), 9th pending (Эфир 5)
Auth: YM ACMA token works (NOT y0__ OAuth for Market API!)
Next: check whisper → enrich ranking_logic.json → push → course digest → tools server

## 🎮 Gamification System v3.0 (2026-03-26 — АКТИВИРОВАН)
- **Engine**: `~/.claude/gamification/engine.py` — SQLite WAL, XP/levels/achievements/streaks
- **Config**: `~/.claude/gamification/config.json` — уровни, ачивки, квесты, проекты
- **Hooks** (подключены в settings.json):
  - `SessionStart` → `hooks/session_start.py` (баннер + snapshot XP)
  - `PostToolUse` (Write|Edit|MultiEdit|Bash|Task) → `hooks/post_tool_use.py` (XP трекинг)
  - `Stop` → `hooks/session_stop.py` (итоги сессии + Telegram)
- **Git hook**: `~/.claude/git-hooks/post-commit` (global core.hooksPath)
- **Dashboard**: `python3 ~/.claude/gamification/dashboard.py` или `/xp`
- **Daily digest**: launchd 09:00 → Telegram
- **Telegram**: уведомления об ачивках, level-up, итоги сессий
- **Текущий статус**: Level 3 ⚡ Mid Developer, 500+ XP, 3/18 ачивок, streak 1д
