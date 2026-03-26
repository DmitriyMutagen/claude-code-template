#!/usr/bin/env python3
"""
Merge Claude Code hooks into existing settings.json.
Adds self-learning hooks without removing existing ones.
"""
import json
import os
import sys

SETTINGS_PATH = os.path.expanduser("~/.claude/settings.json")

# Hooks to ensure exist
REQUIRED_HOOKS = {
    "PreToolUse": [
        {"matcher": "*", "hooks": [{"type": "command", "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh pre"}]},
    ],
    "PostToolUse": [
        {"matcher": "*", "hooks": [{"type": "command", "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh post"}]},
    ],
    "SessionStart": [
        {"matcher": "", "hooks": [{"type": "command", "command": "python3 ~/.claude/hooks/memory-decay.py 2>/dev/null || true"}]},
        {"matcher": "", "hooks": [{"type": "command", "command": "python3 ~/.claude/hooks/mcp-health-check.py 2>/dev/null || true"}]},
        {"matcher": "", "hooks": [{"type": "command", "command": "python3 ~/.claude/hooks/process-watchdog.py 2>/dev/null || true"}]},
    ],
    "PreCompact": [
        {"matcher": "", "hooks": [{"type": "command", "command": "echo '{}' | python3 ~/.claude/hooks/auto-checkpoint.py 2>/dev/null || true"}]},
    ],
    "Stop": [
        {"matcher": "", "hooks": [{"type": "command", "command": "python3 ~/.claude/hooks/session-summarizer.py 2>/dev/null || true"}]},
    ],
}

def main():
    # Load or create settings
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH) as f:
            settings = json.load(f)
    else:
        settings = {}

    hooks = settings.setdefault("hooks", {})
    added = 0

    for event, required_items in REQUIRED_HOOKS.items():
        event_hooks = hooks.setdefault(event, [])
        for item in required_items:
            # Check if already exists (by command string)
            cmd = str(item.get("hooks", [{}])[0].get("command", ""))
            already_exists = any(cmd in str(h) for h in event_hooks)
            if not already_exists:
                event_hooks.append(item)
                added += 1

    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    print(f"  ✅ settings.json обновлён ({added} хуков добавлено)")

if __name__ == "__main__":
    main()
