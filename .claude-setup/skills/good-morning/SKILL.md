---
name: good-morning
description: Morning briefing — priorities, errors, alerts, plan for the day. Use at start of day or via scheduled task at 09:00.
---

# Good Morning Briefing

## When to Use
- Start of day
- Scheduled via /schedule at 09:00
- When saying "good morning" or "доброе утро"

## Process

### Step 1: Load Context
Read:
1. ~/.claude/memory/GLOBAL_MEMORY.md — current priorities
2. Latest daily review from ~/.claude/memory/decay-30d/
3. Latest session summaries from ~/.claude/memory/decay-7d/

### Step 2: Check for Issues
1. Git: check for unpushed commits across all 6 projects
2. Check if any projects have stale branches (>7 days)

### Step 3: Marketplace Alerts (if MCP available)
1. Ozon: zero-stock products
2. WB: unanswered reviews/questions
3. New negative reviews

### Step 4: Generate Briefing

```markdown
# Good Morning — YYYY-MM-DD

## Top 3 Priorities Today
1. [from GLOBAL_MEMORY priorities]
2. [from yesterday's daily review suggestions]
3. [from detected issues]

## Unfinished from Yesterday
- [items from previous session summaries]

## Issues Detected
- [unpushed commits]
- [stale branches]
- [marketplace alerts]

## Instinct Report
- Total instincts: N (N global, N project-scoped)
- Ready for /evolve: N
- Confidence trending up: [list]

## Suggested Plan
1. [actionable item]
2. [actionable item]
3. [actionable item]
```

### Step 5: Telegram Notification
Send briefing to Telegram (same method as daily-review).
