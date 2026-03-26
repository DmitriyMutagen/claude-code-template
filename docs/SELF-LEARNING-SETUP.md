# Self-Learning Claude Code — Setup Guide

## What Was Built (2026-03-26)

Full self-learning system for Claude Code that accumulates knowledge across sessions.

## Components

### 1. Continuous Learning v2.1 (Instinct Engine)
- **Location**: `~/.claude/skills/continuous-learning-v2/`
- **Hooks**: PreToolUse + PostToolUse → observe.sh
- **Storage**: `~/.claude/homunculus/projects/<hash>/observations.jsonl`
- **Commands**: `/instinct-status`, `/evolve`, `/promote`, `/projects`
- **What it does**: Captures every tool call, detects patterns, creates weighted instincts

### 2. Session Summarizer
- **Location**: `~/.claude/hooks/session-summarizer.py`
- **Hook**: Stop event
- **Output**: `~/.claude/memory/decay-7d/session-YYYY-MM-DD-N.md`
- **Also updates**: `permanent/reflexion.md`, `permanent/decisions.md`
- **Speed**: 92ms

### 3. Memory Decay Manager
- **Location**: `~/.claude/hooks/memory-decay.py`
- **Hook**: SessionStart event
- **What it does**: Cleans files >7d from decay-7d/, >30d from decay-30d/
- **Output**: One-line status injected into session context

### 4. Daily Review Skill
- **Location**: `~/.claude/skills/daily-review/SKILL.md`
- **Usage**: `/daily-review` or schedule at 23:00
- **What it does**: Analyzes git activity, instincts, memory health across all projects

### 5. Good Morning Skill
- **Location**: `~/.claude/skills/good-morning/SKILL.md`
- **Usage**: `/good-morning` or schedule at 09:00
- **What it does**: Morning briefing with priorities, errors, marketplace alerts

### 6. Telegram Notify
- **Location**: `~/.claude/scripts/telegram-notify.py`
- **Usage**: `echo "msg" | python3 telegram-notify.py`
- **Requires**: TELEGRAM_BOT_TOKEN + TELEGRAM_USER_ID in env

## File Structure (Global)

```
~/.claude/
├── CLAUDE.md                          # Global instructions
├── settings.json                      # Hooks configuration
├── homunculus/                         # CL v2.1 data
│   ├── identity.json                  # Your profile
│   ├── projects.json                  # Project registry
│   ├── instincts/{personal,inherited} # Global instincts
│   ├── evolved/{agents,skills,commands}
│   └── projects/<hash>/              # Per-project data
│       ├── observations.jsonl         # Raw observations
│       ├── instincts/personal/        # Project instincts
│       └── evolved/                   # Project-evolved skills
├── memory/
│   ├── GLOBAL_MEMORY.md               # Cross-project context
│   ├── permanent/                     # Never expires
│   │   ├── reflexion.md               # Failures & lessons
│   │   ├── gotchas.md                 # Framework traps
│   │   ├── decisions.md               # Architecture decisions
│   │   └── flowwhisper-analysis.md    # Voice input patterns
│   ├── decay-7d/                      # Expires in 7 days
│   │   └── session-*.md               # Session summaries
│   ├── decay-30d/                     # Expires in 30 days
│   │   └── daily-*.md                 # Daily reviews
│   ├── projects/                      # Per-project snapshots
│   └── plans/                         # Active plans
├── hooks/
│   ├── session-summarizer.py          # Stop hook
│   ├── memory-decay.py                # SessionStart hook
│   ├── quality-sentinel.sh            # Stop hook (code quality)
│   └── skill-auto-activate.py         # UserPromptSubmit hook
├── scripts/
│   └── telegram-notify.py             # Telegram helper
├── skills/
│   ├── continuous-learning-v2/        # CL v2.1 engine
│   ├── daily-review/SKILL.md          # Evening review
│   └── good-morning/SKILL.md          # Morning briefing
└── rules/                             # Modular rules
    ├── ci-cd-templates.md
    ├── marketplace-ops.md
    ├── quality-gates.md
    └── ... (9 files)
```

## File Structure (Per Project)

```
project-root/
├── .claude/
│   └── rules/                         # Project-specific rules
├── CLAUDE.md                          # Project config for Claude
├── MEMORY.md                          # Project memory
├── .env.example                       # Documented env vars
├── .gitignore
├── docs/
│   ├── adr/                           # Architecture Decision Records
│   ├── plans/                         # Active specs
│   └── done/                          # Completed specs
├── src/
│   ├── core/                          # Business logic
│   ├── api/                           # HTTP endpoints
│   ├── connectors/                    # External APIs
│   ├── models/                        # Data models
│   └── utils/                         # Shared utilities
└── tests/
    ├── test_core/
    └── test_api/
```

## How to Deploy to New Project

```bash
# 1. Copy template
cp -r ~/Documents/template-project ~/Documents/new-project
cd ~/Documents/new-project

# 2. Replace placeholders
sed -i '' 's/\[PROJECT_NAME\]/MyProject/g' CLAUDE.md MEMORY.md

# 3. Init git
git init && git add . && git commit -m "feat: initial project scaffold"

# 4. CL v2.1 auto-detects on first Claude Code session
# (no manual setup needed — hooks are global)

# 5. Verify
# Next session should show observations being captured
```

## Hooks in settings.json

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "*", "hooks": [{"type": "command", "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh pre"}]}
    ],
    "PostToolUse": [
      {"matcher": "*", "hooks": [{"type": "command", "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh post"}]}
    ],
    "SessionStart": [
      {"matcher": "", "hooks": [{"type": "command", "command": "python3 ~/.claude/hooks/memory-decay.py 2>/dev/null || true"}]}
    ],
    "Stop": [
      {"matcher": "", "hooks": [{"type": "command", "command": "python3 ~/.claude/hooks/session-summarizer.py 2>/dev/null || true"}]}
    ]
  }
}
```

## Maintenance

- `/instinct-status` — check learned patterns
- `/evolve` — cluster instincts into skills
- `/promote` — promote project instincts to global
- `/daily-review` — manual daily analysis
- `/good-morning` — manual morning briefing
- Check `~/.claude/homunculus/projects/` for observation data
- Check `~/.claude/memory/decay-7d/` for session summaries
