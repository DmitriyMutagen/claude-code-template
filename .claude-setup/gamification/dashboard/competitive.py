#!/usr/bin/env python3
"""
Competitive Dashboard -- generates a rich Telegram message with developer ranking.

Usage:
    python3 competitive.py              # print to stdout
    python3 competitive.py --telegram   # send to Telegram
    python3 competitive.py --weekly     # weekly summary
"""

import json
import os
import sqlite3
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

GAMIFY_DIR = Path.home() / ".claude" / "gamification"
DB_PATH = GAMIFY_DIR / "gamify.db"
CONFIG_PATH = GAMIFY_DIR / "config.json"

# Hardcoded benchmarks (fallback if developer_ranks table is empty).
# Format: metric -> (p25, p50, p75, p90, p99)
DEFAULT_BENCHMARKS: dict[str, tuple[float, float, float, float, float]] = {
    "commits_per_day":       (2.0,  5.0,  12.0, 25.0, 50.0),
    "files_per_day":         (5.0,  15.0, 40.0, 80.0, 200.0),
    "tests_per_day":         (0.0,  5.0,  15.0, 40.0, 100.0),
    "agents_per_day":        (0.0,  1.0,  5.0,  10.0, 20.0),
    "xp_per_day":            (50.0, 200.0, 500.0, 1500.0, 5000.0),
    "streak_days":           (1.0,  3.0,  7.0,  14.0, 30.0),
    "deploys_per_week":      (0.0,  1.0,  3.0,  7.0,  14.0),
    "sentry_fixes_per_week": (0.0,  1.0,  3.0,  8.0,  20.0),
}

RANK_LABELS: list[tuple[int, str, str]] = [
    (99, "\u0411\u043e\u0433 \u041a\u043e\u0434\u0438\u043d\u0433\u0430", "\U0001f451"),   # crown
    (90, "\u042d\u043b\u0438\u0442\u0430",    "\u26a1"),       # lightning
    (75, "\u0421\u0435\u043d\u044c\u043e\u0440",   "\U0001f4aa"),   # flexed bicep
    (50, "\u041c\u0438\u0434\u043b",      "\U0001f527"),   # wrench
    (25, "\u0414\u0436\u0443\u043d\u0438\u043e\u0440",   "\u26a0\ufe0f"), # warning
    (0,  "\u041d\u043e\u0432\u0438\u0447\u043e\u043a",   "\u26a0\ufe0f"),
]


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def load_benchmarks(conn: sqlite3.Connection) -> dict[str, tuple[float, float, float, float, float]]:
    """Load benchmarks from DB, fall back to defaults."""
    try:
        rows = conn.execute("SELECT metric, p25, p50, p75, p90, p99 FROM developer_ranks").fetchall()
        if rows:
            result = {}
            for r in rows:
                result[r["metric"]] = (r["p25"], r["p50"], r["p75"], r["p90"], r["p99"])
            return result
    except Exception:
        pass
    return DEFAULT_BENCHMARKS


def calc_percentile(value: float, benchmarks: tuple[float, float, float, float, float]) -> int:
    """Return approximate percentile (0-99) given (p25, p50, p75, p90, p99)."""
    p25, p50, p75, p90, p99 = benchmarks
    if value <= 0 and p25 <= 0:
        return 10
    if value <= 0:
        return 5
    if value >= p99:
        return 99
    if value >= p90:
        return 90 + int(9 * (value - p90) / max(p99 - p90, 0.01))
    if value >= p75:
        return 75 + int(15 * (value - p75) / max(p90 - p75, 0.01))
    if value >= p50:
        return 50 + int(25 * (value - p50) / max(p75 - p50, 0.01))
    if value >= p25:
        return 25 + int(25 * (value - p25) / max(p50 - p25, 0.01))
    return max(1, int(25 * value / max(p25, 0.01)))


