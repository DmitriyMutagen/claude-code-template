---
name: daily-review
description: Analyze today's work across all projects, identify patterns, generate improvement suggestions. Use at end of day or via scheduled task.
---

# Daily Review

## When to Use
- End of day review
- Scheduled via /schedule at 23:00
- After completing a major feature

## Process

### Step 1: Collect Data
For each active project directory:
- ~/Documents/marketai/marketai
- ~/Documents/skolkovo
- ~/Documents/content_factory
- ~/Documents/soulway-b2b
- ~/Documents/агенты/wb_content_factory
- ~/Documents/mcp servers

Run:
1. `git log --since="today 00:00" --oneline` for commits today
2. `git diff --stat HEAD~10` for scope of changes
3. Check ~/.claude/memory/decay-7d/ for session summaries today

### Step 2: Analyze CL v2.1 Instincts
Read instincts from ~/.claude/homunculus/:
- Count new observations today
- List instincts with confidence changes
- Identify instincts ready for /evolve (confidence > 0.7)

### Step 3: Check Memory Health
- Are permanent/ files being populated?
- Are decay-7d/ sessions being written?
- Any gotchas or reflexions added today?

### Step 4: Generate Report
Save to ~/.claude/memory/decay-30d/daily-YYYY-MM-DD.md:

```markdown
# Daily Review — YYYY-MM-DD

## Summary
- Projects touched: N
- Commits: N
- Files changed: N
- Sessions: N
- Instincts learned: N

## Per-Project Activity
### [Project Name]
- Commits: [list]
- Key changes: [summary]

## Patterns Detected
- [pattern 1]
- [pattern 2]

## Suggestions for Tomorrow
1. [suggestion based on today's work]
2. [suggestion based on instincts]

## Tech Debt Discovered
- [if any TODO/FIXME found]

## Memory Health
- Reflexions: N entries
- Gotchas: N entries
- Decisions: N entries
```

### Step 5: Telegram Notification
Send summary to Telegram using:
```bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_USER_ID}" \
  -d "parse_mode=Markdown" \
  -d "text=<summary>"
```
