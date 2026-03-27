#!/usr/bin/env python3
"""
🎮 Aragant Gamification Engine v2.0
Централизованный движок XP/уровней/достижений для всех проектов Дмитрия.
SQLite WAL mode — потокобезопасен, мгновенный доступ.
"""

import json
import sqlite3
import os
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

GAMIFY_DIR = Path.home() / ".claude" / "gamification"
DB_PATH = GAMIFY_DIR / "gamify.db"
CONFIG_PATH = GAMIFY_DIR / "config.json"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


BENCHMARK_DATA = [
    ("commits_per_day", 2, 5, 12, 25, 50, "commits/day", "GitHub Stats 2025"),
    ("files_created_per_day", 3, 8, 20, 50, 100, "files/day", "AI-Dev Benchmarks"),
    ("files_edited_per_day", 5, 15, 40, 80, 200, "edits/day", "AI-Dev Benchmarks"),
    ("tests_per_day", 0, 5, 15, 40, 100, "tests/day", "TDD Practitioners"),
    ("agents_per_day", 0, 1, 5, 10, 20, "agents/day", "Anthropic C Compiler Study"),
    ("xp_per_day", 50, 200, 500, 1500, 5000, "XP/day", "Internal"),
    ("streak_days", 1, 3, 7, 14, 30, "days", "Dev Discipline Study"),
    ("deploys_per_week", 0, 1, 3, 7, 14, "deploys/week", "DORA 2025 Elite"),
    ("sentry_fixes_per_week", 0, 1, 3, 8, 20, "fixes/week", "SRE Benchmarks"),
]


def seed_benchmarks(conn: sqlite3.Connection):
    """Заполняет эталонные данные для рейтинга разработчиков."""
    for row in BENCHMARK_DATA:
        conn.execute(
            "INSERT OR IGNORE INTO developer_ranks (metric, p25, p50, p75, p90, p99, unit, source) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            row
        )


def init_db():
    """Initialize SQLite schema."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS xp_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            project TEXT NOT NULL,
            action TEXT NOT NULL,
            xp INTEGER NOT NULL,
            details TEXT,
            session_id TEXT
        );

        CREATE TABLE IF NOT EXISTS achievements (
            id TEXT PRIMARY KEY,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            project TEXT,
            xp_awarded INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            project TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            total_xp INTEGER DEFAULT 0,
            writes INTEGER DEFAULT 0,
            edits INTEGER DEFAULT 0,
            tests_run INTEGER DEFAULT 0,
            commits INTEGER DEFAULT 0,
            agents_spawned INTEGER DEFAULT 0,
            lines_written INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS daily_stats (
            day DATE PRIMARY KEY,
            total_xp INTEGER DEFAULT 0,
            projects TEXT DEFAULT '[]',
            commits INTEGER DEFAULT 0,
            tests INTEGER DEFAULT 0,
            deploys INTEGER DEFAULT 0,
            sentry_fixes INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS quests (
            id TEXT NOT NULL,
            week TEXT NOT NULL,
            completed_at TIMESTAMP,
            xp_awarded INTEGER DEFAULT 0,
            progress_data TEXT DEFAULT '{}',
            PRIMARY KEY (id, week)
        );

        CREATE INDEX IF NOT EXISTS idx_xp_events_ts ON xp_events(ts);
        CREATE INDEX IF NOT EXISTS idx_xp_events_project ON xp_events(project);

        CREATE TABLE IF NOT EXISTS developer_ranks (
            metric TEXT PRIMARY KEY,
            p25 REAL, p50 REAL, p75 REAL, p90 REAL, p99 REAL,
            unit TEXT, source TEXT
        );

        CREATE TABLE IF NOT EXISTS benchmarks (
            metric TEXT NOT NULL,
            period TEXT NOT NULL,
            value REAL NOT NULL,
            percentile INTEGER,
            rank TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (metric, period)
        );
    """)
    seed_benchmarks(conn)
    conn.commit()
    conn.close()


def detect_project(cwd: str = None) -> dict:
    """Detect current project from CWD."""
    config = load_config()
    cwd = cwd or os.getcwd()
    cwd = str(Path(cwd).resolve())

    # Exact match or parent match
    best_match = None
    best_len = 0
    for path, proj in config["projects"].items():
        path_resolved = str(Path(path).resolve())
        if cwd.startswith(path_resolved) and len(path_resolved) > best_len:
            best_match = proj
            best_match["path"] = path
            best_len = len(path_resolved)

    if best_match:
        return best_match

    # Fallback: use directory name
    return {
        "name": Path(cwd).name,
        "icon": "📁",
        "color": "#6B7280",
        "zone": "unknown"
    }