def rank_for_percentile(pct: int) -> tuple[str, str]:
    """Return (label, emoji) for a percentile."""
    for threshold, label, emoji in RANK_LABELS:
        if pct >= threshold:
            return label, emoji
    return "\u041d\u043e\u0432\u0438\u0447\u043e\u043a", "\u26a0\ufe0f"


def get_today_metrics(conn: sqlite3.Connection) -> dict[str, float]:
    """Compute today's metrics from xp_events and sessions."""
    today = date.today().isoformat()

    row = conn.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN action LIKE '%commit%' THEN 1 ELSE 0 END), 0) as commits,
            COALESCE(SUM(CASE WHEN action IN ('Write') THEN 1 ELSE 0 END), 0) as files_created,
            COALESCE(SUM(CASE WHEN action IN ('Edit', 'MultiEdit') THEN 1 ELSE 0 END), 0) as files_edited,
            COALESCE(SUM(CASE WHEN action LIKE '%test%' THEN 1 ELSE 0 END), 0) as tests,
            COALESCE(SUM(CASE WHEN action = 'task_agent_spawn' THEN 1 ELSE 0 END), 0) as agents,
            COALESCE(SUM(xp), 0) as total_xp
        FROM xp_events
        WHERE date(ts) = ?
    """, (today,)).fetchone()

    return {
        "commits": row["commits"],
        "files": row["files_created"] + row["files_edited"],
        "tests": row["tests"],
        "agents": row["agents"],
        "xp": row["total_xp"],
    }


def get_streak(conn: sqlite3.Connection) -> int:
    """Calculate current streak of consecutive days with activity."""
    rows = conn.execute("""
        SELECT DISTINCT date(ts) as d FROM xp_events ORDER BY d DESC LIMIT 60
    """).fetchall()
    if not rows:
        return 0
    days = sorted([r["d"] for r in rows], reverse=True)
    streak = 0
    expected = date.today()
    for d_str in days:
        d = date.fromisoformat(d_str)
        if d == expected:
            streak += 1
            expected -= timedelta(days=1)
        elif d < expected:
            break
    return streak


def get_week_metrics(conn: sqlite3.Connection) -> dict[str, float]:
    """Compute this week's metrics."""
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()
    today = date.today().isoformat()

    row = conn.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN action LIKE '%deploy%' THEN 1 ELSE 0 END), 0) as deploys,
            COALESCE(SUM(CASE WHEN action LIKE '%sentry%' THEN 1 ELSE 0 END), 0) as sentry_fixes,
            COALESCE(SUM(xp), 0) as total_xp,
            COUNT(*) as total_events,
            COALESCE(SUM(CASE WHEN action LIKE '%commit%' THEN 1 ELSE 0 END), 0) as commits
        FROM xp_events
        WHERE date(ts) >= ? AND date(ts) <= ?
    """, (week_start, today)).fetchone()

    return {
        "deploys": row["deploys"],
        "sentry_fixes": row["sentry_fixes"],
        "total_xp": row["total_xp"],
        "total_events": row["total_events"],
        "commits": row["commits"],
    }


def get_week_daily_breakdown(conn: sqlite3.Connection) -> list[dict]:
    """Get per-day breakdown for the current week."""
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()
    today = date.today().isoformat()

    rows = conn.execute("""
        SELECT date(ts) as d, COUNT(*) as events, SUM(xp) as xp
        FROM xp_events
        WHERE date(ts) >= ? AND date(ts) <= ?
        GROUP BY date(ts)
        ORDER BY d
    """, (week_start, today)).fetchall()

    return [{"date": r["d"], "events": r["events"], "xp": r["xp"]} for r in rows]


def get_prev_week_metrics(conn: sqlite3.Connection) -> dict[str, float]:
    """Compute previous week's metrics."""
    this_monday = date.today() - timedelta(days=date.today().weekday())
    prev_monday = (this_monday - timedelta(days=7)).isoformat()
    prev_sunday = (this_monday - timedelta(days=1)).isoformat()

    row = conn.execute("""
        SELECT
            COALESCE(SUM(xp), 0) as total_xp,
            COUNT(*) as total_events,
            COALESCE(SUM(CASE WHEN action LIKE '%commit%' THEN 1 ELSE 0 END), 0) as commits
        FROM xp_events
        WHERE date(ts) >= ? AND date(ts) <= ?
    """, (prev_monday, prev_sunday)).fetchone()

    return {
        "total_xp": row["total_xp"],
        "total_events": row["total_events"],
        "commits": row["commits"],
    }


