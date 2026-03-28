#!/usr/bin/env python3
"""
Learning Coach — Elite Gap Analysis
Анализирует текущий уровень и показывает что делать для Top 0.1%

Usage:
  python3 learning_coach.py
  python3 learning_coach.py --telegram
"""
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

GAMIFY_DIR = Path.home() / ".claude" / "gamification"


def load_json(filename: str) -> dict:
    path = GAMIFY_DIR / filename
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def get_bar(value: float, max_value: float, width: int = 10) -> str:
    filled = int((value / max_value) * width) if max_value > 0 else 0
    filled = min(filled, width)
    return "█" * filled + "░" * (width - filled)


def format_comparison(mine: float, target: float, unit: str = "", lower_is_better: bool = False) -> str:
    """
    lower_is_better=True для метрик типа "время" — там чем меньше, тем лучше.
    """
    if lower_is_better:
        # Elite: mine <= target; Gap: mine >> target
        if target > 0:
            ratio = mine / target
        else:
            ratio = 1.0
        if ratio <= 1.0:
            pct = 100.0
        else:
            pct = max(0.0, 100.0 - (ratio - 1.0) * 50)
    else:
        pct = (mine / target * 100) if target > 0 else 0

    if pct >= 80:
        status = "✅"
        rank = "Elite"
    elif pct >= 50:
        status = "🟡"
        rank = "Mid"
    elif pct >= 20:
        status = "⚠️"
        rank = "Below"
    else:
        status = "❌"
        rank = "Gap"
    return f"{status} {mine}{unit} / {target}{unit} ({pct:.0f}%) — {rank}"


