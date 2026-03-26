#!/usr/bin/env python3
"""SessionStart hook: detect zombie/stuck processes eating RAM on macOS.

Reports system memory usage and flags suspicious processes (>500MB, >2h).
NEVER kills anything -- only reports.
"""

import re
import subprocess
import sys
import time

HEAVY_THRESHOLD_MB = 500
STUCK_THRESHOLD_SECONDS = 2 * 3600  # 2 hours

WATCH_PATTERNS = {
    "node": re.compile(r"\bnode\b", re.IGNORECASE),
    "python": re.compile(r"\bpython\b", re.IGNORECASE),
    "chromium": re.compile(r"chromium|playwright|headless", re.IGNORECASE),
    "claude": re.compile(r"\bclaude\b", re.IGNORECASE),
}


def run(cmd: str) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=5
        )
        return result.stdout
    except Exception:
        return ""


def get_total_memory_gb() -> float:
    out = run("sysctl -n hw.memsize")
    try:
        return int(out.strip()) / (1024 ** 3)
    except (ValueError, AttributeError):
        return 0.0


def get_used_memory_gb() -> float:
    out = run("vm_stat")
    if not out:
        return 0.0
    page_size = 16384  # default on Apple Silicon
    ps_match = re.search(r"page size of (\d+) bytes", out)
    if ps_match:
        page_size = int(ps_match.group(1))

    def pages(label: str) -> int:
        m = re.search(rf"{label}:\s+(\d+)", out)
        return int(m.group(1)) if m else 0

    active = pages("Pages active")
    wired = pages("Pages wired down")
    compressed = pages("Pages occupied by compressor")
    used_bytes = (active + wired + compressed) * page_size
    return used_bytes / (1024 ** 3)


def parse_elapsed(elapsed_str: str) -> int:
    """Parse ps elapsed time (dd-HH:MM:SS or HH:MM:SS or MM:SS) to seconds."""
    elapsed_str = elapsed_str.strip()
    days = 0
    if "-" in elapsed_str:
        d, elapsed_str = elapsed_str.split("-", 1)
        days = int(d)
    parts = elapsed_str.split(":")
    try:
        if len(parts) == 3:
            h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
        elif len(parts) == 2:
            h, m, s = 0, int(parts[0]), int(parts[1])
        else:
            return 0
    except ValueError:
        return 0
    return days * 86400 + h * 3600 + m * 60 + s


def get_processes():
    """Return list of (pid, rss_mb, elapsed_seconds, command) via ps."""
    out = run("ps -eo pid=,rss=,etime=,command=")
    if not out:
        return []
    procs = []
    for line in out.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 3)
        if len(parts) < 4:
            continue
        try:
            pid = int(parts[0])
            rss_mb = int(parts[1]) / 1024  # rss is in KB
            elapsed = parse_elapsed(parts[2])
            cmd = parts[3]
        except (ValueError, IndexError):
            continue
        procs.append((pid, rss_mb, elapsed, cmd))
    return procs


def format_mb(mb: float) -> str:
    if mb >= 1024:
        return f"{mb / 1024:.1f}GB"
    return f"{mb:.0f}MB"


def format_hours(seconds: int) -> str:
    h = seconds / 3600
    if h >= 24:
        return f"{h / 24:.0f}d"
    return f"{h:.1f}h"


def main():
    try:
        total_gb = get_total_memory_gb()
        used_gb = get_used_memory_gb()
        procs = get_processes()

        # Categorize processes
        categorized: dict[str, list[tuple[int, float, int, str]]] = {
            k: [] for k in WATCH_PATTERNS
        }
        for pid, rss_mb, elapsed, cmd in procs:
            for cat, pattern in WATCH_PATTERNS.items():
                if pattern.search(cmd):
                    categorized[cat].append((pid, rss_mb, elapsed, cmd))
                    break

        # Find suspicious: heavy AND stuck
        suspicious = []
        for cat, proc_list in categorized.items():
            for pid, rss_mb, elapsed, cmd in proc_list:
                if rss_mb > HEAVY_THRESHOLD_MB and elapsed > STUCK_THRESHOLD_SECONDS:
                    label = cat
                    # More specific label from command
                    for name in ("chromium", "playwright", "headless"):
                        if name in cmd.lower():
                            label = name
                            break
                    suspicious.append((pid, rss_mb, elapsed, label, cmd))

        # Summary stats per category (excluding claude from totals display)
        cat_summaries = []
        for cat in ("node", "python", "chromium"):
            proc_list = categorized[cat]
            if proc_list:
                count = len(proc_list)
                total_mb = sum(r for _, r, _, _ in proc_list)
                cat_summaries.append(f"{count} {cat} ({format_mb(total_mb)})")

        claude_count = len(categorized["claude"])

        # Memory health
        mem_pct = (used_gb / total_gb * 100) if total_gb > 0 else 0
        high = mem_pct > 80

        if suspicious:
            header = f"System: {used_gb:.1f}/{total_gb:.1f} GB used"
            if high:
                header += " -- HIGH"
            print(header)
            for pid, rss_mb, elapsed, label, cmd in suspicious:
                short_cmd = cmd[:80]
                print(
                    f"  [!] {label} (PID {pid}): {format_mb(rss_mb)}"
                    f" -- running {format_hours(elapsed)}"
                )
            kill_pids = " ".join(str(p[0]) for p in suspicious)
            print(f"  Suggestion: kill {kill_pids}")
            if cat_summaries:
                print(f"  Totals: {' | '.join(cat_summaries)}")
            if claude_count:
                print(f"  Claude processes: {claude_count}")
        elif cat_summaries or high:
            parts = [f"System: {used_gb:.1f}/{total_gb:.1f} GB used"]
            if high:
                parts[0] += " -- HIGH"
            parts.extend(cat_summaries)
            if claude_count:
                parts.append(f"{claude_count} claude")
            print(" | ".join(parts))
        else:
            print(f"System: {used_gb:.1f}/{total_gb:.1f} GB used | healthy")

    except Exception as e:
        # Defensive: never crash, just emit minimal output
        print(f"System: watchdog error ({e})")
        sys.exit(0)


if __name__ == "__main__":
    main()
