#!/usr/bin/env python3
"""
Session Summarizer — Claude Code Stop Hook.

Collects git stats, CL v2.1 observations, and generates a session summary.
Appends corrections to reflexion.md and architectural decisions to decisions.md.

Runs on session end. Reads optional JSON from stdin.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HOME = Path.home()
MEMORY_DIR = HOME / ".claude" / "memory"
DECAY_7D_DIR = MEMORY_DIR / "decay-7d"
PERMANENT_DIR = MEMORY_DIR / "permanent"
HOMUNCULUS_DIR = HOME / ".claude" / "homunculus" / "projects"

DECISION_KEYWORDS = re.compile(
    r"\b(chose|decided|selected|switched\s+to|picked|went\s+with|opted\s+for|migrated\s+to)\b",
    re.IGNORECASE,
)


def run_git(args: list[str], cwd: str | None = None) -> str:
    """Run a git command, return stdout or empty string on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=5,
            cwd=cwd or os.getcwd(),
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def get_project_name(cwd: str) -> str:
    """Derive project name from git remote or directory name."""
    remote = run_git(["remote", "get-url", "origin"], cwd)
    if remote:
        name = remote.rstrip("/").rsplit("/", 1)[-1]
        if name.endswith(".git"):
            name = name[:-4]
        return name
    return Path(cwd).name


def get_branch(cwd: str) -> str:
    return run_git(["branch", "--show-current"], cwd) or "unknown"


def get_diff_stat(cwd: str) -> str:
    return run_git(["diff", "--stat", "HEAD"], cwd) or "(no changes)"


def get_recent_commits(cwd: str) -> str:
    return run_git(["log", "--oneline", "-5"], cwd) or "(no commits)"


def find_observations(project_name: str) -> tuple[int, list[str], list[str]]:
    """
    Find CL v2.1 observations for the project.
    Returns (count, corrections, decisions).
    """
    count = 0
    corrections: list[str] = []
    decisions: list[str] = []

    if not HOMUNCULUS_DIR.is_dir():
        return count, corrections, decisions

    try:
        for proj_dir in HOMUNCULUS_DIR.iterdir():
            if not proj_dir.is_dir():
                continue
            # Match by directory name containing project name (case-insensitive)
            if project_name.lower() not in proj_dir.name.lower():
                continue

            for obs_file in sorted(proj_dir.glob("**/*.md"), reverse=True):
                try:
                    content = obs_file.read_text(encoding="utf-8", errors="replace")
                    # Count observation entries (lines starting with - or numbered)
                    obs_lines = [
                        line.strip()
                        for line in content.splitlines()
                        if line.strip() and (line.strip().startswith("- ") or re.match(r"^\d+\.", line.strip()))
                    ]
                    count += len(obs_lines)

                    # Extract corrections (lines mentioning error, fix, wrong, mistake, corrected)
                    for line in obs_lines:
                        if re.search(r"\b(error|fix|wrong|mistake|correct|bug|issue)\b", line, re.IGNORECASE):
                            corrections.append(line.lstrip("- ").lstrip("0123456789. "))

                    # Extract decisions
                    for line in obs_lines:
                        if DECISION_KEYWORDS.search(line):
                            decisions.append(line.lstrip("- ").lstrip("0123456789. "))
                except Exception:
                    continue
            break  # Found the project directory
    except Exception:
        pass

    return count, corrections, decisions


def next_session_number(date_str: str) -> int:
    """Find the next sequential number for today's session files."""
    try:
        existing = list(DECAY_7D_DIR.glob(f"session-{date_str}-*.md"))
        numbers = []
        for f in existing:
            match = re.search(rf"session-{re.escape(date_str)}-(\d+)\.md$", f.name)
            if match:
                numbers.append(int(match.group(1)))
        return max(numbers, default=0) + 1
    except Exception:
        return 1


def append_to_file(path: Path, content: str) -> None:
    """Append content to a file, creating parent dirs if needed."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
    except Exception:
        pass


def read_stdin() -> dict:
    """Read optional JSON from stdin (Claude Code hook payload)."""
    try:
        if sys.stdin.isatty():
            return {}
        data = sys.stdin.read(65536)
        if data.strip():
            return json.loads(data)
    except Exception:
        pass
    return {}


def main() -> None:
    # Read stdin but don't require it
    hook_data = read_stdin()

    cwd = os.getcwd()
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    # Gather git info
    project_name = get_project_name(cwd)
    branch = get_branch(cwd)
    diff_stat = get_diff_stat(cwd)
    recent_commits = get_recent_commits(cwd)

    # Check if we're even in a git repo -- if not, still produce a summary
    is_git = bool(run_git(["rev-parse", "--is-inside-work-tree"], cwd))

    # Find CL v2.1 observations
    obs_count, corrections, decisions = find_observations(project_name)

    # Also scan recent commits and diff for decision keywords
    commit_decisions: list[str] = []
    for line in recent_commits.splitlines():
        if DECISION_KEYWORDS.search(line):
            # Strip the short hash prefix
            clean = re.sub(r"^[a-f0-9]+\s+", "", line)
            commit_decisions.append(clean)

    all_decisions = decisions + commit_decisions

    # Build session number
    session_num = next_session_number(date_str)

    # Key learnings from corrections
    learnings_section = ""
    if corrections:
        items = "\n".join(f"- {c}" for c in corrections[:10])
        learnings_section = f"\n## Key Learnings\n{items}\n"
    else:
        learnings_section = "\n## Key Learnings\nNo corrections observed this session.\n"

    # Build summary
    summary = f"""# Session Summary -- {date_str} #{session_num}
**Time**: {time_str}
**Project**: {project_name}
**Branch**: {branch}

## Changes
```
{diff_stat}
```

## Commits
```
{recent_commits}
```

## Observations
{obs_count} observation(s) from CL v2.1.
{learnings_section}"""

    # Ensure directories exist
    try:
        DECAY_7D_DIR.mkdir(parents=True, exist_ok=True)
        PERMANENT_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    # Save session summary
    summary_path = DECAY_7D_DIR / f"session-{date_str}-{session_num}.md"
    try:
        summary_path.write_text(summary, encoding="utf-8")
    except Exception:
        pass

    # Append corrections to reflexion.md
    if corrections:
        reflexion_path = PERMANENT_DIR / "reflexion.md"
        block = f"\n\n## {date_str} -- {project_name} (session #{session_num})\n"
        block += "\n".join(f"- {c}" for c in corrections[:10])
        block += "\n"
        append_to_file(reflexion_path, block)

    # Append architectural decisions to decisions.md
    if all_decisions:
        decisions_path = PERMANENT_DIR / "decisions.md"
        block = f"\n\n## {date_str} -- {project_name} (session #{session_num})\n"
        block += "\n".join(f"- {d}" for d in all_decisions[:10])
        block += "\n"
        append_to_file(decisions_path, block)

    # Output result for Claude Code hook
    result = {
        "status": "ok",
        "summary": str(summary_path),
        "project": project_name,
        "session": session_num,
        "observations": obs_count,
        "corrections": len(corrections),
        "decisions": len(all_decisions),
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
