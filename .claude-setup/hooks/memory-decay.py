#!/usr/bin/env python3
"""SessionStart hook: clean expired memory files, report status."""

import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_ROOT = Path.home() / ".claude" / "memory"

DECAY_DIRS = {
    "decay-7d": 7,
    "decay-30d": 30,
}

PERMANENT_DIR = MEMORY_ROOT / "permanent"


def get_file_age_days(path: Path) -> float:
    """Return file age in days based on mtime."""
    try:
        mtime = path.stat().st_mtime
        return (time.time() - mtime) / 86400.0
    except OSError:
        return 0.0


def get_access_count(path: Path) -> int:
    """Estimate access count from atime vs mtime delta and size heuristic.

    If a file was accessed many times, atime diverges from mtime.
    We also check for a .meta JSON sidecar with explicit access_count.
    """
    try:
        import json
        meta_path = path.with_suffix(path.suffix + ".meta")
        if meta_path.exists():
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            return int(data.get("access_count", 0))
    except Exception:
        pass

    # Fallback: compare atime vs mtime as rough heuristic
    try:
        stat = path.stat()
        atime_delta = abs(stat.st_atime - stat.st_mtime)
        # If accessed significantly after modification, likely read multiple times
        if atime_delta > 86400 * 3:
            return 4  # conservative estimate: accessed >3 times
        return 1
    except OSError:
        return 0


def clean_decay_dir(dir_path: Path, max_age_days: int) -> tuple[int, int, list[str]]:
    """Clean expired files. Returns (remaining, removed, promote_candidates)."""
    if not dir_path.is_dir():
        return 0, 0, []

    remaining = 0
    removed = 0
    promote = []

    try:
        for entry in dir_path.iterdir():
            if entry.name.startswith(".") or entry.suffix == ".meta":
                continue
            if not entry.is_file():
                continue

            age = get_file_age_days(entry)

            if age > max_age_days:
                # Before deleting, check if high-value
                access = get_access_count(entry)
                if access > 3:
                    promote.append(entry.name)

                try:
                    entry.unlink()
                    # Also remove sidecar meta if exists
                    meta = entry.with_suffix(entry.suffix + ".meta")
                    if meta.exists():
                        meta.unlink()
                    removed += 1
                except OSError:
                    remaining += 1
            else:
                remaining += 1
    except OSError:
        pass

    return remaining, removed, promote


def count_permanent() -> int:
    """Count files in permanent memory."""
    if not PERMANENT_DIR.is_dir():
        return 0
    try:
        return sum(
            1 for f in PERMANENT_DIR.iterdir()
            if f.is_file() and not f.name.startswith(".")
        )
    except OSError:
        return 0


def main() -> None:
    start = time.monotonic()

    sessions_remaining = 0
    sessions_removed = 0
    dailies_remaining = 0
    dailies_removed = 0
    all_promote: list[str] = []

    for dir_name, max_days in DECAY_DIRS.items():
        dir_path = MEMORY_ROOT / dir_name
        remaining, removed, promote = clean_decay_dir(dir_path, max_days)

        if dir_name == "decay-7d":
            sessions_remaining = remaining
            sessions_removed = removed
        else:
            dailies_remaining = remaining
            dailies_removed = removed

        all_promote.extend(promote)

    permanent_count = count_permanent()

    # Build output
    parts = [
        f"Memory Status: {sessions_remaining} sessions (7d)",
        f"{dailies_remaining} dailies (30d)",
        f"{permanent_count} permanent items",
    ]
    summary = " | ".join(parts)

    # Cleanup stats (only show if something was cleaned)
    cleaned_parts = []
    if sessions_removed:
        cleaned_parts.append(f"{sessions_removed} expired sessions")
    if dailies_removed:
        cleaned_parts.append(f"{dailies_removed} expired dailies")

    print(summary)

    if cleaned_parts:
        print(f"Cleaned: {', '.join(cleaned_parts)}")

    if all_promote:
        print(f"PROMOTE to permanent (accessed >3x): {', '.join(all_promote)}")

    elapsed = time.monotonic() - start
    if elapsed > 0.5:
        print(f"(memory-decay took {elapsed:.1f}s)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Never crash the session start
        print(f"Memory decay error: {e}", file=sys.stderr)