def format_metric_line(
    name: str, value: float, benchmark_key: str,
    benchmarks: dict[str, tuple[float, float, float, float, float]],
    unit: str = "/day", connector: str = "\u251c"
) -> tuple[str, int]:
    """Format a single metric line and return (line, percentile)."""
    bm = benchmarks.get(benchmark_key)
    if bm is None:
        return f"  {connector} {name}: {value:.0f}{unit}", 50

    pct = calc_percentile(value, bm)
    label, emoji = rank_for_percentile(pct)
    line = f"  {connector} {name}: {int(value)}{unit} {emoji} {label} (Top {pct}%)"
    return line, pct


def pct_change_str(current: float, previous: float) -> str:
    """Format percentage change."""
    if previous <= 0:
        if current > 0:
            return "+inf% (first week!)"
        return "0%"
    change = ((current - previous) / previous) * 100
    arrow = "+" if change >= 0 else ""
    return f"{arrow}{change:.0f}%"


def overall_rank(percentiles: list[int]) -> tuple[str, int]:
    """Compute overall rank from individual percentiles."""
    if not percentiles:
        return "Unranked", 0
    avg = sum(percentiles) / len(percentiles)
    pct = int(avg)
    label, emoji = rank_for_percentile(pct)
    return f"{emoji} {label} (Top {pct}%)", pct


def identify_strengths_weaknesses(
    metrics: list[tuple[str, int]]
) -> tuple[list[str], list[str]]:
    """Return (strengths, weaknesses) based on percentiles."""
    strengths = [name for name, pct in metrics if pct >= 75]
    weaknesses = [name for name, pct in metrics if pct < 50]
    return strengths, weaknesses


def generate_challenge(weaknesses: list[tuple[str, int]]) -> str:
    """Generate a challenge based on weakest metric."""
    if not weaknesses:
        return "\u041f\u0440\u043e\u0434\u043e\u043b\u0436\u0430\u0439 \u0436\u0435\u0447\u044c!"
    metric_name, pct = min(weaknesses, key=lambda x: x[1])
    challenges = {
        "deploys": "\u0421\u0434\u0435\u043b\u0430\u0439 1 \u0434\u0435\u043f\u043b\u043e\u0439 \u0434\u043e \u041c\u0438\u0434\u043b\u0430!",
        "sentry": "\u041f\u043e\u0447\u0438\u043d\u0438 1 Sentry issue \u0434\u043b\u044f \u0430\u043f\u0430!",
        "commits": "\u0417\u0430\u043f\u0443\u0448\u0438 5 \u043a\u043e\u043c\u043c\u0438\u0442\u043e\u0432 \u0441\u0435\u0433\u043e\u0434\u043d\u044f!",
        "tests": "\u0417\u0430\u043f\u0443\u0441\u0442\u0438 5 \u0442\u0435\u0441\u0442\u043e\u0432 \u0434\u043b\u044f \u0430\u043f\u0430!",
        "files": "\u0417\u0430\u0442\u0440\u043e\u043d\u044c 10 \u0444\u0430\u0439\u043b\u043e\u0432 \u0441\u0435\u0433\u043e\u0434\u043d\u044f!",
        "agents": "\u0417\u0430\u043f\u0443\u0441\u0442\u0438 2 \u0430\u0433\u0435\u043d\u0442\u043e\u0432 \u0434\u043b\u044f \u0430\u043f\u0430!",
        "xp": "\u0417\u0430\u0440\u0430\u0431\u043e\u0442\u0430\u0439 200 XP \u0441\u0435\u0433\u043e\u0434\u043d\u044f!",
        "streak": "\u041a\u043e\u0434\u044c 3 \u0434\u043d\u044f \u043f\u043e\u0434\u0440\u044f\u0434 \u0434\u043b\u044f \u0430\u043f\u0430!",
    }
    for key, challenge in challenges.items():
        if key in metric_name.lower():
            return challenge
    return f"\u041f\u0440\u043e\u043a\u0430\u0447\u0430\u0439 {metric_name} \u0434\u043e \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0435\u0433\u043e \u0440\u0430\u043d\u0433\u0430!"


