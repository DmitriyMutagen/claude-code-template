---
name: improver
description: Meta-agent that analyzes system patterns, lessons, and instincts to suggest upgrades. Run weekly or after major milestones. Proposes rule/skill/hook improvements.
---

# /improver --- System Self-Improvement Agent

## When to Run
- Weekly (via /schedule or manually)
- After completing a major feature/project
- When feeling stuck or slow

## Process

### Step 1: Gather Evidence
Read these files:
1. ~/.claude/memory/permanent/reflexion.md --- past failures
2. ~/.claude/memory/permanent/gotchas.md --- framework traps
3. ~/.claude/memory/permanent/decisions.md --- architecture decisions
4. ~/.claude/memory/permanent/flowwhisper-analysis.md --- voice patterns
5. ~/.claude/homunculus/instincts/personal/*.yaml --- all instincts
6. ~/.claude/memory/decay-7d/session-*.md --- recent sessions
7. ~/.claude/memory/decay-30d/daily-*.md --- recent daily reviews
8. ~/.claude/gamification/gamify.db --- performance metrics

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
