#!/usr/bin/env python3
"""Manual checkpoint script -- same logic as auto-checkpoint hook.

Usage:
    python3 ~/.claude/scripts/quick-checkpoint.py
    python3 ~/.claude/scripts/quick-checkpoint.py /path/to/project
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CHECKPOINT_DIR = Path.home() / ".claude" / "memory" / "decay-7d"


def run_git(*args: str, cwd: str | None = None) -> str:
    """Run a git command, return stdout or empty string on failure."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            timeout=3,
            cwd=cwd,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def is_git_repo(cwd: str) -> bool:
    return bool(run_git("rev-parse", "--is-inside-work-tree", cwd=cwd))


def get_branch(cwd: str) -> str:
    return run_git("branch", "--show-current", cwd=cwd) or "(detached)"


def get_last_commits(cwd: str, count: int = 3) -> str:
    return run_git("log", "--oneline", f"-{count}", cwd=cwd) or "(no commits)"


def get_status_short(cwd: str) -> str:
    return run_git("status", "--short", cwd=cwd) or "(clean)"


def count_modified(status: str) -> int:
    if status == "(clean)":
        return 0
    return len([line for line in status.splitlines() if line.strip()])


def read_memory_head(cwd: str, lines: int = 20) -> str:
    memory_path = Path(cwd) / "MEMORY.md"
    if not memory_path.is_file():
        return "(no MEMORY.md in project)"
    try:
        text = memory_path.read_text(encoding="utf-8", errors="replace")
        result = "\n".join(text.splitlines()[:lines])
        return result or "(empty MEMORY.md)"
    except Exception:
        return "(could not read MEMORY.md)"


def next_checkpoint_number(date_str: str) -> int:
    if not CHECKPOINT_DIR.is_dir():
        return 1
    prefix = f"compact-{date_str}-"
    existing = [
        f.name for f in CHECKPOINT_DIR.iterdir()
        if f.name.startswith(prefix) and f.suffix == ".md"
    ]
    if not existing:
        return 1
    numbers = []
    for name in existing:
        stem = name.removesuffix(".md").removeprefix(prefix)
        try:
            numbers.append(int(stem))
        except ValueError:
            pass
    return max(numbers, default=0) + 1


def save_checkpoint(cwd: str) -> str:
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d %H:%M")
    project_name = Path(cwd).name

    if not is_git_repo(cwd):
        checkpoint_n = next_checkpoint_number(date_str)
        filename = f"compact-{date_str}-{checkpoint_n}.md"
        memory_head = read_memory_head(cwd)
        content = f"""# Pre-Compact Checkpoint -- {time_str}
**Project**: {project_name}
**Branch**: (not a git repo)
**Modified files**: unknown

## Active Task Context
```
{memory_head}
```
"""
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        (CHECKPOINT_DIR / filename).write_text(content, encoding="utf-8")
        return f"Checkpoint saved: {project_name} (no git) -> {filename}"

    branch = get_branch(cwd)
    last_commits = get_last_commits(cwd)
    status = get_status_short(cwd)
    modified_count = count_modified(status)
    memory_head = read_memory_head(cwd)

    first_commit_line = last_commits.splitlines()[0] if last_commits != "(no commits)" else "no commits"
    last_msg = first_commit_line.split(" ", 1)[1] if " " in first_commit_line else first_commit_line

    checkpoint_n = next_checkpoint_number(date_str)
    filename = f"compact-{date_str}-{checkpoint_n}.md"

    content = f"""# Pre-Compact Checkpoint -- {time_str}
**Project**: {project_name}
**Branch**: {branch}
**Modified files**: {modified_count}

## Last 3 Commits
```
{last_commits}
```

## Uncommitted Changes
```
{status}
```

## Active Task Context
```
{memory_head}
```
"""

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint_path = CHECKPOINT_DIR / filename
    checkpoint_path.write_text(content, encoding="utf-8")

    return f"Checkpoint saved: {branch} | {modified_count} files modified | {last_msg} -> {filename}"


def main() -> None:
    if len(sys.argv) > 1:
        cwd = os.path.abspath(sys.argv[1])
        if not os.path.isdir(cwd):
            print(f"Error: {cwd} is not a directory", file=sys.stderr)
            sys.exit(1)
    else:
        cwd = os.getcwd()

    summary = save_checkpoint(cwd)
    print(summary)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"quick-checkpoint error: {e}", file=sys.stderr)
        sys.exit(1)