def build_daily_message() -> str:
    """Build the daily competitive dashboard message."""
    conn = get_db()
    benchmarks = load_benchmarks(conn)
    today_m = get_today_metrics(conn)
    week_m = get_week_metrics(conn)
    streak = get_streak(conn)

    today_str = date.today().strftime("%d.%m.%Y")

    all_percentiles: list[int] = []
    named_metrics: list[tuple[str, int]] = []

    lines_today = []
    for name, value, bm_key, unit in [
        ("Commits",  today_m["commits"], "commits_per_day",  "/day"),
        ("Files",    today_m["files"],   "files_per_day",    "/day"),
        ("Tests",    today_m["tests"],   "tests_per_day",    "/day"),
        ("Agents",   today_m["agents"],  "agents_per_day",   "/day"),
        ("XP",       today_m["xp"],      "xp_per_day",       "/day"),
    ]:
        # files benchmark: merge files_created + files_edited
        actual_bm_key = bm_key
        if bm_key == "files_per_day":
            actual_bm_key = "files_edited_per_day"

        connector = "\u251c" if name != "Streak" else "\u2514"
        line, pct = format_metric_line(name, value, actual_bm_key, benchmarks, unit, connector)
        lines_today.append(line)
        all_percentiles.append(pct)
        named_metrics.append((name, pct))

    # Streak (last daily metric, use special connector)
    streak_bm = benchmarks.get("streak_days")
    if streak_bm:
        streak_pct = calc_percentile(float(streak), streak_bm)
        streak_label, streak_emoji = rank_for_percentile(streak_pct)
        lines_today.append(
            f"  \u2514 Streak: {streak} days {streak_emoji} {streak_label} (Top {streak_pct}%)"
        )
        all_percentiles.append(streak_pct)
        named_metrics.append(("Streak", streak_pct))

    lines_week = []
    for name, value, bm_key, unit in [
        ("Deploys", week_m["deploys"],       "deploys_per_week",      "/week"),
        ("Sentry",  week_m["sentry_fixes"],  "sentry_fixes_per_week", "/week"),
    ]:
        connector = "\u251c" if name == "Deploys" else "\u2514"
        line, pct = format_metric_line(name, value, bm_key, benchmarks, unit, connector)
        lines_week.append(line)
        all_percentiles.append(pct)
        named_metrics.append((name, pct))

    rank_str, rank_pct = overall_rank(all_percentiles)
    strengths, weaknesses_list = identify_strengths_weaknesses(named_metrics)
    weak_tuples = [(n, p) for n, p in named_metrics if p < 50]
    challenge = generate_challenge(weak_tuples)

    strengths_str = ", ".join(s.lower() for s in strengths) if strengths else "\u0440\u0430\u0437\u043e\u0433\u0440\u0435\u0432\u0430\u0435\u043c\u0441\u044f"
    weaknesses_str = ", ".join(w.lower() for w in weaknesses_list) if weaknesses_list else "\u043d\u0435\u0442!"

    msg = f"""*\u0420\u0435\u0439\u0442\u0438\u043d\u0433 -- {today_str}*

*\u041e\u0411\u0429\u0418\u0419 \u0420\u0410\u041d\u0413: {rank_str}*

_\u0421\u0435\u0433\u043e\u0434\u043d\u044f:_
{chr(10).join(lines_today)}

_\u041d\u0435\u0434\u0435\u043b\u044f:_
{chr(10).join(lines_week)}

*\u0421\u0438\u043b\u044c\u043d\u044b\u0435 \u0441\u0442\u043e\u0440\u043e\u043d\u044b:* {strengths_str}
*\u0417\u043e\u043d\u0430 \u0440\u043e\u0441\u0442\u0430:* {weaknesses_str}

*\u0427\u0435\u043b\u043b\u0435\u043d\u0434\u0436 \u0434\u043d\u044f:* {challenge}"""

    return msg


