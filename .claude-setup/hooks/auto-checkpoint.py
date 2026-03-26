#!/usr/bin/env python3
"""PreCompact hook: save a mini-checkpoint before context compaction.

Captures git state, modified files, and MEMORY.md snippet so that
post-compact context retains a breadcrumb of what was happening.

stdlib only, fast (<2s), never crashes.
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
    """Check if cwd is inside a git repository."""
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
    """Read first N lines of MEMORY.md if it exists in the project."""
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
    """Find next N for compact-YYYY-MM-DD-N.md to avoid overwrites."""
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
        # compact-2026-03-27-3.md -> extract "3"
        stem = name.removesuffix(".md").removeprefix(prefix)
        try:
            numbers.append(int(stem))
        except ValueError:
            pass
    return max(numbers, default=0) + 1


def save_checkpoint(cwd: str) -> str:
    """Build and save checkpoint markdown. Returns the one-liner summary."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d %H:%M")
    project_name = Path(cwd).name

    branch = get_branch(cwd)
    last_commits = get_last_commits(cwd)
    status = get_status_short(cwd)
    modified_count = count_modified(status)
    memory_head = read_memory_head(cwd)

    # Last commit message for the one-liner
    first_commit_line = last_commits.splitlines()[0] if last_commits != "(no commits)" else "no commits"
    # Strip hash prefix for cleaner display
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

    return f"Pre-compact checkpoint saved: {branch} | {modified_count} files modified | {last_msg}"


def main() -> None:
    cwd = os.getcwd()

    if not is_git_repo(cwd):
        # Not a git repo -- still save a minimal checkpoint
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        checkpoint_n = next_checkpoint_number(date_str)
        filename = f"compact-{date_str}-{checkpoint_n}.md"
        project_name = Path(cwd).name
        memory_head = read_memory_head(cwd)

        content = f"""# Pre-Compact Checkpoint -- {now.strftime("%Y-%m-%d %H:%M")}
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
        print(f"Pre-compact checkpoint saved: {project_name} (no git)")
        return

    summary = save_checkpoint(cwd)
    print(summary)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Never crash -- hooks must be silent on failure
        print(f"auto-checkpoint error: {e}", file=sys.stderr)
