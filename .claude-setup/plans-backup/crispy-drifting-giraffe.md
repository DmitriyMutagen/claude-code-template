# Plan: CTO-Level Infrastructure — COMPLETE 10 Layers + Global + Template

## Context
Полная имплементация документа «Архитектура и экосистема ИИ-разработки на базе Claude Code: Практики уровня CTO (2026)». Все 10 слоёв, все инструменты, все паттерны. Глобально для ВСЕХ проектов + готовый шаблон.

---

## PHASE 0: INSTALL ALL TOOLS (Global, one-time)

| Tool | Install | Source |
|------|---------|--------|
| SuperClaude v4.3.0 | `pipx install superclaude && superclaude install` | PyPI / GitHub SuperClaude-Org |
| cc-sdd | `gh repo clone gotalab/cc-sdd ~/.claude/plugins/cc-sdd` | GitHub gotalab/cc-sdd |
| parry-guard | `gh repo clone vaporif/parry-guard ~/.claude/plugins/parry-guard` | GitHub vaporif/parry-guard |
| Dippy + Parable | `gh repo clone ldayton/Dippy ~/.claude/plugins/dippy` | GitHub ldayton/Dippy |
| vexp MCP | Install from vexp.dev (MCP server for AST memory) | vexp.dev |
| obra/superpowers | Already installed (3164 skills, 111K stars) | GitHub obra/superpowers |

Verification: `superclaude doctor`, check `/sc:*` commands, check skill list

---

## PHASE 1: GLOBAL HOOKS (settings.json — ALL projects)

### 1.1 Skills Auto-Activation (UserPromptSubmit) — CRITICAL
**Без этого skills игнорируются в ~90% случаев!**

Script `~/.claude/hooks/skill-auto-activate.py`:
1. Парсит промпт пользователя ($CLAUDE_PROMPT)
2. Матчит ключевые слова → релевантные skills
3. Возвращает через stdout: "SKILL ACTIVATION — Use /superpowers:brainstorming before planning"
4. Claude видит напоминание ПЕРЕД ответом

Keyword mapping:
- "plan/design/architect" → `/superpowers:brainstorming` + `/superpowers:writing-plans`
- "test/tdd/coverage" → `/superpowers:test-driven-development`
- "bug/fix/error" → `/superpowers:systematic-debugging`
- "review/pr" → `/superpowers:requesting-code-review`
- "spec/requirements" → `/kiro:spec-requirements`
- "branch/feature" → `/superpowers:using-git-worktrees`
- "deploy/release" → `/superpowers:verification-before-completion`
- "refactor" → `/superpowers:subagent-driven-development`

### 1.2 Quality Sentinel (Stop Event)
Script `~/.claude/hooks/quality-sentinel.sh`:
1. `git diff --name-only` — список изменённых файлов
2. Ищет рискованные паттерны:
   - `try.*except` без логирования → "Добавь Sentry.captureException()?"
   - Raw SQL → "Используешь параметризованные запросы?"
   - `async def` без `await` → "Нет await — синхронный вызов?"
   - `os.environ` → "Секреты через .env?"
3. Если есть `.py` файлы → `pytest -x -q 2>&1 | head -20`
4. Если fail → возвращает ошибку, блокирует завершение

### 1.3 Parry Security (PreToolUse + PostToolUse)
- Блокировка чтения: `.env`, `credentials`, `*.key`, `*.pem`
- Сканирование output: base64-encoded secrets, curl to external
- Tainted data tagging при парсинге внешних файлов

### 1.4 Dippy Permission (PreToolUse → Bash)
- Auto-approve: `ls`, `cat`, `grep`, `git log`, `pytest`, `ruff`, `pip list`
- Block + prompt: `rm`, `git push --force`, `curl > file`, `chmod`, `kill`
- Parse through Parable AST: `ls | grep foo` → safe (read-only pipeline)

### 1.5 Session Handoff (Stop Event)
Auto-save `.claude/session-handoff.md` при завершении

### 1.6 SubagentStop Hook
Валидация output субагентов перед принятием результатов

---

## PHASE 2: ALL BEHAVIORAL PATTERNS (Global ~/.claude/CLAUDE.md)

### 2.1 Confidence Check
- >90% → execute
- 70-89% → show 2-3 alternatives with pros/cons
- <70% → STOP, ask human
- ROI: 200 tokens saves 50,000

### 2.2 Self-Check
- After each architectural block → verify vs requirements
- Run lint + type check automatically
- Check security rules

### 2.3 Reflexion (Cross-session learning)
- Log errors, hallucinations, failed approaches → `.claude/memory/permanent/reflexion.md`
- Next session reads these → avoids known failures
- Auto-update on repeated errors

### 2.4 ALL 9 Cognitive Personas
| Flag | Focus |
|------|-------|
| --architect | System abstractions, scaling, contracts, microservices |
| --security | OWASP, injections, leaks, authorization |
| --performance | Profiling, cache, N+1, indexes |
| --frontend | UI/UX, components, accessibility |
| --backend | APIs, DB, queues, services |
| --data | Analytics, pipelines, ETL |
| --qa | Tests, coverage, edge cases |
| --devops | Docker, CI/CD, monitoring, infra |
| --ml | Models, training, inference |