def build_report(progress: dict, benchmarks: dict) -> str:
    lines = []
    sep = "━" * 52

    lines.append("")
    lines.append(sep)
    lines.append("  🏛️  VIRTUAL ELITE IT COMPANY — Learning Coach")
    lines.append(sep)

    # Skill Tree
    assessments = progress.get("skill_assessments", {})
    if assessments:
        lines.append("")
        lines.append("📊 SKILL TREE:")
        skill_icons: dict[str, str] = {
            "architecture": "🏗️  Архитектура",
            "development":  "💻 Разработка",
            "quality":      "🧪 Качество",
            "devops":       "🚀 DevOps",
            "management":   "📋 Управление",
            "ai_dev":       "🤖 AI-Dev",
            "seo":          "📈 SEO",
        }
        for key, label in skill_icons.items():
            if key in assessments:
                lvl = assessments[key]["level"]
                trend = assessments[key].get("trend", "+0")
                bar = get_bar(lvl, 5, 8)
                lines.append(f"  {label:<22} [{bar}] {lvl}/5  {trend}")

    # Elite Benchmarks
    comparisons = progress.get("elite_comparisons", {})
    if comparisons:
        lines.append("")
        lines.append("🏆 ELITE BENCHMARKS (ты vs Top-100):")
        comp_meta: dict[str, tuple[str, bool]] = {
            "commits_per_day":  ("Commits/day",     False),
            "tests_per_day":    ("Tests/day",        False),
            "deploys_per_week": ("Deploys/week",     False),
            "adr_coverage":     ("ADR coverage %",   False),
            "ship_speed_hours": ("Ship speed (h)",   True),   # меньше = лучше
        }
        for key, (label, lower) in comp_meta.items():
            if key in comparisons:
                c = comparisons[key]
                source = c.get("source", "—")
                formatted = format_comparison(c["mine"], c["target"], lower_is_better=lower)
                lines.append(f"  {label:<24} {formatted}  [{source}]")

    # Active Learning Tracks
    tracks = progress.get("tracks_progress", {})
    if tracks:
        lines.append("")
        lines.append("🎯 ACTIVE LEARNING TRACKS:")
        for track_id, track in tracks.items():
            lines.append(f"")
            lines.append(f"  📚 {track['name']}")
            lines.append(f"     Следующий шаг: {track.get('next_action', 'Обновить прогресс')}")
            lines.append(f"     XP заработано: {track.get('xp_earned', 0)}")

    # Gap Analysis — Top 3 priorities
    lines.append("")
    lines.append("⚡ ТОП-3 ДЕЙСТВИЯ ПРЯМО СЕЙЧАС:")

    priorities: list[dict] = []

    adr_cov = comparisons.get("adr_coverage", {}).get("mine", 100)
    if adr_cov < 50:
        priorities.append({
            "action": "Создай docs/adr/ в Aragant",
            "cmd": "mkdir -p ~/Documents/marketai/marketai/docs/adr",
            "time": "20 мин",
            "xp": "+50 XP",
            "impact": "Chief Architect +8%",
        })

    dep_week = comparisons.get("deploys_per_week", {}).get("mine", 10)
    if dep_week < 3:
        priorities.append({
            "action": "Настрой push-to-deploy CI/CD",
            "cmd": "claude '/ci-pipeline'",
            "time": "1 ч",
            "xp": "+100 XP",
            "impact": "CTO +15%",
        })

    tests_day = comparisons.get("tests_per_day", {}).get("mine", 20)
    if tests_day < 10:
        priorities.append({
            "action": "Запусти pytest --cov в Aragant",
            "cmd": "cd ~/Documents/marketai/marketai && pytest tests/ --cov=src/",
            "time": "10 мин",
            "xp": "+40 XP",
            "impact": "Quality +5%",
        })

    ship_target = comparisons.get("ship_speed_hours", {}).get("target", 4)
    ship_hours = comparisons.get("ship_speed_hours", {}).get("mine", 0)
    if ship_hours > ship_target * 3:
        priorities.append({
            "action": "Разбей следующую задачу на <4h деплой-цикл",
            "cmd": "claude '/blueprint' + '/closed-loop-delivery'",
            "time": "15 мин план",
            "xp": "+100 XP при деплое",
            "impact": "Solo Founder +20%",
        })

    # Fallback
    if not priorities:
        priorities = [
            {
                "action": "Запусти /growth-coach для полного анализа",
                "cmd": "claude '/growth-coach'",
                "time": "5 мин",
                "xp": "+20 XP",
                "impact": "Оценка уровня",
            },
            {
                "action": "Обнови learning_progress.json с реальными данными",
                "cmd": f"edit {GAMIFY_DIR}/learning_progress.json",
                "time": "10 мин",
                "xp": "+10 XP",
                "impact": "Точность анализа",
            },
        ]

    for i, p in enumerate(priorities[:3], 1):
        lines.append(f"")
        lines.append(f"  {i}. {p['action']}")
        lines.append(f"     $ {p['cmd']}")
        lines.append(f"     ⏱️  {p['time']} | {p['xp']} | {p['impact']}")

    lines.append("")
    lines.append(sep)
    lines.append(f"  Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(sep)
    lines.append("")

    return "\n".join(lines)


def send_telegram(text: str, bot_token: str, user_id: str) -> bool:
    """Отправляет сообщение в Telegram."""
    try:
        import urllib.request
        import urllib.parse

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": user_id,
            "text": text,
            "parse_mode": "HTML",
        }).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception as e:
        print(f"[telegram] ошибка отправки: {e}", file=sys.stderr)
        return False


def run() -> None:
    parser = argparse.ArgumentParser(description="Elite Learning Coach")
    parser.add_argument("--telegram", action="store_true", help="Отправить отчёт в Telegram")
    args = parser.parse_args()

    progress = load_json("learning_progress.json")
    benchmarks = load_json("elite_benchmarks.json")

    if not progress:
        print("learning_progress.json не найден. Создай его сначала.", file=sys.stderr)
        sys.exit(1)

    report = build_report(progress, benchmarks)
    print(report)

    if args.telegram:
        config = load_json("config.json")
        bot_token = config.get("telegram_bot_token", "")
        user_id = config.get("telegram_user_id", "")
        if bot_token and user_id:
            # Telegram не любит Unicode-блоки в обычном тексте — отправляем как есть
            ok = send_telegram(f"<pre>{report}</pre>", bot_token, user_id)
            if ok:
                print("[telegram] отчёт отправлен")
            else:
                print("[telegram] не удалось отправить", file=sys.stderr)
        else:
            print("[telegram] bot_token или user_id не найдены в config.json", file=sys.stderr)


if __name__ == "__main__":
    run()
