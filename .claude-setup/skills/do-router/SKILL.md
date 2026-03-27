---
name: do-router
description: >
  Universal task router. Classifies task complexity and routes to optimal
  execution tier. Use with any task — replaces manual skill selection.
tags:
  - routing
  - orchestration
  - meta
trigger: /do
---

# /do -- Universal Task Router

## How It Works

Every task enters through `/do`. The router classifies it by complexity and
routes execution through the optimal tier. No need to pick a skill manually --
`/do` handles that.

## Classification Algorithm

When a task arrives:

1. **Parse intent** -- what does the user actually want? (not literally, but the real goal)
2. **Estimate scope** -- how many files, how much time, how many moving parts?
3. **Check keywords** -- match against tier trigger words
4. **Assign tier** -- default to Tier 2 if ambiguous (most tasks are features)
5. **Announce** -- show tier, estimated time, plan summary
6. **Execute** -- follow tier-specific workflow

---

## Tier 1: Quick Fix

**Scope**: < 5 min, 1-2 files, no architectural impact

**Trigger keywords**: "fix", "поправь", "измени", "переименуй", "обнови значение",
typo, config tweak, one-liner, string change

**Workflow**:
1. Read the target file(s)
2. Make the change
3. Run lint/tests if available
4. Done

**Announce format**:
```
Tier 1: Quick Fix -- делаю сразу
```

**Rules applied**: data-correctness, result-verifier

---

## Tier 2: Feature

**Scope**: 5 min - 2 hours, 3-10 files, single feature or bugfix

**Trigger keywords**: "добавь", "создай", "сделай", "new endpoint", "new component",
"добавь фичу", "напиши функцию", "интегрируй"

**Workflow**:
1. Read MEMORY.md + project CLAUDE.md for context
2. Check Context7 for relevant library docs (never guess API)
3. Search for existing solutions (Exa/Brave) if non-trivial
4. Present 2-3 implementation variants with trade-offs (if > 30 min)
5. Get approval on approach
6. Implement with tests
7. Run lint + tests, verify result
8. Show what was done

**Announce format**:
```
Tier 2: Feature
Time: ~X min | Files: ~Y | Agents: Z
Plan: [one-line description]
Research: [what was checked -- Context7 / existing solutions]
Go?
```

**Rules applied**: research-before-code, think-ahead, data-correctness,
result-verifier, security-baseline

---

## Tier 3: Architecture

**Scope**: 2+ hours, 10+ files, new module or significant refactor

**Trigger keywords**: "спроектируй", "архитектура", "новый модуль", "переделай",
"redesign", "refactor all", "как архитектор", "migration"

**Workflow**:
1. **Deep Research** -- Exa/Brave for best practices, Context7 for library docs,
   check how industry leaders solve this
2. **Spec** -- write spec in `docs/plans/YYYY-MM-DD-{name}.md`
   - What and why
   - API contracts (endpoints, input/output)
   - Data model (schema, migrations)
   - Edge cases and non-requirements
3. **ADR** -- record architectural decision in `docs/adr/ADR-NNN-{name}.md`
4. **Variants** -- minimum 2 options with trade-offs table
5. **Get approval** -- do NOT write code until plan is confirmed
6. **Implement** -- break into tasks, execute sequentially or in parallel agents
7. **Test** -- unit + integration, run full suite
8. **Verify** -- check against Definition of Done from spec
9. **Checkpoint** -- update MEMORY.md, git commit

**Announce format**:
```
Tier 3: Architecture
Time: ~X h | Files: ~Y | Agents: Z x W waves
Steps: Spec -> ADR -> Approval -> Implementation -> Verification
Deep Research first.
Approve planning phase?
```

**Rules applied**: research-before-code, spec-first, think-ahead,
data-correctness, result-verifier, auto-coaching, security-baseline

---

## Tier 4: Campaign

**Scope**: multi-day, 50+ files, new project or platform-scale change

**Trigger keywords**: "новый проект", "платформа", "сервис с нуля", "MVP",
"build from scratch", "launch"

**Workflow**:
1. **Full Spec** -- architecture + data model + API contract + deployment plan
   - File: `docs/plans/campaign-{name}.md`
   - Includes: user stories, non-requirements, Definition of Done
2. **Architecture** -- C4 diagrams (Mermaid), module boundaries, data flow
3. **ADR** -- one per major technology/pattern choice
4. **Break into daily waves** -- each wave is self-contained and demoable
   - Wave = plan + implement + test + checkpoint
5. **Campaign tracker** -- progress file updated after each wave:
   ```
   ## Wave 1 (Day 1): Core models + DB
   - [x] Schema design
   - [x] Migrations
   - [x] Basic CRUD
   Status: DONE

   ## Wave 2 (Day 2): API layer
   - [ ] Endpoints
   - [ ] Auth
   Status: IN PROGRESS
   ```
6. **Daily review** -- what shipped, what blocked, what next
7. **Final verification** -- full test suite, security audit, deploy check

**Announce format**:
```
Tier 4: Campaign
Duration: ~X days | Waves: Y | Files: ~Z
Lifecycle: Spec -> Architecture -> Daily Waves -> Deploy
Campaign tracker for progress.
Start planning?
```

**Rules applied**: ALL rules -- research-before-code, spec-first, think-ahead,
data-correctness, result-verifier, auto-coaching, security-baseline

---

## Rules Matrix

| Rule                | T1 | T2 | T3 | T4 |
|---------------------|----|----|----|----|
| research-before-code|    | x  | x  | x  |
| spec-first          |    |    | x  | x  |
| think-ahead         |    | x  | x  | x  |
| data-correctness    | x  | x  | x  | x  |
| result-verifier     | x  | x  | x  | x  |
| auto-coaching       |    |    | x  | x  |
| security-baseline   |    | x  | x  | x  |
| adr-record          |    |    | x  | x  |
| campaign-tracker    |    |    |    | x  |

---

## Edge Cases

- **Ambiguous scope** -- default to Tier 2, upgrade if complexity reveals itself
- **Tier upgrade mid-task** -- if a Tier 2 task turns out to need architectural
  decisions, STOP, announce upgrade to Tier 3, write spec before continuing
- **Tier downgrade** -- if research shows the task is simpler than expected,
  announce downgrade and proceed faster
- **Multiple tasks in one message** -- classify each independently, execute
  Tier 1 items first, then address higher tiers
- **Voice input (FlowWhisper)** -- interpret intent, not literal words.
  "сделай чтоб работало" = find bug, understand cause, fix, verify

---

## Integration with CTO Layer

The `/do` router respects the CTO phases from CLAUDE.md:

| Tier | CTO Phases Applied          |
|------|-----------------------------|
| T1   | Phase 3 only (just do it)   |
| T2   | Phase 0 + 3 + 4             |
| T3   | Phase 0 + 1 + 2 + 3 + 4    |
| T4   | ALL phases, full lifecycle  |

Phase 0 (Understanding) always runs implicitly -- the router IS Phase 0.