### 2.5 Wave → Checkpoint → Wave
- Wave 1: Parallel reads (10+ files simultaneously)
- Checkpoint: Consolidate, decide
- Wave 2: Parallel writes to independent modules
- 3.5x speedup vs sequential

### 2.6 Heavy Words
- "YAGNI", "KISS", "SOLID boundaries"
- "Clean Architecture dependency rule"
- "Idempotent UPSERT", "Tenacity retry + exponential backoff"
- "adhere to DRY", "respect bounded contexts"

---

## PHASE 3: WORKFLOWS (Global)

### 3.1 Anthropic Official: Explore → Plan → Code → Commit
1. **Explore** — "read files, DO NOT CODE" — Serena + Context7
2. **Plan** — Planning Mode (Shift+Tab×2), think/ultrathink, 2-3 alternatives
3. **Code** — fresh session with plan, 1-2 sections at a time, review between
4. **Commit** — Conventional Commits, PR, quality gates

### 3.2 SDD 10-Phase Pipeline (cc-sdd)
1. init → 2. explore → 3. propose → 4. spec → 5. design (parallel with spec) →
6. tasks → 7. apply → 8. review → 9. verify → 10. archive

5 Quality Gates between phases (human approval + auto-tests + spec compliance)

### 3.3 Superpowers Workflow (for complex features)
1. `/brainstorm` → Socratic questions, edge cases, trade-offs
2. `/writing-plans` → chunks of 2-5 min, each needs sign-off
3. `/using-git-worktrees` → isolated branch, clean baseline
4. `/test-driven-development` → tests FIRST, code ONLY when tests red
5. `/subagent-driven-development` → fresh subagent per task + double review
6. `/verification-before-completion` → self-validation before claiming done
7. `/finishing-a-development-branch` → checklist: docs, tests, review

---

## PHASE 4: MEMORY ARCHITECTURE (Global + Project)

### 4.1 Three-Layer Decay System
```
Layer 1: ~/.claude/CLAUDE.md                    # Global preferences (NOT in git)
Layer 2: /project/CLAUDE.md                     # Project context (in git, <200 lines)
Layer 3: /project/.claude/memory/               # Topic files (in git)
         ├── permanent/
         │   ├── decisions.md                    # ADR summary
         │   ├── architecture.md                 # Current architecture
         │   ├── api-patterns.md                 # API patterns
         │   ├── gotchas.md                      # Known traps
         │   └── reflexion.md                    # Failed approaches
         ├── decay-7d/
         │   └── progress.md                     # Current sprint
         └── decay-30d/
             └── context.md                      # Research results
```

### 4.2 vexp MCP (AST-graph memory)
- Tree-sitter AST parsing → dependency graph
- Observations linked to code nodes (functions, classes)
- Auto-tag `[STALE]` when signatures change
- 65-70% token savings
- Scoring: BM25 (35%) + TF-IDF cosine (25%) + time decay (20%) + graph proximity (15%) + structural penalty (-30%)

### 4.3 CLAUDE.md Rules
- MAX 200 lines (index, not inline)
- NO @-file imports (they embed full text every prompt)
- Use references to topic files instead

---

## PHASE 5: SUBAGENT ORCHESTRATION

### 5.1 Clone Pattern
- Task() isolates context, spawns fresh clone
- Only minimal data passed to subagent
- Simple > complex multi-agent swarms

### 5.2 Agent Profiles (create in ~/.claude/agents/ for global, .claude/agents/ for project)
- solution-architect.md — ADR + plans ONLY, no code tools
- fullstack-developer.md — implement by spec
- qa-engineer.md — E2E tests, coverage
- security-auditor.md — OWASP audit
- devops-engineer.md — Docker, CI/CD

### 5.3 Model Routing
- Coordinator: Opus (strategy, architecture)
- Subagents: Sonnet/Haiku (implementation, routine)
- 3-5x API cost savings

---

## PHASE 6: OBSERVABILITY

### 6.1 Sentry (already configured)
- `/seer "top errors in last 24 hours"`
- Before fix: `list_issues` → After deploy: check new errors
- `analyze_issue_with_seer` for complex bugs

### 6.2 Future: Laminar/SigNoz/PostHog for LLM tracing

---

## PHASE 7: MCP STRATEGY

### 7.1 Rule: MAX 3-5 powerful gateways (not API mirrors)
### 7.2 Scripting Model
- BAD: 50 individual CRUD tools (read_user, update_order)
- GOOD: powerful gateways (execute_code, download_data, take_action)
- MCP handles auth + security, Claude scripts against data

