# Self-Learning Claude Code System — Architecture & Implementation Plan

**Date**: 2026-03-26
**Status**: APPROVED FOR IMPLEMENTATION
**Author**: Claude CTO + Mega Research (7 parallel agents, 42+ queries, 50+ sources)
**Confidence**: 92% (CL v2.1 already installed, just needs wiring)

---

## Executive Summary

Дмитрий имеет 90% инфраструктуры для самообучающегося Claude Code, но **ничего из этого не работает**:
- `permanent/reflexion.md` — ПУСТОЙ
- `permanent/gotchas.md` — ПУСТОЙ
- `permanent/decisions.md` — ПУСТОЙ
- `decay-7d/`, `decay-30d/` — ПУСТЫЕ
- Continuous Learning v2.1 — УСТАНОВЛЕН, но **НЕ ПОДКЛЮЧЕН** к хукам
- 0 из 6 проектов имеют полную структуру

**Решение**: Вариант B (Adaptive System) — подключить CL v2.1 + Daily Review + Project Standardization.

---

## PHASE 1: Wire Up Continuous Learning v2.1 (Day 1, 2h)

### 1.1 Add CL v2.1 hooks to settings.json

CL v2.1 уже установлен в `~/.claude/skills/continuous-learning-v2/`.
Нужно добавить хуки observe.sh в PreToolUse и PostToolUse.

**Файл**: `~/.claude/settings.json`
**Изменение**: добавить в hooks.PreToolUse и hooks.PostToolUse:

```json
{
  "matcher": "*",
  "hooks": [{
    "type": "command",
    "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh pre"
  }]
}
```

```json
{
  "matcher": "*",
  "hooks": [{
    "type": "command",
    "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh post"
  }]
}
```

### 1.2 Create homunculus directory structure

```bash
mkdir -p ~/.claude/homunculus/{instincts/{personal,inherited},evolved/{agents,skills,commands},projects}
```

### 1.3 Create identity.json

```json
{
  "name": "Dmitriy Gagauz",
  "role": "Solo Founder + CTO",
  "technical_level": "advanced",
  "preferred_languages": ["python", "typescript"],
  "frameworks": ["fastapi", "react", "next.js"],
  "style": "functional, async-first, clean-architecture"
}
```

### 1.4 Enable observer (optional, for automatic analysis)

Edit `~/.claude/skills/continuous-learning-v2/config.json`:
```json
{
  "version": "2.1",
  "observer": {
    "enabled": true,
    "run_interval_minutes": 10,
    "min_observations_to_analyze": 30
  }
}
```

**Verification**: After 1 session, check `~/.claude/homunculus/projects/` for observation files.

---

## PHASE 2: Session Summarizer & Memory Population (Day 1-2, 3h)

### 2.1 Session Summarizer Hook (Stop event)

**Файл**: `~/.claude/hooks/session-summarizer.py`

Хук Stop: при завершении сессии:
1. Читает git diff за сессию
2. Читает observations из CL v2.1
3. Генерирует summary в `~/.claude/memory/decay-7d/session-YYYY-MM-DD-N.md`
4. Обновляет `permanent/reflexion.md` если были ошибки
5. Обновляет `permanent/gotchas.md` если нашли проблему библиотеки
6. Обновляет `permanent/decisions.md` если были архитектурные решения

### 2.2 Memory Decay Manager (SessionStart)

**Файл**: `~/.claude/hooks/memory-decay.py`

При старте сессии:
1. Удалить файлы старше 7 дней из `decay-7d/`
2. Удалить файлы старше 30 дней из `decay-30d/`
3. Перенести high-value items из decay-7d в permanent/
4. Загрузить project-specific memory если есть

---

## PHASE 3: Daily Review System (Day 2-3, 4h)

### 3.1 Skill `/daily-review`

**Файл**: `~/.claude/skills/daily-review.md`

