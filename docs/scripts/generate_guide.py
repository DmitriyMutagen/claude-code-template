#!/usr/bin/env python3
"""
Claude Code Infrastructure Guide — Auto-Generator v1.0
Полная регенерация HTML из живых данных ~/.claude/
Запуск: python3 ~/.claude/generate_guide.py
Автозапуск: Stop hook после каждой сессии
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ─── Пути ────────────────────────────────────────────────────────────────────
CLAUDE_DIR = Path.home() / ".claude"
GUIDE_PATH = Path.home() / "Documents" / "Claude-Code-Infrastructure-Guide.html"
GUIDE_TEMPLATE = Path.home() / "Documents" / "template-project" / "docs" / "Claude-Code-Infrastructure-Guide.html"
VERSIONS_DIR = CLAUDE_DIR / "guide_versions"
VERSIONS_DIR.mkdir(exist_ok=True)

# ─── Сбор данных ─────────────────────────────────────────────────────────────

def collect_rules():
    rules_dir = CLAUDE_DIR / "rules"
    rules = []
    if rules_dir.exists():
        for f in sorted(rules_dir.glob("*.md")):
            content = f.read_text(encoding="utf-8")
            # Первая строка после # = описание
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            title = lines[0].lstrip("#").strip() if lines else f.stem
            desc = ""
            for line in lines[1:5]:
                if line and not line.startswith("#") and not line.startswith("```"):
                    desc = line[:100]
                    break
            rules.append({"file": f.stem, "title": title, "desc": desc})
    return rules


def collect_agents():
    agents_dir = CLAUDE_DIR / "agents"
    agents = []
    if agents_dir.exists():
        for f in sorted(agents_dir.glob("*.md")):
            if "archive" in str(f):
                continue
            content = f.read_text(encoding="utf-8")
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            name = f.stem
            desc = ""
            for line in lines[:10]:
                if line.startswith("description:"):
                    desc = line.replace("description:", "").strip()
                    break
                if line and not line.startswith("#") and not line.startswith("---") and len(line) > 20:
                    desc = line[:120]
                    break
            agents.append({"name": name, "desc": desc})
    return agents


def collect_hooks():
    settings_path = CLAUDE_DIR / "settings.json"
    hooks_info = {}
    if settings_path.exists():
        try:
            data = json.loads(settings_path.read_text())
            for event, cmds in data.get("hooks", {}).items():
                hooks_info[event] = len(cmds)
        except Exception:
            pass
    return hooks_info


def collect_skills_custom():
    """Кастомные скиллы Дмитрия из ~/.claude/skills/*/SKILL.md"""
    skills_dir = CLAUDE_DIR / "skills"
    skills = []
    known = {
        "daily-review", "good-morning", "growth-coach", "org-structure",
        "checkpoint", "continue", "new-project", "spec", "review", "audit",
        "deploy-check", "wb-enrich", "wb-qa", "parallel", "xp"
    }
    if skills_dir.exists():
        for skill_dir in sorted(skills_dir.iterdir()):
            if skill_dir.is_dir() and skill_dir.name in known:
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    content = skill_md.read_text(encoding="utf-8")
                    desc_match = re.search(r"description:\s*(.+)", content)
                    desc = desc_match.group(1).strip() if desc_match else ""
                    if not desc:
                        lines = [l.strip() for l in content.split("\n") if l.strip()]
                        for line in lines[3:8]:
                            if line and not line.startswith("#") and not line.startswith("---"):
                                desc = line[:100]
                                break
                    skills.append({"name": skill_dir.name, "desc": desc})
    return skills


def collect_projects():
    """Проекты из GLOBAL_MEMORY.md"""
    gm = CLAUDE_DIR / "memory" / "GLOBAL_MEMORY.md"
    projects = []
    if gm.exists():
        content = gm.read_text(encoding="utf-8")
        # Ищем таблицу проектов
        in_table = False
        for line in content.split("\n"):
            if "| Проект |" in line:
                in_table = True
                continue
            if in_table:
                if line.startswith("|---"):
                    continue
                if line.startswith("|") and "|" in line[1:]:
                    parts = [p.strip() for p in line.split("|")[1:-1]]
                    if len(parts) >= 4:
                        projects.append({
                            "name": parts[0],
                            "path": parts[1],
                            "status": parts[2],
                            "last": parts[3]
                        })
                else:
                    in_table = False
    return projects


def collect_gamification():
    cfg_path = CLAUDE_DIR / "gamification" / "config.json"
    db_path = CLAUDE_DIR / "gamification" / "gamification.db"
    data = {"levels": [], "achievements": [], "current_xp": 0, "current_level": 1, "streak": 0}

    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text())
            data["levels"] = cfg.get("levels", [])
            data["achievements"] = cfg.get("achievements", [])
        except Exception:
            pass

    # Попробуем получить XP из движка
    try:
        result = subprocess.run(
            ["python3", str(CLAUDE_DIR / "gamification" / "engine.py")],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout
        xp_match = re.search(r"(\d[\d,]+)\s*XP", output)
        level_match = re.search(r"Level\s+(\d+)", output)
        streak_match = re.search(r"Стрик:\s*(\d+)", output)
        if xp_match:
            data["current_xp"] = int(xp_match.group(1).replace(",", ""))
        if level_match:
            data["current_level"] = int(level_match.group(1))
        if streak_match:
            data["streak"] = int(streak_match.group(1))
    except Exception:
        pass

    return data


def collect_memory_stats():
    mem_dir = CLAUDE_DIR / "memory"
    stats = {
        "sessions_7d": 0,
        "dailies_30d": 0,
        "permanent": []
    }
    sessions_dir = mem_dir / "decay-7d"
    if sessions_dir.exists():
        stats["sessions_7d"] = len(list(sessions_dir.glob("session-*.md")))

    daily_dir = mem_dir / "decay-30d"
    if daily_dir.exists():
        stats["dailies_30d"] = len(list(daily_dir.glob("daily-*.md")))

    perm_dir = mem_dir / "permanent"
    if perm_dir.exists():
        stats["permanent"] = [f.name for f in perm_dir.glob("*.md")]

    return stats


def get_version():
    """Читаем текущую версию или создаём 1.0"""
    ver_file = VERSIONS_DIR / "current_version.txt"
    if ver_file.exists():
        return ver_file.read_text().strip()
    return "3.0"


def bump_version(version: str) -> str:
    parts = version.split(".")
    if len(parts) == 2:
        return f"{parts[0]}.{int(parts[1]) + 1}"
    return version


def save_changelog_entry(version: str, changes: list[str]):
    log_file = VERSIONS_DIR / "CHANGELOG.md"
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## v{version} — {today}\n" + "\n".join(f"- {c}" for c in changes) + "\n"
    if log_file.exists():
        existing = log_file.read_text()
        log_file.write_text(entry + existing)
    else:
        log_file.write_text(f"# Infrastructure Guide Changelog\n{entry}")


def detect_changes(prev_data: dict, curr_data: dict) -> list[str]:
    """Находим что изменилось"""
    changes = []

    prev_rules = set(r["file"] for r in prev_data.get("rules", []))
    curr_rules = set(r["file"] for r in curr_data.get("rules", []))
    new_rules = curr_rules - prev_rules
    if new_rules:
        changes.append(f"Новые правила: {', '.join(new_rules)}")

    prev_agents = set(a["name"] for a in prev_data.get("agents", []))
    curr_agents = set(a["name"] for a in curr_data.get("agents", []))
    new_agents = curr_agents - prev_agents
    if new_agents:
        changes.append(f"Новые агенты: {', '.join(new_agents)}")

    prev_skills = set(s["name"] for s in prev_data.get("skills", []))
    curr_skills = set(s["name"] for s in curr_data.get("skills", []))
    new_skills = curr_skills - prev_skills
    if new_skills:
        changes.append(f"Новые скиллы: {', '.join(new_skills)}")

    curr_xp = curr_data.get("gamification", {}).get("current_xp", 0)
    prev_xp = prev_data.get("gamification", {}).get("current_xp", 0)
    if curr_xp != prev_xp and curr_xp > 0:
        changes.append(f"XP: {prev_xp:,} → {curr_xp:,} (+{curr_xp - prev_xp:,})")

    if not changes:
        changes.append("Автообновление статистики")

    return changes


# ─── HTML Генерация ───────────────────────────────────────────────────────────

def gen_rules_html(rules: list) -> str:
    rows = ""
    for r in rules:
        name = r["file"].replace(".md", "")
        title = r["title"][:60]
        desc = r["desc"][:100] if r["desc"] else "—"
        rows += f"""        <tr>
          <td><code>~/.claude/rules/{r['file']}</code></td>
          <td>{title}</td>
          <td>{desc}</td>
        </tr>\n"""
    return f"""<table class="data-table">
      <thead><tr><th>Файл</th><th>Название</th><th>Описание</th></tr></thead>
      <tbody>
{rows}      </tbody>
    </table>"""


def gen_agents_html(agents: list) -> str:
    cards = ""
    for a in agents:
        desc = a["desc"][:120] if a["desc"] else "Специализированный агент"
        cards += f"""      <div class="agent-card">
        <div class="agent-name">{a['name']}</div>
        <div class="agent-desc">{desc}</div>
      </div>\n"""
    return f"""<div class="agents-grid">
{cards}    </div>"""


def gen_skills_html(skills: list) -> str:
    rows = ""
    for s in skills:
        desc = s["desc"][:100] if s["desc"] else "—"
        rows += f"""        <tr>
          <td><code>/{s['name']}</code></td>
          <td>{desc}</td>
        </tr>\n"""
    return f"""<table class="data-table">
      <thead><tr><th>Команда</th><th>Описание</th></tr></thead>
      <tbody>
{rows}      </tbody>
    </table>"""


def gen_hooks_html(hooks: dict) -> str:
    rows = ""
    hook_descriptions = {
        "SessionStart": "Инициализация сессии: баннер, XP снапшот, CL v2.1",
        "PreToolUse": "Блокировка опасных операций (push main, .env запись)",
        "PostToolUse": "Трекинг XP, CL v2.1 наблюдения, auto-commit",
        "Stop": "Сохранение сессии, геймификация итоги, Telegram уведомление",
        "UserPromptSubmit": "Preflight check: Context7, Exa, tier classification",
        "Notification": "Уведомления о долгих операциях",
        "PreCompact": "Auto-checkpoint перед сжатием контекста"
    }
    for event, count in hooks.items():
        desc = hook_descriptions.get(event, "")
        rows += f"""        <tr>
          <td><code>{event}</code></td>
          <td class="badge">{count} хуков</td>
          <td>{desc}</td>
        </tr>\n"""
    return f"""<table class="data-table">
      <thead><tr><th>Событие</th><th>Кол-во</th><th>Назначение</th></tr></thead>
      <tbody>
{rows}      </tbody>
    </table>"""


def gen_projects_html(projects: list) -> str:
    cards = ""
    status_colors = {"🟢": "#10B981", "🟡": "#F59E0B", "🔴": "#EF4444"}
    for p in projects:
        color = "#6B7280"
        for emoji, c in status_colors.items():
            if emoji in p["status"]:
                color = c
                break
        cards += f"""      <div class="project-card" style="border-left-color:{color}">
        <div class="project-name">{p['name']}</div>
        <div class="project-path">{p['path']}</div>
        <div class="project-status">{p['status']}</div>
        <div class="project-last">{p['last'][:80]}</div>
      </div>\n"""
    return f"""<div class="projects-grid">
{cards}    </div>"""


def gen_gamification_html(gm: dict) -> str:
    levels = gm.get("levels", [])
    curr_level = gm.get("current_level", 1)
    curr_xp = gm.get("current_xp", 0)
    streak = gm.get("streak", 0)

    # Find next level XP
    next_xp = 0
    curr_title = "Unknown"
    for lv in levels:
        if lv["level"] == curr_level:
            curr_title = lv["title"]
        if lv["level"] == curr_level + 1:
            next_xp = lv["xp"]

    curr_start = 0
    for lv in levels:
        if lv["level"] == curr_level:
            curr_start = lv["xp"]

    progress = 0
    if next_xp > curr_start:
        progress = int((curr_xp - curr_start) / (next_xp - curr_start) * 100)
        progress = max(0, min(100, progress))

    achievements = gm.get("achievements", [])
    ach_html = ""
    for ach in achievements[:12]:
        hidden_class = "achievement hidden-ach" if ach.get("hidden") else "achievement"
        ach_html += f"""<div class="{hidden_class}" title="{ach.get('desc','')}">
          <span>{ach.get('name','')}</span>
          <span class="xp-badge">+{ach.get('xp_reward', 0)} XP</span>
        </div>\n"""

    return f"""<div class="gm-stats">
      <div class="gm-level">{curr_title}</div>
      <div class="gm-xp">⚡ {curr_xp:,} XP | Streak: 🔥{streak}д</div>
      <div class="progress-bar">
        <div class="progress-fill" style="width:{progress}%"></div>
      </div>
      <div class="progress-label">{progress}% до Level {curr_level+1} ({next_xp:,} XP)</div>
    </div>
    <h3>Ачивки (топ-12)</h3>
    <div class="achievements-grid">
{ach_html}    </div>"""


def gen_memory_html(stats: dict) -> str:
    perm = stats.get("permanent", [])
    perm_items = "".join(f"<li><code>{p}</code></li>" for p in perm)
    return f"""<div class="memory-stats">
      <div class="stat-item">📂 Сессий (7д): <strong>{stats['sessions_7d']}</strong></div>
      <div class="stat-item">📅 Daily reviews (30д): <strong>{stats['dailies_30d']}</strong></div>
      <div class="stat-item">💾 Permanent файлов: <strong>{len(perm)}</strong></div>
    </div>
    <h4>Permanent файлы:</h4>
    <ul class="perm-list">{perm_items}</ul>"""


def gen_changelog_html(changelog_path: Path) -> str:
    if not changelog_path.exists():
        return "<p>История обновлений пуста</p>"
    content = changelog_path.read_text(encoding="utf-8")
    entries = re.findall(r"## (v[\d.]+) — ([^\n]+)\n((?:- [^\n]+\n?)*)", content)
    html = ""
    for version, date, items in entries[:10]:
        items_html = "".join(f"<li>{i.lstrip('- ')}</li>" for i in items.strip().split("\n") if i)
        html += f"""<div class="changelog-entry">
      <span class="version-badge">{version}</span>
      <span class="date">{date}</span>
      <ul>{items_html}</ul>
    </div>\n"""
    return html if html else "<p>Нет записей</p>"


# ─── Инжект в HTML ────────────────────────────────────────────────────────────

def inject_section(html: str, section_id: str, content: str) -> tuple[str, bool]:
    """Находит AUTO маркеры и заменяет содержимое"""
    start_marker = f"<!-- AUTO:{section_id} START -->"
    end_marker = f"<!-- AUTO:{section_id} END -->"
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        re.DOTALL
    )
    new_content = f"{start_marker}\n{content}\n{end_marker}"
    if start_marker in html:
        new_html = pattern.sub(new_content, html)
        return new_html, True
    return html, False


def update_meta(html: str, version: str, generated_at: str) -> str:
    """Обновляем версию и дату в HTML"""
    html = re.sub(r'id="guide-version">[^<]+<', f'id="guide-version">v{version}<', html)
    html = re.sub(r'id="guide-updated">[^<]+<', f'id="guide-updated">{generated_at}<', html)
    html = re.sub(r'<meta name="guide-version" content="[^"]*"',
                  f'<meta name="guide-version" content="{version}"', html)
    return html


# ─── Главная функция ──────────────────────────────────────────────────────────

def main():
    print("🔄 Generating Infrastructure Guide...")

    # 1. Загружаем предыдущие данные для diff
    prev_data_file = VERSIONS_DIR / "last_data.json"
    prev_data = {}
    if prev_data_file.exists():
        try:
            prev_data = json.loads(prev_data_file.read_text())
        except Exception:
            pass

    # 2. Собираем свежие данные
    print("  📊 Collecting data...")
    curr_data = {
        "rules": collect_rules(),
        "agents": collect_agents(),
        "hooks": collect_hooks(),
        "skills": collect_skills_custom(),
        "projects": collect_projects(),
        "gamification": collect_gamification(),
        "memory": collect_memory_stats(),
    }

    # 3. Определяем изменения
    changes = detect_changes(prev_data, curr_data)
    print(f"  📝 Changes: {changes}")

    # 4. Версия
    version = get_version()
    new_version = bump_version(version)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 5. Читаем текущий HTML
    html_path = GUIDE_PATH
    if not html_path.exists() and GUIDE_TEMPLATE.exists():
        html_path = GUIDE_TEMPLATE
    if not html_path.exists():
        print("❌ HTML template not found")
        sys.exit(1)

    html = html_path.read_text(encoding="utf-8")
    print(f"  📄 HTML loaded: {len(html)} chars")

    # 6. Инжектируем секции
    sections_updated = []

    html, ok = inject_section(html, "rules", gen_rules_html(curr_data["rules"]))
    if ok: sections_updated.append("rules")

    html, ok = inject_section(html, "agents", gen_agents_html(curr_data["agents"]))
    if ok: sections_updated.append("agents")

    html, ok = inject_section(html, "hooks", gen_hooks_html(curr_data["hooks"]))
    if ok: sections_updated.append("hooks")

    html, ok = inject_section(html, "skills", gen_skills_html(curr_data["skills"]))
    if ok: sections_updated.append("skills")

    html, ok = inject_section(html, "projects", gen_projects_html(curr_data["projects"]))
    if ok: sections_updated.append("projects")

    html, ok = inject_section(html, "gamification", gen_gamification_html(curr_data["gamification"]))
    if ok: sections_updated.append("gamification")

    html, ok = inject_section(html, "memory", gen_memory_html(curr_data["memory"]))
    if ok: sections_updated.append("memory")

    html, ok = inject_section(html, "changelog", gen_changelog_html(VERSIONS_DIR / "CHANGELOG.md"))
    if ok: sections_updated.append("changelog")

    # 7. Обновляем мета
    html = update_meta(html, new_version, generated_at)

    # 8. Сохраняем
    GUIDE_PATH.write_text(html, encoding="utf-8")
    if GUIDE_TEMPLATE.exists():
        GUIDE_TEMPLATE.write_text(html, encoding="utf-8")

    # 9. Сохраняем версию и данные
    (VERSIONS_DIR / "current_version.txt").write_text(new_version)
    prev_data_file.write_text(json.dumps(curr_data, ensure_ascii=False, indent=2))

    # 10. Changelog
    save_changelog_entry(new_version, changes)

    # 11. Backup версии
    backup_path = VERSIONS_DIR / f"guide-v{new_version}-{datetime.now().strftime('%Y%m%d-%H%M')}.html"
    backup_path.write_text(html, encoding="utf-8")

    # Ротация — оставляем 10 backup
    backups = sorted(VERSIONS_DIR.glob("guide-v*.html"), key=lambda f: f.stat().st_mtime)
    while len(backups) > 10:
        backups[0].unlink()
        backups = backups[1:]

    print(f"  ✅ Sections updated: {sections_updated}")
    print(f"  📦 Version: {version} → {new_version}")
    print(f"  💾 Saved to: {GUIDE_PATH}")
    print(f"  🔖 Backup: {backup_path.name}")
    print(f"  📝 Changes: {', '.join(changes)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
