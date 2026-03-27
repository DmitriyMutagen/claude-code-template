#!/usr/bin/env python3
"""PostToolUse hook: auto-document feat/refactor commits in MEMORY.md.

Reads hook JSON from stdin. If the Bash command contains "git commit"
and the message starts with "feat:" or "refactor:", appends a line
to the project's MEMORY.md.
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path


def main() -> None:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        payload = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        return

    tool_input = payload.get("tool_input", {})
    command = tool_input.get("command", "")

    if "git commit" not in command:
        return

    # Extract commit message from -m "..." or -m '...'
    match = re.search(r'git commit\s+.*-m\s+["\'](.+?)["\']', command)
    if not match:
        return

    msg = match.group(1).strip()

    # Only track feat: and refactor: commits
    if not (msg.startswith("feat:") or msg.startswith("refactor:")):
        return

    # Find MEMORY.md -- prefer CWD, fall back to home
    cwd = os.environ.get("PWD", os.getcwd())
    memory_path = Path(cwd) / "MEMORY.md"

    if not memory_path.exists():
        # Create minimal MEMORY.md
        try:
            memory_path.write_text("# Project Memory\n\n## Changelog\n\n", encoding="utf-8")
        except OSError:
            return

    today = date.today().isoformat()
    line = f"- {today}: {msg}\n"

    try:
        content = memory_path.read_text(encoding="utf-8")
        # Insert after "## Changelog" header if it exists, otherwise append
        if "## Changelog" in content:
            idx = content.index("## Changelog") + len("## Changelog")
            # Skip past the newline after the header
            while idx < len(content) and content[idx] in ("\n", "\r"):
                idx += 1
            content = content[:idx] + line + content[idx:]
        else:
            content = content.rstrip("\n") + "\n\n## Changelog\n" + line
        memory_path.write_text(content, encoding="utf-8")
    except OSError:
        return

    summary = msg[:60] + "..." if len(msg) > 60 else msg
    print(f"\U0001f4dd Документация обновлена: {summary}")


if __name__ == "__main__":
    main()
