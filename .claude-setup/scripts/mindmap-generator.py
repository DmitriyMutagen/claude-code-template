#!/usr/bin/env python3
"""
Генератор интерактивных HTML mind map на базе markmap.js.
Stdlib only -- никаких зависимостей.

Usage:
    python3 mindmap-generator.py architecture    # из CLAUDE.md + структура директорий
    python3 mindmap-generator.py tasks           # из MEMORY.md + git log
    python3 mindmap-generator.py decisions       # из docs/adr/
    python3 mindmap-generator.py project [path]  # полный обзор проекта
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #1a1b26; }}
  svg.markmap {{ width: 100%; height: 100vh; }}
  .controls {{
    position: fixed; top: 12px; right: 16px; z-index: 10;
    display: flex; gap: 8px;
  }}
  .controls button {{
    background: #24283b; color: #a9b1d6; border: 1px solid #414868;
    border-radius: 6px; padding: 6px 14px; cursor: pointer; font-size: 13px;
  }}
  .controls button:hover {{ background: #414868; }}
  .info {{
    position: fixed; bottom: 12px; left: 16px; z-index: 10;
    color: #565f89; font-family: monospace; font-size: 11px;
  }}
</style>
</head>
<body>
<div class="controls">
  <button onclick="location.reload()">Обновить</button>
</div>
<div class="info">{footer}</div>
<div class="markmap">
<script type="text/template">
---
markmap:
  colorFreezeLevel: 3
  maxWidth: 300
  initialExpandLevel: 3
  color:
    - '#7aa2f7'
    - '#bb9af7'
    - '#7dcfff'
    - '#9ece6a'
    - '#e0af68'
    - '#f7768e'
---

{markdown}
</script>
</div>
<script src="https://cdn.jsdelivr.net/npm/markmap-autoloader"></script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

IGNORED_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".mypy_cache",
    ".ruff_cache", ".pytest_cache", ".next", "dist", "build", ".tox",
    ".claude", ".serena", ".eggs", "*.egg-info",
}

IGNORED_FILES = {
    ".DS_Store", "Thumbs.db", ".env", ".env.local",
}


def run_cmd(cmd: list[str], cwd: Optional[str] = None) -> str:
    """Run a shell command, return stdout or empty string on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10, cwd=cwd
        )
        return result.stdout.strip()
    except Exception:
        return ""


def read_file(path: str | Path) -> str:
    """Read file contents, return empty string on failure."""
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def escape_md(text: str) -> str:
    """Escape characters that could break markmap markdown."""
    return text.replace("`", "'").replace("#", "\\#")


def ensure_output_dir(project_root: Path) -> Path:
    """Create docs/maps/ directory, return its path."""
    out = project_root / "docs" / "maps"
    out.mkdir(parents=True, exist_ok=True)
    return out


def save_html(output_dir: Path, name: str, title: str, markdown: str) -> Path:
    """Render markdown into HTML template and save."""
    today = date.today().isoformat()
    filename = f"{name}-{today}.html"
    filepath = output_dir / filename

    footer = f"{title} | {today} | mindmap-generator.py"
    html = HTML_TEMPLATE.format(
        title=title, footer=footer, markdown=markdown
    )
    filepath.write_text(html, encoding="utf-8")
    return filepath


