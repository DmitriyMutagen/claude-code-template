---
name: improver
description: Мета-агент самоулучшения. Еженедельно анализирует систему, ищет топовые практики Top-0.1%, предлагает конкретные апгрейды. Запускай каждое воскресенье или когда хочешь апгрейд системы.
---

# /improver — Infinite Self-Improvement System

## What it does

Анализирует текущую систему и предлагает конкретные улучшения основанные на:
1. **Реальных практиках Top-100** мировых архитекторов/CTO/Founders
2. **Gaps** между текущим и элитным уровнем (project health scan)
3. **Новых инструментах** 2026 года
4. **Паттернах** которые не используются но должны быть

## Process

### Step 1: Gather Evidence (original)
Read these files:
1. ~/.claude/memory/permanent/reflexion.md — past failures
2. ~/.claude/memory/permanent/gotchas.md — framework traps
3. ~/.claude/memory/permanent/decisions.md — architecture decisions
4. ~/.claude/memory/permanent/flowwhisper-analysis.md — voice patterns
5. ~/.claude/homunculus/instincts/personal/*.yaml — all instincts
6. ~/.claude/memory/decay-7d/session-*.md — recent sessions
7. ~/.claude/memory/decay-30d/daily-*.md — recent daily reviews
8. ~/.claude/gamification/gamify.db — performance metrics

### Step 2: Analyze Patterns
- Which errors keep repeating? (reflexion.md)
- Which instincts have high confidence? (should become rules)
- Which metrics are Junior level? (growth areas)
- Which tools are underused? (MCP servers not called)
- Which rules are being ignored? (check session logs)

### Step 3: Generate Proposals
For each finding, create a proposal:

#### Proposal Format:
```
IMPROVEMENT PROPOSAL #N

Type: [rule | skill | hook | instinct | config]
Priority: [P0-critical | P1-high | P2-medium | P3-low]
Problem: [what's broken or slow]
Evidence: [data from Step 1]
Solution: [specific change to make]
File: [which file to create/modify]
Impact: [expected improvement]
```

### Step 4: Apply Approved Proposals
After approval:
- Create/update files
- Update GLOBAL_MEMORY with changes
- Commit to git
- Sync to template-project

### Step 5: Report
Save to ~/.claude/memory/decay-30d/improver-YYYY-MM-DD.md
Send summary to Telegram

---

## Auto-Evolution Engine (расширение)

Помимо анализа reflexion/instincts, запускает project scanner:

```bash
python3 ~/.claude/gamification/auto_evolution.py
```

### Project Health Scan
Сканирует все проекты на наличие:
- ADR docs (Martin Fowler standard)
- CI/CD GitHub Actions (Werner Vogels standard)
- Sentry integration (Google SRE standard)
- Tests directory (Kent Beck standard)
- /health endpoint (12-Factor App)
- Docker setup

### Top-100 Patterns Database
Встроенная база паттернов от:
- Alistair Cockburn (Hexagonal Architecture)
- Martin Fowler (Event Sourcing, CQRS, ADR)
- Eric Evans (DDD)
- Kent Beck (TDD)
- Werner Vogels (deploy daily)
- Google SRE Book (SLO, health checks)
- Pieter Levels (ship in 24h)
- DHH (revenue first)

### Output
- Project health matrix (таблица YES/no по каждому критерию)
- Top-3 priority gaps (с конкретными командами и временем)
- 3 новых паттерна для изучения (с XP за внедрение)
- Auto-upgrade suggestions
- JSON отчёт в evolution_reports/

## Commands

```bash
# Auto-Evolution Engine
python3 ~/.claude/gamification/auto_evolution.py

# Full improver via claude
/improver
```

## Automation

LaunchAgent (воскресенье 20:00):
```
~/Library/LaunchAgents/com.aragant.auto-evolution.plist
```

Проверить:
```bash
launchctl list | grep auto-evolution
```

## Related files

- `~/.claude/gamification/auto_evolution.py` — evolution engine
- `~/.claude/gamification/elite_benchmarks.json` — benchmarks
- `~/.claude/gamification/evolution_reports/` — report history
- `~/.claude/gamification/learning_coach.py` — skill tracking
- `~/Library/LaunchAgents/com.aragant.auto-evolution.plist` — schedule

## Principle

Every week +1 elite practice gets adopted into the system.
52 weeks = 52 elite practices. Compound effect.