def get_total_xp(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COALESCE(SUM(xp), 0) as total FROM xp_events").fetchone()
    return row["total"]


def get_level(total_xp: int, config: dict) -> dict:
    levels = config["levels"]
    current = levels[0]
    next_level = levels[1] if len(levels) > 1 else None

    for i, lvl in enumerate(levels):
        if total_xp >= lvl["xp"]:
            current = lvl
            next_level = levels[i + 1] if i + 1 < len(levels) else None

    if next_level:
        xp_in_level = total_xp - current["xp"]
        xp_needed = next_level["xp"] - current["xp"]
        progress_pct = min(100, int(xp_in_level / xp_needed * 100))
    else:
        xp_in_level = total_xp - current["xp"]
        xp_needed = 0
        progress_pct = 100

    return {
        "level": current["level"],
        "title": current["title"],
        "color": current["color"],
        "total_xp": total_xp,
        "xp_in_level": xp_in_level,
        "xp_to_next": xp_needed - xp_in_level if next_level else 0,
        "next_title": next_level["title"] if next_level else "MAX",
        "progress_pct": progress_pct
    }


def get_streak(conn: sqlite3.Connection) -> int:
    """Calculate current active streak in days."""
    today = date.today()
    streak = 0
    check_date = today

    # Check if there's any activity today or yesterday (grace period)
    for _ in range(365):
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM xp_events WHERE DATE(ts) = ?",
            (check_date.isoformat(),)
        ).fetchone()

        if row["cnt"] > 0:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            # Allow yesterday gap if today not started yet
            if check_date == today:
                check_date -= timedelta(days=1)
                continue
            break

    return streak


def get_today_xp(conn: sqlite3.Connection) -> int:
    today = date.today().isoformat()
    row = conn.execute(
        "SELECT COALESCE(SUM(xp), 0) as total FROM xp_events WHERE DATE(ts) = ?",
        (today,)
    ).fetchone()
    return row["total"]


def get_session_xp(conn: sqlite3.Connection, session_id: str) -> int:
    row = conn.execute(
        "SELECT COALESCE(SUM(xp), 0) as total FROM xp_events WHERE session_id = ?",
        (session_id,)
    ).fetchone()
    return row["total"]


def get_unlocked_achievements(conn: sqlite3.Connection) -> list:
    rows = conn.execute("SELECT id FROM achievements").fetchall()
    return [r["id"] for r in rows]


def calculate_multiplier(conn, session_id: str = "") -> float:
    """Calculate XP multiplier based on context."""
    config = load_config()
    mults = config.get("xp_multipliers", {})
    multiplier = 1.0

    from datetime import datetime, date
    now = datetime.now()
    today = date.today().isoformat()

    # First session of day
    first_event_today = conn.execute(
        "SELECT COUNT(*) as c FROM xp_events WHERE DATE(ts) = ? AND ts < datetime('now', '-1 minute')",
        (today,)
    ).fetchone()["c"]
    if first_event_today == 0:
        multiplier = max(multiplier, mults.get("first_session_day", 1.5))

    # Active streak bonus
    streak = get_streak(conn)
    if streak >= 3:
        multiplier = max(multiplier, mults.get("streak_active", 1.25))

    return min(multiplier, 3.0)  # Cap at 3x


def add_xp(action: str, xp: int, details: str = "", session_id: str = "") -> int:
    """Add XP event and return total XP."""
    project = detect_project()
    conn = get_db()
    try:
        # Apply multiplier (skip for achievement rewards to avoid double-multiply)
        if action != "achievement_reward":
            mult = calculate_multiplier(conn, session_id)
            xp = max(1, round(xp * mult))

        conn.execute(
            "INSERT INTO xp_events (project, action, xp, details, session_id) VALUES (?, ?, ?, ?, ?)",
            (project["name"], action, xp, details, session_id)
        )
        conn.commit()
        total = get_total_xp(conn)
        return total
    finally:
        conn.close()