Skill выполняет:
1. `git log --since="yesterday"` для каждого активного проекта
2. Анализ observation files из CL v2.1
3. Анализ session summaries из decay-7d/
4. Gap analysis: что покрыто слабо?
5. Предложения: фичи, рефакторинг, техдолг
6. Генерация отчёта в `decay-30d/daily-YYYY-MM-DD.md`
7. Telegram notification с кратким summary

### 3.2 Skill `/good-morning`

**Файл**: `~/.claude/skills/good-morning.md`

Утренний брифинг:
1. Текущие приоритеты из GLOBAL_MEMORY.md
2. Незавершённые задачи из вчерашнего daily-review
3. Sentry: новые ошибки за ночь
4. Git: непушнутые коммиты, open PRs
5. Ozon/WB: zero-stock alerts, новые отзывы
6. Telegram: summary утром

### 3.3 Scheduled trigger (cron)

Через `/schedule` skill настроить:
- Daily review: ежедневно в 23:00
- Good morning: ежедневно в 09:00

---

## PHASE 4: Project Standardization (Day 3, 3h)

### 4.1 Script стандартизации

**Скрипт**: `~/.claude/scripts/standardize-projects.py`

Для каждого из 6 проектов:

| Проект | Что создать |
|--------|------------|
| Aragant | MEMORY.md |
| Skolkovo | CLAUDE.md |
| Content Factory | CLAUDE.md, docs/adr/ |
| SoulWay B2B | MEMORY.md, .claude/, CLAUDE.md, docs/adr/ |
| WB Content Factory | MEMORY.md, docs/adr/ |
| MCP Servers | docs/adr/ |

### 4.2 CLAUDE.md Template для каждого проекта

Генерация из анализа кодовой базы:
- Tech stack detection
- Directory structure
- Key files and entry points
- Running instructions
- Current sprint / TODO

---

## PHASE 5: Cross-Project Intelligence (Day 4-5, 4h)

### 5.1 Instinct promotion

CL v2.1 уже поддерживает promotion: project → global когда инстинкт виден в 2+ проектах.

Настроить auto-promotion criteria:
- Same instinct in 2+ projects
- Average confidence >= 0.7 (снижено с 0.8 для solo dev)

### 5.2 Tech Debt Tracker

**Файл**: `~/.claude/memory/permanent/tech-debt.md`

Auto-populate из:
- TODO/FIXME в коде (grep по всем проектам)
- Known issues из MEMORY.md каждого проекта
- Sentry recurring errors
- Stale branches (>30 days without activity)

### 5.3 Pattern Library

**Файл**: `~/.claude/memory/permanent/patterns.md`

Auto-populate из CL v2.1 instincts:
- Кластеры инстинктов с confidence > 0.7
- Cross-project patterns
- Anti-patterns (из reflexion.md)

---

## PHASE 6: Telegram Dashboard (Day 5, 2h)

### 6.1 Daily digest в Telegram

