#!/usr/bin/env python3
"""Task tracker: collects tasks from daily reviews, MEMORY.md, gamification.

Usage:
    python3 task-tracker.py              # print to stdout
    python3 task-tracker.py --telegram   # send to Telegram bot
"""

import json
import os
import re
import sqlite3
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
DECAY_DIR = CLAUDE_DIR / "memory" / "decay-30d"
GAMIFY_DB = CLAUDE_DIR / "gamification" / "gamify.db"
GAMIFY_CONFIG = CLAUDE_DIR / "gamification" / "config.json"


def read_recent_daily_reviews(days: int = 3) -> list[str]:
    """Read daily review files from decay directory, extract suggestions."""
    suggestions: list[str] = []
    if not DECAY_DIR.is_dir():
        return suggestions

    today = date.today()
    for i in range(days):
        d = today - timedelta(days=i)
        pattern = f"daily-{d.isoformat()}*"
        matches = list(DECAY_DIR.glob(pattern))
        # Also try alternate naming
        if not matches:
            pattern2 = f"*{d.isoformat()}*"
            matches = list(DECAY_DIR.glob(pattern2))

        for f in matches[:2]:  # max 2 files per day
            try:
                content = f.read_text(encoding="utf-8")
            except OSError:
                continue

            # Extract action items / suggestions
            for line in content.splitlines():
                stripped = line.strip()
                # Lines starting with - [ ], * [ ], TODO, NEXT, ACTION
                if re.match(r"^[-*]\s*\[[ ]\]", stripped):
                    suggestions.append(stripped.lstrip("-* ").lstrip("[ ] "))
                elif stripped.upper().startswith(("TODO:", "NEXT:", "ACTION:")):
                    suggestions.append(stripped)
                elif re.match(r"^[-*]\s+(?:Сделать|Надо|Нужно|Запустить|Проверить|Починить)", stripped):
                    suggestions.append(stripped.lstrip("-* "))

    return suggestions[:5]


def read_memory_tasks() -> tuple[list[str], list[str]]:
    """Read MEMORY.md from CWD for next actions and tech debt."""
    memory_path = Path(os.environ.get("PWD", os.getcwd())) / "MEMORY.md"
    if not memory_path.exists():
        # Fallback to home
        memory_path = Path.home() / "MEMORY.md"
    if not memory_path.exists():
        return [], []

    try:
        content = memory_path.read_text(encoding="utf-8")
    except OSError:
        return [], []

    tasks: list[str] = []
    tech_debt: list[str] = []
    current_section = ""

    for line in content.splitlines():
        stripped = line.strip()
        lower = stripped.lower()

        if stripped.startswith("#"):
            current_section = lower

        if any(kw in current_section for kw in ("next", "todo", "задач", "план", "sprint", "backlog")):
            if re.match(r"^[-*]\s", stripped):
                item = stripped.lstrip("-* ").strip()
                if item and not item.startswith("#"):
                    tasks.append(item)

        if any(kw in current_section for kw in ("debt", "долг", "issue", "проблем", "known")):
            if re.match(r"^[-*]\s", stripped):
                item = stripped.lstrip("-* ").strip()
                if item and not item.startswith("#"):
                    tech_debt.append(item)

    return tasks[:5], tech_debt[:5]


def get_gamification_challenge() -> str:
    """Get daily challenge from gamification DB."""
    if not GAMIFY_DB.exists():
        return ""

    try:
        conn = sqlite3.connect(str(GAMIFY_DB))
        conn.row_factory = sqlite3.Row

        # Get weakest metric for challenge
        today = date.today().isoformat()
        row = conn.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN action LIKE '%test%' THEN 1 ELSE 0 END), 0) as tests,
                COALESCE(SUM(CASE WHEN action LIKE '%commit%' THEN 1 ELSE 0 END), 0) as commits,
                COALESCE(SUM(CASE WHEN action LIKE '%deploy%' THEN 1 ELSE 0 END), 0) as deploys
            FROM xp_events
            WHERE date(ts) = ?
        """, (today,)).fetchone()

        conn.close()

        if not row:
            return "Начни день с коммита!"

        tests = row["tests"]
        commits = row["commits"]
        deploys = row["deploys"]

        if commits == 0:
            return "Сделай первый коммит дня!"
        if tests == 0:
            return "Запусти тесты -- ноль тестов за сегодня!"
        if deploys == 0:
            return "Задеплой что-нибудь сегодня!"
        return "Все метрики на ходу -- продолжай жечь!"

    except Exception:
        return ""


def build_message() -> str:
    """Build the task tracker message."""
    today_str = date.today().strftime("%d.%m.%Y")

    review_tasks = read_recent_daily_reviews()
    memory_tasks, tech_debt = read_memory_tasks()
    challenge = get_gamification_challenge()

    lines = [f"*Задачи на {today_str}:*", ""]

    task_num = 1

    if review_tasks:
        lines.append("_Из daily review:_")
        for t in review_tasks:
            lines.append(f"  {task_num}. {t}")
            task_num += 1
        lines.append("")

    if memory_tasks:
        lines.append("_Из MEMORY.md:_")
        for t in memory_tasks:
            lines.append(f"  {task_num}. {t}")
            task_num += 1
        lines.append("")

    if not review_tasks and not memory_tasks:
        lines.append("  Нет задач в очереди. Проверь MEMORY.md или запусти /daily-review.")
        lines.append("")

    if tech_debt:
        lines.append("*Техдолг:*")
        for td in tech_debt:
            lines.append(f"  - {td}")
        lines.append("")

    if challenge:
        lines.append(f"*Challenge:* {challenge}")

    return "\n".join(lines)


def send_telegram(text: str) -> bool:
    """Send message via Telegram Bot API."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_USER_ID", "")

    # Try config
    if not token or not chat_id:
        if GAMIFY_CONFIG.exists():
            try:
                cfg = json.loads(GAMIFY_CONFIG.read_text(encoding="utf-8"))
                token = token or cfg.get("telegram_bot_token", "")
                chat_id = chat_id or cfg.get("telegram_user_id", "")
            except (json.JSONDecodeError, OSError):
                pass

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
            return resp.status == 200
    except Exception as e:
        print(f"Telegram send failed: {e}", file=sys.stderr)
        return False


def main() -> None:
    to_telegram = "--telegram" in sys.argv

    msg = build_message()

    if to_telegram:
        ok = send_telegram(msg)
        if ok:
            print("Sent to Telegram.")
        else:
            print("Failed. Output:\n")
            print(msg)
    else:
        print(msg)


if __name__ == "__main__":
    main()