def check_and_award_achievements(session_stats: dict = None) -> list:
    """Check achievement conditions and award new ones. Returns list of newly unlocked."""
    config = load_config()
    conn = get_db()
    unlocked = get_unlocked_achievements(conn)
    newly_unlocked = []

    try:
        total_xp = get_total_xp(conn)
        streak = get_streak(conn)

        # Gather stats
        writes = conn.execute("SELECT COUNT(*) as c FROM xp_events WHERE action='Write'").fetchone()["c"]
        deploys = conn.execute("SELECT COUNT(*) as c FROM xp_events WHERE action='bash_deploy'").fetchone()["c"]
        sentry_fixes = conn.execute("SELECT COUNT(*) as c FROM xp_events WHERE action='sentry_fix_detected'").fetchone()["c"]
        agents = conn.execute("SELECT COUNT(*) as c FROM xp_events WHERE action='task_agent_spawn'").fetchone()["c"]

        # Today's projects
        today = date.today().isoformat()
        proj_today = conn.execute(
            "SELECT COUNT(DISTINCT project) as c FROM xp_events WHERE DATE(ts) = ?", (today,)
        ).fetchone()["c"]

        stats = {
            "writes_total": writes,
            "streak_days": streak,
            "deploys_total": deploys,
            "sentry_fixes": sentry_fixes,
            "agents_spawned": agents,
            "projects_today": proj_today,
            **(session_stats or {})
        }

        for ach in config["achievements"]:
            if ach["id"] in unlocked:
                continue

            condition = ach["condition"]
            earned = False

            # Simple condition parser
            if ">=" in condition:
                key, val = condition.split(">=")
                key = key.strip()
                val = int(val.strip())
                if stats.get(key, 0) >= val:
                    earned = True
            elif condition.startswith("project_deploy:"):
                pass  # External trigger

            if earned:
                xp_reward = ach.get("xp_reward", 0)
                project = detect_project()
                conn.execute(
                    "INSERT OR IGNORE INTO achievements (id, project, xp_awarded) VALUES (?, ?, ?)",
                    (ach["id"], project["name"], xp_reward)
                )
                if xp_reward > 0:
                    conn.execute(
                        "INSERT INTO xp_events (project, action, xp, details) VALUES (?, ?, ?, ?)",
                        (project["name"], "achievement_reward", xp_reward, f"Achievement: {ach['name']}")
                    )
                conn.commit()
                newly_unlocked.append(ach)

    finally:
        conn.close()

    return newly_unlocked


def get_project_breakdown(conn: sqlite3.Connection) -> list:
    """XP breakdown by project."""
    rows = conn.execute("""
        SELECT project, SUM(xp) as total_xp, COUNT(*) as events,
               MAX(ts) as last_active
        FROM xp_events
        GROUP BY project
        ORDER BY total_xp DESC
    """).fetchall()
    return [dict(r) for r in rows]


def get_week_stats(conn: sqlite3.Connection) -> dict:
    """Stats for the last 7 days."""
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    rows = conn.execute("""
        SELECT DATE(ts) as day, SUM(xp) as xp, COUNT(*) as events
        FROM xp_events
        WHERE DATE(ts) >= ?
        GROUP BY DATE(ts)
        ORDER BY day
    """, (week_ago,)).fetchall()
    return {r["day"]: {"xp": r["xp"], "events": r["events"]} for r in rows}


def get_recent_achievements(conn: sqlite3.Connection, limit: int = 5) -> list:
    config = load_config()
    rows = conn.execute(
        "SELECT id, unlocked_at FROM achievements ORDER BY unlocked_at DESC LIMIT ?",
        (limit,)
    ).fetchall()

    result = []
    ach_map = {a["id"]: a for a in config["achievements"]}
    for row in rows:
        if row["id"] in ach_map:
            a = ach_map[row["id"]].copy()
            a["unlocked_at"] = row["unlocked_at"]
            result.append(a)
    return result


def render_progress_bar(pct: int, width: int = 20, fill: str = "█", empty: str = "░") -> str:
    filled = int(width * pct / 100)
    return fill * filled + empty * (width - filled)


def get_full_stats() -> dict:
    """Get all stats for dashboard/status display."""
    config = load_config()
    conn = get_db()
    try:
        total_xp = get_total_xp(conn)
        level_info = get_level(total_xp, config)
        streak = get_streak(conn)
        today_xp = get_today_xp(conn)
        projects = get_project_breakdown(conn)
        week = get_week_stats(conn)
        recent_ach = get_recent_achievements(conn)
        unlocked_count = conn.execute("SELECT COUNT(*) as c FROM achievements").fetchone()["c"]
        total_ach = len(config["achievements"])

        # Compare to previous week
        prev_week_start = (date.today() - timedelta(days=14)).isoformat()
        prev_week_end = (date.today() - timedelta(days=7)).isoformat()
        prev_week_xp = conn.execute(
            "SELECT COALESCE(SUM(xp),0) as total FROM xp_events WHERE DATE(ts) >= ? AND DATE(ts) < ?",
            (prev_week_start, prev_week_end)
        ).fetchone()["total"]

        curr_week_xp = sum(v.get("xp", 0) for v in week.values())
        week_delta = curr_week_xp - prev_week_xp
        week_delta_pct = round((week_delta / max(prev_week_xp, 1)) * 100) if prev_week_xp else None

        return {
            "level": level_info,
            "streak": streak,
            "today_xp": today_xp,
            "total_xp": total_xp,
            "projects": projects,
            "week_stats": week,
            "curr_week_xp": curr_week_xp,
            "prev_week_xp": prev_week_xp,
            "week_delta": week_delta,
            "week_delta_pct": week_delta_pct,
            "recent_achievements": recent_ach,
            "achievements_count": f"{unlocked_count}/{total_ach}",
            "config": config
        }
    finally:
        conn.close()