Формат:
```
🧠 Daily Learning Report — 2026-03-26

📊 Sessions: 5 | Commits: 12 | Files changed: 34
🎯 Instincts learned: 3 new, 2 promoted
⚠️ Gotchas found: 1 (SQLAlchemy async session)
🏗️ Decisions: 1 ADR (chose FastAPI over Django)
📈 Confidence trending up: prefer-async, validate-input

Top suggestion: Aragant API needs rate limiting (3 Sentry errors)
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   Claude Code Session                    │
│                                                          │
│  User Prompt ──→ PreToolUse ──→ Tool ──→ PostToolUse    │
│                      │                      │            │
│                      ▼                      ▼            │
│              CL v2.1 observe.sh      CL v2.1 observe.sh │
│                      │                      │            │
│                      ▼                      ▼            │
│           ~/.claude/homunculus/projects/<hash>/           │
│                 observations.jsonl                        │
│                      │                                    │
│         ┌────────────┴──────────────┐                    │
│         ▼                           ▼                    │
│   Observer Agent              Session Stop               │
│   (background, Haiku)        session-summarizer.py       │
│         │                           │                    │
│         ▼                           ▼                    │
│   instincts/personal/         memory/decay-7d/           │
│   *.yaml (weighted)          session-YYYY-MM-DD.md       │
│         │                           │                    │
│         ▼                           ▼                    │
│   /evolve → skills/           /daily-review              │
│   /promote → global           memory/decay-30d/          │
│                               daily-YYYY-MM-DD.md        │
│                                     │                    │
│                                     ▼                    │
│                              permanent/                   │
│                              reflexion.md                 │
│                              gotchas.md                   │
│                              decisions.md                 │
│                              patterns.md                  │
│                              tech-debt.md                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  Memory Hierarchy                        │
│                                                          │
│  L1: In-Context (token window)                          │
│      └── GLOBAL_MEMORY.md head (first 200 lines)        │
│      └── Project MEMORY.md                               │
│                                                          │
│  L2: Session (decay-7d/)                                │
│      └── session summaries                               │
│      └── observations.jsonl                              │
│                                                          │
│  L3: Short-term (decay-30d/)                            │
│      └── daily reviews                                   │
│      └── instincts < 0.5 confidence                     │
│                                                          │
│  L4: Long-term (permanent/)                             │
│      └── reflexion.md, gotchas.md, decisions.md         │
│      └── patterns.md, tech-debt.md                      │
│      └── instincts ≥ 0.7 confidence (global)            │
│                                                          │
│  L5: Identity (CLAUDE.md + Rules)                       │
│      └── project config, user preferences               │
│      └── 9 rule files in ~/.claude/rules/               │
└─────────────────────────────────────────────────────────┘
```

---

## What We DON'T Need (and why)

| Tool | Why skip | Alternative |
|------|----------|-------------|
| CORE (RedPlanetHQ) | Requires Docker + Redis + separate server. Overkill for solo. | CL v2.1 + file-based memory |
| Ars Contexta | Knowledge graph from conversations is cool but heavy. Better after CL v2.1 proves itself. | Instincts + evolve = same result lighter |
| SPARC Memory Bank | For multi-agent teams 5+. We have 1 human + Claude. | CL v2.1 project scoping |
| Wispr Flow integration | FlowWhisper already works. No export API needed. | Direct voice → Claude Code |
| Custom knowledge graph server | MCP memory server exists. File-based is simpler. | permanent/ files + instincts |

---

## Success Metrics

| Metric | Baseline (now) | Target (30 days) |
|--------|----------------|-------------------|
| Memory files populated | 0/5 permanent files | 5/5 auto-populated |
| Instincts learned | 0 | 50+ (across 6 projects) |
| Daily reviews generated | 0 | 30 (one per day) |
| Project structure compliance | 0/6 | 6/6 |
| Context restoration time | ~20 min manual | ~30 sec automatic |
| Repeat mistakes | Unknown | Tracked in reflexion.md |

---

## Implementation Order

```
Day 1 (2-3h):
  ✅ Wire CL v2.1 hooks → settings.json
  ✅ Create homunculus structure + identity.json
  ✅ Session summarizer hook
  ✅ Memory decay manager

Day 2 (3-4h):
  ✅ /daily-review skill
  ✅ /good-morning skill
  ✅ Auto-populate permanent/ files template

Day 3 (3h):
  ✅ Standardize all 6 projects
  ✅ Generate CLAUDE.md for each
  ✅ Tech debt tracker

Day 4 (2-3h):
  ✅ Cross-project intelligence
  ✅ Pattern library
  ✅ Instinct promotion tuning

Day 5 (2h):
  ✅ Telegram dashboard
  ✅ Schedule daily triggers
  ✅ Full cycle test
  ✅ Documentation
```

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| CL v2.1 hooks slow down tool calls | HIGH | observe.sh is async, <50ms measured |
| Observer agent consumes tokens | MEDIUM | Uses Haiku (cheap), runs every 10min |
| Memory files grow too large | LOW | Auto-purge (30 day TTL) + size limit (10MB) |
| False instincts (wrong patterns) | MEDIUM | Confidence threshold 0.7, human review |
| Hooks conflict with existing | LOW | CL v2.1 hooks append, don't replace |