### 7.3 Current stack (already configured)
1. Context7 — library docs
2. Serena — semantic code navigation
3. Playwright — browser automation
4. marketplace-api — unified 3-marketplace gateway (47 tools)
5. science-api — PubMed/USDA/OpenFDA
6. + vexp (ADD: AST memory)

---

## PHASE 8: ANTI-PATTERNS (document in global CLAUDE.md)

| Anti-pattern | Why dangerous | Solution |
|---|---|---|
| Vibe coding without spec | Tech debt exponential | cc-sdd + SDD workflow |
| >20k tokens on MCP | Destroys useful context | Max 3-5 powerful gateways |
| Auto-formatting hooks | 160k tokens per 3 rounds | Format in CI/CD, not Claude |
| RAG for code search | Hidden failures, fragile | ripgrep/Serena instead |
| Complex multi-agent systems | Debugging exponentially harder | Clone Pattern, simple Task() |
| Let context hit limit | Quality degrades | Clear at 30-50% |
| @-file imports in CLAUDE.md | Embeds full file every prompt | References instead |
| No observability | Blind to errors | Sentry + OTel from day 1 |

---

## PHASE 9: PROJECT TEMPLATE (~/Documents/project-template/)

Full ready-to-use template for ANY new project:

```
~/Documents/project-template/
├── .claude/
│   ├── agents/                          # 5 agent profiles
│   │   ├── solution-architect.md
│   │   ├── fullstack-developer.md
│   │   ├── qa-engineer.md
│   │   ├── security-auditor.md
│   │   └── devops-engineer.md
│   ├── memory/
│   │   ├── permanent/                   # decisions, gotchas, reflexion
│   │   ├── decay-7d/
│   │   └── decay-30d/
│   ├── architecture/                    # dependency-rules, behavioral-patterns
│   └── hooks/                           # quality-sentinel, skill-auto-activate
├── .mcp.json                            # serena + sentry + vexp
├── .pre-commit-config.yaml              # ruff + ast-grep + secrets
├── .serena/project.yml
├── .github/workflows/                   # test + lint + security
├── docs/
│   ├── todo/                            # Active specs
│   ├── done/                            # Completed specs
│   ├── specs/SPEC_TEMPLATE.md
│   ├── adr/ADR_TEMPLATE.md
│   └── artifacts/plans/ + logs/
├── src/                                 # Clean Architecture layers
│   ├── api/          (Presentation)
│   ├── services/     (Application)
│   ├── domain/       (Domain)
│   └── infrastructure/
├── tests/
├── CLAUDE.md                            # <200 lines, index format
├── AGENTS.md
├── mission.md                           # Business mission (edit per project)
├── MEMORY.md
├── .env.example
├── .gitignore
└── pyproject.toml
```

Usage: `cp -r ~/Documents/project-template/ ~/Documents/my-new-project/`

---

## PHASE 10: APPLY TO MARKETAI

1. Create MarketAI-specific agent profiles
2. Setup memory decay structure for MarketAI
3. Create ADR-001 (LLM Provider: Polza.ai), ADR-002 (Async SQLAlchemy), ADR-003 (Per-rating auto-reply)
4. Move existing plans to docs/todo/ or docs/done/
5. Create docs/artifacts/ for plans/logs
6. Fix MCP credentials (USDA, OpenFDA, Semantic Scholar)
7. Create mission.md for MarketAI
8. Create CI/CD workflows

---

## MASTER CHECKLIST (from document)

- [ ] 1. Clean Architecture boilerplate with CLAUDE.md
- [ ] 2. SuperClaude Framework installed (`pipx install superclaude`)
- [ ] 3. obra/superpowers installed (20+ skills)
- [ ] 4. cc-sdd installed (SDD workflow + Project Memory)
- [ ] 5. Memory: .claude/memory/ (decisions, architecture, gotchas, reflexion)
- [ ] 6. Hooks: Skills Auto-Activation + Quality Sentinel + Parry + Dippy
- [ ] 7. Subagents: architect + qa + fullstack in .claude/agents/
- [ ] 8. MCP: Context7 + Serena + Playwright + vexp (max 3-5)
- [ ] 9. Sentry: setup from first deploy
- [ ] 10. OTel: SigNoz or PostHog for LLM tracing (future)
- [ ] 11. Docs structure: docs/todo + docs/done pattern
- [ ] 12. First feature — ONLY through /brainstorm → /writing-plans → TDD
- [ ] 13. Project template created in ~/Documents/project-template/

---

## Verification

```bash
# Tools installed
superclaude doctor
ls ~/.claude/plugins/{cc-sdd,parry-guard,dippy}

# Hooks configured
python3 -c "import json; d=json.load(open('$HOME/.claude/settings.json')); print(json.dumps(d.get('hooks',{}), indent=2))"

# Template exists
ls ~/Documents/project-template/{CLAUDE.md,.claude/agents,.mcp.json,docs/adr,docs/todo}

# Skills work
# Test: type "plan a new feature" → should see skill activation reminder

# Tests pass
cd /Users/Dmitrij/Documents/marketai/marketai && pytest tests/ -x -q
```