def calculate_rankings(conn: sqlite3.Connection) -> dict:
    """Рассчитывает процентильный рейтинг относительно индустриальных бенчмарков."""
    today = date.today().isoformat()
    week_ago = (date.today() - timedelta(days=7)).isoformat()

    # Собираем актуальные метрики
    metrics = {}

    # Коммиты сегодня
    commits = conn.execute(
        "SELECT COUNT(*) FROM xp_events WHERE action LIKE '%git_commit%' AND DATE(ts) = ?", (today,)
    ).fetchone()[0]
    metrics["commits_per_day"] = commits

    # Файлы созданы сегодня
    writes = conn.execute(
        "SELECT COUNT(*) FROM xp_events WHERE action='Write' AND DATE(ts) = ?", (today,)
    ).fetchone()[0]
    metrics["files_created_per_day"] = writes

    # Файлы отредактированы сегодня
    edits = conn.execute(
        "SELECT COUNT(*) FROM xp_events WHERE action='Edit' AND DATE(ts) = ?", (today,)
    ).fetchone()[0]
    metrics["files_edited_per_day"] = edits

    # Тесты сегодня
    tests = conn.execute(
        "SELECT COUNT(*) FROM xp_events WHERE action LIKE '%test%' AND DATE(ts) = ?", (today,)
    ).fetchone()[0]
    metrics["tests_per_day"] = tests

    # Агенты сегодня
    agents = conn.execute(
        "SELECT COUNT(*) FROM xp_events WHERE action='task_agent_spawn' AND DATE(ts) = ?", (today,)
    ).fetchone()[0]
    metrics["agents_per_day"] = agents

    # XP сегодня
    xp = conn.execute(
        "SELECT COALESCE(SUM(xp), 0) FROM xp_events WHERE DATE(ts) = ?", (today,)
    ).fetchone()[0]
    metrics["xp_per_day"] = xp

    # Стрик
    metrics["streak_days"] = get_streak(conn)

    # Деплои за неделю
    deploys = conn.execute(
        "SELECT COUNT(*) FROM xp_events WHERE action='bash_deploy' AND DATE(ts) >= ?", (week_ago,)
    ).fetchone()[0]
    metrics["deploys_per_week"] = deploys

    # Sentry фиксы за неделю
    fixes = conn.execute(
        "SELECT COUNT(*) FROM xp_events WHERE action='sentry_fix_detected' AND DATE(ts) >= ?", (week_ago,)
    ).fetchone()[0]
    metrics["sentry_fixes_per_week"] = fixes

    # Рассчёт процентилей
    rankings = {}
    benches = conn.execute("SELECT * FROM developer_ranks").fetchall()

    METRIC_LABELS = {
        "commits_per_day": "Коммиты/день",
        "files_created_per_day": "Файлы созданы",
        "files_edited_per_day": "Файлы изменены",
        "tests_per_day": "Тесты/день",
        "agents_per_day": "Агенты/день",
        "xp_per_day": "XP/день",
        "streak_days": "Стрик (дни)",
        "deploys_per_week": "Деплои/неделя",
        "sentry_fixes_per_week": "Sentry фиксы/нед",
    }

    for bench in benches:
        metric = bench["metric"]
        value = metrics.get(metric, 0)

        # Линейная интерполяция процентиля
        if value <= bench["p25"]:
            pct = int(25 * value / max(bench["p25"], 1))
        elif value <= bench["p50"]:
            pct = 25 + int(25 * (value - bench["p25"]) / max(bench["p50"] - bench["p25"], 1))
        elif value <= bench["p75"]:
            pct = 50 + int(25 * (value - bench["p50"]) / max(bench["p75"] - bench["p50"], 1))
        elif value <= bench["p90"]:
            pct = 75 + int(15 * (value - bench["p75"]) / max(bench["p90"] - bench["p75"], 1))
        elif value <= bench["p99"]:
            pct = 90 + int(9 * (value - bench["p90"]) / max(bench["p99"] - bench["p90"], 1))
        else:
            pct = 99

        pct = min(99, max(0, pct))

        # Название ранга
        if pct >= 90:
            rank = "God Tier"
        elif pct >= 75:
            rank = "Elite"
        elif pct >= 50:
            rank = "Senior"
        elif pct >= 25:
            rank = "Mid"
        else:
            rank = "Junior"

        # Эмодзи ранга
        if pct >= 90:
            emoji = "\U0001f3c6"
        elif pct >= 75:
            emoji = "\u26a1"
        elif pct >= 50:
            emoji = "\U0001f4aa"
        elif pct >= 25:
            emoji = "\U0001f527"
        else:
            emoji = "\u26a0\ufe0f"

        rankings[metric] = {
            "value": value,
            "percentile": pct,
            "rank": rank,
            "emoji": emoji,
            "unit": bench["unit"],
            "label": METRIC_LABELS.get(metric, metric),
        }

        # Сохраняем в таблицу benchmarks
        conn.execute("""
            INSERT OR REPLACE INTO benchmarks (metric, period, value, percentile, rank, updated_at)
            VALUES (?, 'daily', ?, ?, ?, datetime('now'))
        """, (metric, value, pct, rank))

    conn.commit()

    # Общий ранг = средний процентиль
    if rankings:
        avg_pct = sum(r["percentile"] for r in rankings.values()) / len(rankings)
    else:
        avg_pct = 0

    if avg_pct >= 90:
        overall = "\U0001f3c6 God Tier"
    elif avg_pct >= 75:
        overall = "\u26a1 Elite"
    elif avg_pct >= 50:
        overall = "\U0001f4aa Senior"
    elif avg_pct >= 25:
        overall = "\U0001f527 Mid"
    else:
        overall = "\u26a0\ufe0f Junior"

    return {
        "metrics": rankings,
        "overall_rank": overall,
        "overall_percentile": int(avg_pct),
        "strengths": [k for k, v in rankings.items() if v["percentile"] >= 75],
        "growth_areas": [k for k, v in rankings.items() if v["percentile"] < 50],
    }


