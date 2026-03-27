# Setup Claude Code Infrastructure on New Machine

## Prerequisites
- macOS or Linux
- Python 3.11+
- Node.js 18+
- Git
- Claude Code CLI installed

## Quick Start (30 seconds)

```bash
# 1. Clone template
git clone https://github.com/DmitriyMutagen/claude-code-template.git ~/my-project
cd ~/my-project

# 2. Run installer
bash .claude-setup/install.sh

# 3. Add your API keys to ~/.claude/settings.json
# (edit the env section with your actual keys)

# 4. Restart Claude Code
# Done! All hooks, rules, skills, instincts are active.
```

## What Gets Installed

| Component | Count | Location |
|-----------|-------|----------|
| Rules | 16 | ~/.claude/rules/ |
| Hooks | 8 | ~/.claude/hooks/ |
| Scripts | 3 | ~/.claude/scripts/ |
| Instincts | 10 | ~/.claude/homunculus/instincts/personal/ |
| Skills | 4 | ~/.claude/skills/ (CL v2.1, daily-review, good-morning, do-router) |
| Gamification | 3 files | ~/.claude/gamification/ |

## Verify Installation

After restart, you should see at session start:
```
MCP Status: X/Y healthy
System: X/Y GB used | healthy
Memory Status: X sessions (7d) | Y dailies (30d) | Z permanent items
```

## Daily Commands
- `/do [task]` — universal task router
- `/daily-review` — evening analysis
- `/good-morning` — morning briefing
- `/instinct-status` — learned patterns
- `/evolve` — cluster instincts into skills
- `python3 ~/.claude/gamification/engine.py` — competitive ranking
- `python3 ~/.claude/gamification/dashboard/competitive.py --telegram` — send to Telegram