def build_weekly_message() -> str:
    """Build the weekly summary message."""
    conn = get_db()
    week_m = get_week_metrics(conn)
    prev_m = get_prev_week_metrics(conn)
    daily = get_week_daily_breakdown(conn)
    streak = get_streak(conn)
    benchmarks = load_benchmarks(conn)

    week_num = date.today().isocalendar()[1]

    commits_change = pct_change_str(week_m["commits"], prev_m["commits"])
    xp_change = pct_change_str(week_m["total_xp"], prev_m["total_xp"])

    best_day = max(daily, key=lambda d: d["xp"]) if daily else None
    worst_day = min(daily, key=lambda d: d["xp"]) if daily else None

    # Overall rank
    today_m = get_today_metrics(conn)
    percentiles = []
    for value, bm_key in [
        (week_m["commits"] / max(len(daily), 1), "commits_per_day"),
        (today_m["xp"],                          "xp_per_day"),
        (float(streak),                          "streak_days"),
    ]:
        bm = benchmarks.get(bm_key)
        if bm:
            percentiles.append(calc_percentile(value, bm))

    rank_str, _ = overall_rank(percentiles)

    best_str = f"{best_day['date']} ({best_day['events']} events, {best_day['xp']:,} XP)" if best_day else "N/A"
    worst_str = f"{worst_day['date']} ({worst_day['events']} events, {worst_day['xp']:,} XP)" if worst_day else "N/A"

    # Weekly chart
    chart_lines = []
    week_start = date.today() - timedelta(days=date.today().weekday())
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    daily_map = {d["date"]: d for d in daily}
    for i in range(7):
        d = week_start + timedelta(days=i)
        if d > date.today():
            break
        d_str = d.isoformat()
        info = daily_map.get(d_str)
        xp = info["xp"] if info else 0
        bars = min(12, xp // 50) if xp > 0 else 0
        chart_lines.append(f"  {day_names[i]}: {'#' * bars}{'.' * (12 - bars)} {xp:>5} XP")

    chart = "\n".join(chart_lines)

    msg = f"""*Weekly Report -- week {week_num}*

Progress vs last week:
  Commits: {week_m['commits']} ({commits_change})
  XP: {week_m['total_xp']:,} ({xp_change})

Best day: {best_str}
Worst day: {worst_str}

XP chart:
```
{chart}
```

Overall rank: {rank_str}
Streak: {streak} days"""

    return msg


def send_telegram(text: str) -> bool:
    """Send message via Telegram Bot API."""
    config = load_config()
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or config.get("telegram_bot_token")
    chat_id = os.environ.get("TELEGRAM_USER_ID") or config.get("telegram_user_id")

    if not token or not chat_id:
        print("ERROR: TELEGRAM_BOT_TOKEN / TELEGRAM_USER_ID not configured", file=sys.stderr)
        return False

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    data = urllib.parse.urlencode(payload).encode()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                return True
            body = resp.read().decode()
            print(f"Telegram API error: {resp.status} {body}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Telegram send failed: {e}", file=sys.stderr)
        return False


def main() -> None:
    args = set(sys.argv[1:])
    weekly = "--weekly" in args
    to_telegram = "--telegram" in args

    if weekly:
        msg = build_weekly_message()
    else:
        msg = build_daily_message()

    if to_telegram:
        ok = send_telegram(msg)
        if ok:
            print("Sent to Telegram.")
        else:
            print("Failed to send. Printing to stdout:\n")
            print(msg)
    else:
        print(msg)


if __name__ == "__main__":
    main()