def generate_daily_challenge(conn: sqlite3.Connection, rankings: dict) -> str:
    """Генерирует челлендж на основе самой слабой метрики."""
    growth = rankings.get("growth_areas", [])
    if not growth:
        return "🎯 Challenge: Поддержи свой God Tier уровень — 10+ коммитов сегодня!"

    weakest = growth[0]
    metric_data = rankings["metrics"].get(weakest, {})

    CHALLENGES = {
        "commits_per_day": "Сделай 10+ коммитов сегодня",
        "deploys_per_week": "Сделай 1 деплой сегодня",
        "tests_per_day": "Запусти тесты в 3+ проектах",
        "streak_days": "Продолжи стрик — коммит каждый день",
        "sentry_fixes_per_week": "Закрой 2 Sentry issues",
        "agents_per_day": "Запусти 5+ параллельных агентов",
        "files_created_per_day": "Создай 10+ новых файлов",
    }

    challenge = CHALLENGES.get(weakest, f"Улучши {weakest}")
    current_rank = metric_data.get("rank", "Junior")

    return f"🎯 Daily Challenge: {challenge}\n   Текущий: {current_rank} → Цель: следующий ранг (+100 XP)"


if __name__ == "__main__":
    init_db()
    stats = get_full_stats()
    config = stats["config"]
    lvl = stats["level"]

    bar = render_progress_bar(lvl["progress_pct"])
    print(f"\n🎮 {lvl['title']} | Level {lvl['level']} | XP: {lvl['total_xp']:,}")
    print(f"🔥 Стрик: {stats['streak']} дней | Сегодня: +{stats['today_xp']} XP")
    print(f"🏅 Достижения: {stats['achievements_count']}")

    # Конкурентный рейтинг
    conn = get_db()
    try:
        rankings = calculate_rankings(conn)

        print(f"\n📊 Рейтинг среди разработчиков:")
        for metric, data in rankings["metrics"].items():
            label = data["label"]
            val = data["value"]
            emoji = data["emoji"]
            pct = data["percentile"]
            rank = data["rank"]
            print(f"  {label:<20s} {val:>5} → {emoji} Top {pct}% ({rank})")

        print(f"\n  ОБЩИЙ РАНГ: {rankings['overall_rank']} Developer (Top {rankings['overall_percentile']}%)")

        # Ежедневный челлендж
        challenge = generate_daily_challenge(conn, rankings)
        print(f"\n{challenge}")
    finally:
        conn.close()