def list_tree(root: Path, prefix: str = "", depth: int = 0, max_depth: int = 3) -> list[str]:
    """Return a list of markdown bullet lines representing directory tree."""
    if depth > max_depth:
        return []
    lines: list[str] = []
    try:
        entries = sorted(root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return []

    for entry in entries:
        name = entry.name
        if name in IGNORED_DIRS or name in IGNORED_FILES:
            continue
        if name.startswith(".") and depth == 0:
            continue
        if entry.is_dir():
            if any(name.endswith(suf) for suf in (".egg-info",)):
                continue
            lines.append(f"{'#' * (depth + 3)} {name}/")
            lines.extend(list_tree(entry, prefix, depth + 1, max_depth))
        elif depth < max_depth:
            lines.append(f"{'#' * (depth + 3)} {name}")
    return lines


def parse_claude_md(content: str) -> dict[str, list[str]]:
    """Extract key sections from CLAUDE.md content."""
    sections: dict[str, list[str]] = {}
    current_section = ""
    for line in content.splitlines():
        if line.startswith("## "):
            current_section = line.lstrip("# ").strip()
            sections[current_section] = []
        elif current_section and line.strip():
            sections[current_section].append(line.strip())
    return sections


def parse_memory_md(content: str) -> dict[str, list[str]]:
    """Extract sections from MEMORY.md."""
    sections: dict[str, list[str]] = {}
    current = ""
    for line in content.splitlines():
        if line.startswith("## "):
            current = line.lstrip("# ").strip()
            sections[current] = []
        elif line.startswith("### ") and current:
            sections[current].append(line.lstrip("# ").strip())
        elif current and line.strip().startswith("- "):
            sections[current].append(line.strip())
    return sections


def extract_tech_stack(claude_sections: dict[str, list[str]]) -> list[str]:
    """Try to find tech stack info from CLAUDE.md sections."""
    keywords = ["stack", "tech", "стек", "технолог"]
    for key, vals in claude_sections.items():
        if any(k in key.lower() for k in keywords):
            return vals
    return []


# ---------------------------------------------------------------------------
# Mode: architecture
# ---------------------------------------------------------------------------

def gen_architecture(project_root: Path) -> str:
    """Generate architecture mind map markdown."""
    project_name = project_root.name or "Проект"
    lines = [f"# {project_name} -- Архитектура"]

    # CLAUDE.md info
    claude_path = project_root / "CLAUDE.md"
    if not claude_path.exists():
        claude_path = project_root / ".claude" / "CLAUDE.md"

    claude_content = read_file(claude_path)
    if claude_content:
        sections = parse_claude_md(claude_content)

        # Tech stack
        stack = extract_tech_stack(sections)
        if stack:
            lines.append("## Технологии")
            for item in stack[:15]:
                clean = item.lstrip("- *").strip()
                if clean:
                    lines.append(f"### {clean[:80]}")

        # Key sections
        interesting = ["Architecture", "Архитектура", "Key Directories",
                       "Overview", "Current Sprint", "Running"]
        for sec_name, vals in sections.items():
            if any(k.lower() in sec_name.lower() for k in interesting):
                lines.append(f"## {sec_name}")
                for v in vals[:10]:
                    clean = v.lstrip("- *").strip()
                    if clean and not clean.startswith("```"):
                        lines.append(f"### {clean[:80]}")

    # Directory structure
    lines.append("## Структура проекта")
    for key_dir in ["src", "lib", "app", "tests", "docs", "scripts", "config"]:
        dp = project_root / key_dir
        if dp.is_dir():
            lines.append(f"### {key_dir}/")
            lines.extend(list_tree(dp, depth=1, max_depth=3))

    # Top-level config files
    config_files = []
    for f in sorted(project_root.iterdir()):
        if f.is_file() and f.suffix in (".toml", ".json", ".yaml", ".yml", ".cfg", ".ini"):
            if not f.name.startswith("."):
                config_files.append(f.name)
    if config_files:
        lines.append("## Конфигурация")
        for cf in config_files[:10]:
            lines.append(f"### {cf}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mode: tasks
# ---------------------------------------------------------------------------

def gen_tasks(project_root: Path) -> str:
    """Generate tasks mind map from MEMORY.md + git log."""
    project_name = project_root.name or "Проект"
    lines = [f"# {project_name} -- Задачи"]

    # MEMORY.md
    memory_path = project_root / "MEMORY.md"
    memory_content = read_file(memory_path)
    if memory_content:
        sections = parse_memory_md(memory_content)

        # Categorize sections
        done_keys = ["done", "готово", "completed", "завершено", "выполнено"]
        progress_keys = ["progress", "текущ", "sprint", "спринт", "working", "in progress"]
        todo_keys = ["todo", "план", "plan", "backlog", "next", "следующ"]
        blocker_keys = ["block", "issue", "проблем", "баг", "bug", "known"]

        categorized = {
            "Выполнено": [],
            "В работе": [],
            "Запланировано": [],
            "Блокеры / Проблемы": [],
            "Прочее": [],
        }

        for sec_name, vals in sections.items():
            sec_lower = sec_name.lower()
            target = "Прочее"
            if any(k in sec_lower for k in done_keys):
                target = "Выполнено"
            elif any(k in sec_lower for k in progress_keys):
                target = "В работе"
            elif any(k in sec_lower for k in todo_keys):
                target = "Запланировано"
            elif any(k in sec_lower for k in blocker_keys):
                target = "Блокеры / Проблемы"
            categorized[target].append((sec_name, vals))

        for cat, sec_list in categorized.items():
            if sec_list:
                lines.append(f"## {cat}")
                for sec_name, vals in sec_list:
                    lines.append(f"### {sec_name}")
                    for v in vals[:10]:
                        clean = v.lstrip("- *[]xX ").strip()
                        if clean:
                            lines.append(f"#### {clean[:80]}")
    else:
        lines.append("## MEMORY.md не найден")

    # Git log
    git_log = run_cmd(
        ["git", "log", "--oneline", "--no-decorate", "-20"],
        cwd=str(project_root),
    )
    if git_log:
        lines.append("## Последние коммиты")
        for gl_line in git_log.splitlines():
            parts = gl_line.split(" ", 1)
            if len(parts) == 2:
                sha, msg = parts
                lines.append(f"### {escape_md(msg)} ({sha[:7]})")
            else:
                lines.append(f"### {escape_md(gl_line)}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mode: decisions
# ---------------------------------------------------------------------------

def gen_decisions(project_root: Path) -> str:
    """Generate decisions mind map from docs/adr/."""
    project_name = project_root.name or "Проект"
    lines = [f"# {project_name} -- Решения (ADR)"]

    adr_dir = project_root / "docs" / "adr"
    if not adr_dir.is_dir():
        lines.append("## docs/adr/ не найден")
        lines.append("### Создайте ADR-файлы для отслеживания решений")
        return "\n".join(lines)

    adrs: list[dict[str, str]] = []
    for f in sorted(adr_dir.iterdir()):
        if f.suffix in (".md", ".txt"):
            content = read_file(f)
            adr: dict[str, str] = {"file": f.name, "title": f.stem}
            for line in content.splitlines():
                lower = line.lower().strip()
                if lower.startswith("# "):
                    adr["title"] = line.lstrip("# ").strip()
                elif "статус" in lower or "status" in lower:
                    val = line.split(":", 1)[-1].strip()
                    adr["status"] = val
                elif "дата" in lower or "date" in lower:
                    val = line.split(":", 1)[-1].strip()
                    adr["date"] = val
                elif "решение" in lower or "decision" in lower:
                    val = line.split(":", 1)[-1].strip()
                    if val:
                        adr["decision"] = val
            adrs.append(adr)

    # Group by status
    by_status: dict[str, list[dict[str, str]]] = {}
    for adr in adrs:
        status = adr.get("status", "неизвестно")
        by_status.setdefault(status, []).append(adr)

    status_labels = {
        "принято": "Принятые",
        "accepted": "Принятые",
        "отклонено": "Отклоненные",
        "rejected": "Отклоненные",
        "proposed": "Предложенные",
        "предложено": "Предложенные",
        "deprecated": "Устаревшие",
    }

    for status, adr_list in by_status.items():
        label = status_labels.get(status.lower(), status)
        lines.append(f"## {label}")
        for adr in adr_list:
            title = escape_md(adr["title"])
            lines.append(f"### {title}")
            if "date" in adr:
                lines.append(f"#### {adr['date']}")
            if "decision" in adr:
                lines.append(f"#### {escape_md(adr['decision'][:100])}")

    if not adrs:
        lines.append("## Пусто")
        lines.append("### ADR-файлы не найдены в docs/adr/")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mode: project (all combined)
# ---------------------------------------------------------------------------

def gen_project(project_root: Path) -> str:
    """Generate full project overview combining all modes."""
    project_name = project_root.name or "Проект"
    lines = [f"# {project_name} -- Полный обзор"]

    # Architecture section (inline, not as separate top-level)
    arch = gen_architecture(project_root)
    # Strip the top-level header and shift all headings down one level
    for line in arch.splitlines()[1:]:
        if line.startswith("#"):
            lines.append("#" + line)
        elif line.strip():
            lines.append(line)

    # Tasks section
    tasks = gen_tasks(project_root)
    for line in tasks.splitlines()[1:]:
        if line.startswith("#"):
            lines.append("#" + line)
        elif line.strip():
            lines.append(line)

    # Decisions section
    decisions = gen_decisions(project_root)
    for line in decisions.splitlines()[1:]:
        if line.startswith("#"):
            lines.append("#" + line)
        elif line.strip():
            lines.append(line)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

MODES = {
    "architecture": ("Архитектура", gen_architecture),
    "tasks": ("Задачи", gen_tasks),
    "decisions": ("Решения", gen_decisions),
    "project": ("Обзор проекта", gen_project),
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        print("Режимы:", ", ".join(MODES.keys()))
        sys.exit(0)

    mode = sys.argv[1].lower()
    if mode not in MODES:
        print(f"Неизвестный режим: {mode}")
        print("Доступные:", ", ".join(MODES.keys()))
        sys.exit(1)

    # Determine project root
    if len(sys.argv) >= 3:
        project_root = Path(sys.argv[2]).resolve()
    else:
        project_root = Path.cwd()

    if not project_root.is_dir():
        print(f"Директория не найдена: {project_root}")
        sys.exit(1)

    title, generator = MODES[mode]
    full_title = f"{project_root.name} -- {title}"

    # Generate markdown
    markdown = generator(project_root)

    # Save HTML
    output_dir = ensure_output_dir(project_root)
    filepath = save_html(output_dir, mode, full_title, markdown)

    print(f"Mind map: {filepath}")
    print(f"Открыть: open \"{filepath}\"")


if __name__ == "__main__":
    main()
