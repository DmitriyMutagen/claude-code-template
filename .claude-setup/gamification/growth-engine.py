#!/usr/bin/env python3
"""Growth Engine -- прокачка до Top-1% архитекторов.

Анализирует gamify.db, instincts, reflexion.md и проекты.
Строит дерево навыков, находит слабые места, генерирует план прокачки.

Usage:
    python3 growth-engine.py              # print skill tree + plan
    python3 growth-engine.py --telegram   # send to Telegram
    python3 growth-engine.py --detail     # detailed breakdown per skill
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# --- Paths ---
HOME = Path.home()
GAMIFY_DB = HOME / ".claude" / "gamification" / "gamify.db"
INSTINCTS_DIR = HOME / ".claude" / "homunculus" / "instincts" / "personal"
REFLEXION_FILE = HOME / ".claude" / "memory" / "permanent" / "reflexion.md"
SKILL_TREE_FILE = HOME / ".claude" / "memory" / "permanent" / "skill-tree.md"
PROJECTS_DIR = HOME / "Documents"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "926967075")

# --- Skill Tree Definition ---
SKILL_TREE: dict[str, dict[str, dict[str, str]]] = {
    "Архитектура": {
        "clean_architecture": {"name": "Clean Architecture", "check": "check_architecture"},
        "api_design": {"name": "API Design", "check": "check_api"},
        "database_design": {"name": "Database Design", "check": "check_db"},
        "system_design": {"name": "System Design", "check": "check_system"},
    },
    "Разработка": {
        "python": {"name": "Python", "check": "check_python"},
        "typescript": {"name": "TypeScript", "check": "check_typescript"},
        "docker": {"name": "Docker", "check": "check_docker"},
        "git": {"name": "Git", "check": "check_git"},
    },
    "Качество": {
        "tdd": {"name": "TDD", "check": "check_tdd"},
        "e2e": {"name": "E2E Testing", "check": "check_e2e"},
        "security": {"name": "Security", "check": "check_security"},
        "error_handling": {"name": "Error Handling", "check": "check_errors"},
    },
    "DevOps": {
        "cicd": {"name": "CI/CD", "check": "check_cicd"},
        "monitoring": {"name": "Monitoring", "check": "check_monitoring"},
        "deploy": {"name": "Deploy", "check": "check_deploy"},
    },
    "Управление": {
        "spec_first": {"name": "Spec-First", "check": "check_specs"},
        "adr": {"name": "ADR", "check": "check_adr"},
        "estimation": {"name": "Estimation", "check": "check_estimation"},
    },
    "AI-Dev": {
        "prompt_eng": {"name": "Prompt Engineering", "check": "check_prompts"},
        "multi_agent": {"name": "Multi-Agent", "check": "check_agents"},
        "self_learning": {"name": "Self-Learning", "check": "check_learning"},
    },
}

LEVEL_NAMES = {1: "Junior", 2: "Mid", 3: "Senior", 4: "Elite", 5: "Master"}
RANK_THRESHOLDS = {
    "Top-1%": 4.5,
    "Top-5%": 4.0,
    "Top-10%": 3.5,
    "Top-20%": 3.0,
    "Top-30%": 2.5,
    "Top-50%": 2.0,
    "Bottom-50%": 0.0,
}


def progress_bar(level: int) -> str:
    """Render a 5-block progress bar for skill level 1-5."""
    filled = "\u2588" * level
    empty = "\u2591" * (5 - level)
    return f"{filled}{empty}"


def count_to_level(count: int, thresholds: tuple[int, int, int, int] = (1, 5, 20, 50)) -> int:
    """Convert a count to level 1-5 based on thresholds."""
    t1, t2, t3, t4 = thresholds
    if count >= t4:
        return 5
    if count >= t3:
        return 4
    if count >= t2:
        return 3
    if count >= t1:
        return 2
    return 1


def bool_to_level(found: bool, extra_signal: bool = False) -> int:
    """Convert boolean presence to level. Extra signal bumps up."""
    if not found:
        return 1
    return 4 if extra_signal else 3


# --- Database helpers ---

class GamifyDB:
    """Read-only wrapper around gamify.db."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            if not self.db_path.exists():
                raise FileNotFoundError(f"gamify.db not found at {self.db_path}")
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def query_one(self, sql: str, params: tuple[Any, ...] = ()) -> Any:
        row = self.conn.execute(sql, params).fetchone()
        return row[0] if row else 0

    def query_all(self, sql: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        return self.conn.execute(sql, params).fetchall()

    def count_events(self, action: str, days: int = 7) -> int:
        return self.query_one(
            "SELECT COUNT(*) FROM xp_events WHERE action = ? AND ts > datetime('now', ?)",
            (action, f"-{days} days"),
        )

    def count_events_like(self, pattern: str, days: int = 7) -> int:
        return self.query_one(
            "SELECT COUNT(*) FROM xp_events WHERE action LIKE ? AND ts > datetime('now', ?)",
            (pattern, f"-{days} days"),
        )

    def total_sessions_metric(self, metric: str, days: int = 30) -> int:
        return self.query_one(
            f"SELECT COALESCE(SUM({metric}), 0) FROM sessions "
            f"WHERE started_at > datetime('now', ?)",
            (f"-{days} days",),
        )

    def get_benchmark(self, metric: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM benchmarks WHERE metric = ? ORDER BY updated_at DESC LIMIT 1",
            (metric,),
        ).fetchone()
        if row:
            return dict(row)
        return None


# --- Filesystem scanners ---

def scan_projects_for(pattern: str, glob_pattern: str = "**/*") -> int:
    """Count files matching glob_pattern across all project directories."""
    count = 0
    if not PROJECTS_DIR.exists():
        return 0
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir() or project_dir.name.startswith("."):
            continue
        try:
            count += len(list(project_dir.glob(pattern)))
        except (PermissionError, OSError):
            continue
    return count


def scan_for_docker_files() -> int:
    """Count projects with docker-compose or Dockerfile."""
    count = 0
    if not PROJECTS_DIR.exists():
        return 0
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir() or project_dir.name.startswith("."):
            continue
        has_docker = (
            (project_dir / "Dockerfile").exists()
            or (project_dir / "docker-compose.yml").exists()
            or (project_dir / "docker-compose.yaml").exists()
        )
        if has_docker:
            count += 1
    return count


def scan_for_ci_files() -> int:
    """Count projects with .github/workflows/."""
    count = 0
    if not PROJECTS_DIR.exists():
        return 0
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir() or project_dir.name.startswith("."):
            continue
        workflows = project_dir / ".github" / "workflows"
        if workflows.exists() and any(workflows.glob("*.yml")):
            count += 1
    return count


def count_instincts() -> int:
    """Count personal instinct files."""
    if not INSTINCTS_DIR.exists():
        return 0
    return len(list(INSTINCTS_DIR.glob("*.yaml"))) + len(list(INSTINCTS_DIR.glob("*.yml")))


def count_reflexions() -> int:
    """Count non-empty reflexion entries."""
    if not REFLEXION_FILE.exists():
        return 0
    text = REFLEXION_FILE.read_text(encoding="utf-8", errors="replace")
    lines = [l for l in text.splitlines() if l.strip().startswith("- 20")]
    return len(lines)


# --- Skill check functions ---

def check_architecture(db: GamifyDB) -> int:
    """Check based on src/core/, src/api/ structure presence."""
    core_dirs = scan_projects_for("src/core")
    api_dirs = scan_projects_for("src/api")
    total = core_dirs + api_dirs
    return count_to_level(total, (1, 3, 6, 10))


def check_api(db: GamifyDB) -> int:
    """Check API design skill -- look for FastAPI/OpenAPI files."""
    api_files = scan_projects_for("**/routes*.py") + scan_projects_for("**/router*.py")
    return count_to_level(api_files, (1, 3, 8, 15))


def check_db(db: GamifyDB) -> int:
    """Check database design -- migrations, models."""
    migrations = scan_projects_for("**/alembic/**/*.py")
    models = scan_projects_for("**/models/*.py") + scan_projects_for("**/models.py")
    return count_to_level(migrations + models, (1, 3, 8, 15))


def check_system(db: GamifyDB) -> int:
    """Check system design -- compose files, multiple services."""
    compose_count = scan_for_docker_files()
    return count_to_level(compose_count, (1, 3, 5, 8))


def check_python(db: GamifyDB) -> int:
    """Check Python skill from xp_events and file counts."""
    py_files = scan_projects_for("**/*.py")
    commits = db.count_events("bash_git_commit", days=30)
    score = min(py_files, 100) + commits
    return count_to_level(score, (5, 20, 60, 150))


def check_typescript(db: GamifyDB) -> int:
    """Check TypeScript presence."""
    ts_files = scan_projects_for("**/*.ts") + scan_projects_for("**/*.tsx")
    return count_to_level(ts_files, (5, 20, 60, 150))


def check_docker(db: GamifyDB) -> int:
    """Check Docker proficiency."""
    docker_projects = scan_for_docker_files()
    deploys = db.count_events("bash_deploy", days=30)
    return count_to_level(docker_projects + deploys, (1, 3, 5, 8))


def check_git(db: GamifyDB) -> int:
    """Check Git skill from commit frequency and conventional commits."""
    commits_week = db.count_events("bash_git_commit", days=7)
    night_commits = db.count_events("bash_git_commit_night", days=7)
    total = commits_week + night_commits
    return count_to_level(total, (3, 10, 30, 60))


def check_tdd(db: GamifyDB) -> int:
    """Check TDD from test runs this week."""
    tests = db.count_events("bash_test_pass", days=7)
    return count_to_level(tests, (1, 5, 20, 50))


def check_e2e(db: GamifyDB) -> int:
    """Check E2E testing -- Playwright test files."""
    e2e_files = scan_projects_for("**/*.spec.ts") + scan_projects_for("**/e2e/**/*.py")
    return count_to_level(e2e_files, (1, 3, 8, 15))


def check_security(db: GamifyDB) -> int:
    """Check security awareness from instincts and patterns."""
    instinct_count = count_instincts()
    has_security_instinct = (INSTINCTS_DIR / "quality-score-mandatory.yaml").exists() if INSTINCTS_DIR.exists() else False
    base = 2 if has_security_instinct else 1
    if instinct_count >= 8:
        base = max(base, 4)
    elif instinct_count >= 4:
        base = max(base, 3)
    return min(base, 5)


def check_errors(db: GamifyDB) -> int:
    """Check error handling -- Sentry fixes, retry patterns."""
    sentry_fixes = db.count_events_like("%sentry%", days=30)
    bench = db.get_benchmark("sentry_fixes_per_week")
    if bench and bench.get("rank") in ("God Tier", "Elite"):
        return 5
    if sentry_fixes >= 5:
        return 4
    if sentry_fixes >= 1:
        return 3
    return 2  # at least has Sentry configured


def check_cicd(db: GamifyDB) -> int:
    """Check CI/CD from workflow files."""
    ci_projects = scan_for_ci_files()
    return count_to_level(ci_projects, (1, 2, 4, 6))


def check_monitoring(db: GamifyDB) -> int:
    """Check monitoring -- Sentry integration, health endpoints."""
    bench = db.get_benchmark("sentry_fixes_per_week")
    sentry_rank = bench.get("rank", "Junior") if bench else "Junior"
    if sentry_rank in ("God Tier", "Elite"):
        return 5
    if sentry_rank == "Senior":
        return 4
    if sentry_rank == "Mid":
        return 3
    return 2  # Sentry is configured at minimum


def check_deploy(db: GamifyDB) -> int:
    """Check deploy skill."""
    deploys = db.count_events("bash_deploy", days=30)
    bench = db.get_benchmark("deploys_per_week")
    rank = bench.get("rank", "Junior") if bench else "Junior"
    level_from_rank = {"God Tier": 5, "Elite": 4, "Senior": 3, "Mid": 2, "Junior": 1}.get(rank, 1)
    level_from_count = count_to_level(deploys, (1, 3, 7, 14))
    return max(level_from_rank, level_from_count)


def check_specs(db: GamifyDB) -> int:
    """Check spec-first from docs/plans/ files."""
    specs = scan_projects_for("docs/plans/*.md")
    return count_to_level(specs, (1, 3, 8, 15))


def check_adr(db: GamifyDB) -> int:
    """Check ADR practice from docs/adr/ files."""
    adrs = scan_projects_for("docs/adr/*.md")
    return count_to_level(adrs, (1, 3, 6, 10))


def check_estimation(db: GamifyDB) -> int:
    """Check estimation skill -- based on reflexions (learning from mistakes)."""
    reflexions = count_reflexions()
    return count_to_level(reflexions, (1, 3, 8, 15))


def check_prompts(db: GamifyDB) -> int:
    """Check prompt engineering from agent spawns and context files."""
    agents = db.count_events("task_agent_spawn", days=7)
    writes = db.count_events("Write", days=7)
    score = agents + (writes // 10)
    return count_to_level(score, (2, 8, 20, 40))


def check_agents(db: GamifyDB) -> int:
    """Check multi-agent orchestration."""
    agents_week = db.count_events("task_agent_spawn", days=7)
    bench = db.get_benchmark("agents_per_day")
    rank = bench.get("rank", "Junior") if bench else "Junior"
    level_from_rank = {"God Tier": 5, "Elite": 4, "Senior": 3, "Mid": 2, "Junior": 1}.get(rank, 1)
    return max(level_from_rank, count_to_level(agents_week, (2, 8, 20, 40)))


def check_learning(db: GamifyDB) -> int:
    """Check self-learning systems from instincts count."""
    instinct_count = count_instincts()
    has_memory = (HOME / ".claude" / "memory" / "GLOBAL_MEMORY.md").exists()
    base = count_to_level(instinct_count, (2, 5, 8, 12))
    if has_memory and base < 3:
        base = 3
    return base


# --- Main evaluation engine ---

# Registry mapping check function names to callables
CHECK_REGISTRY: dict[str, Any] = {
    "check_architecture": check_architecture,
    "check_api": check_api,
    "check_db": check_db,
    "check_system": check_system,
    "check_python": check_python,
    "check_typescript": check_typescript,
    "check_docker": check_docker,
    "check_git": check_git,
    "check_tdd": check_tdd,
    "check_e2e": check_e2e,
    "check_security": check_security,
    "check_errors": check_errors,
    "check_cicd": check_cicd,
    "check_monitoring": check_monitoring,
    "check_deploy": check_deploy,
    "check_specs": check_specs,
    "check_adr": check_adr,
    "check_estimation": check_estimation,
    "check_prompts": check_prompts,
    "check_agents": check_agents,
    "check_learning": check_learning,
}


def evaluate_all(db: GamifyDB) -> dict[str, dict[str, int]]:
    """Evaluate all skills, return {category: {skill_id: level}}."""
    results: dict[str, dict[str, int]] = {}
    for category, skills in SKILL_TREE.items():
        results[category] = {}
        for skill_id, skill_info in skills.items():
            check_name = skill_info["check"]
            check_fn = CHECK_REGISTRY.get(check_name)
            if check_fn:
                try:
                    level = check_fn(db)
                except Exception:
                    level = 1
            else:
                level = 1
            results[category][skill_id] = max(1, min(5, level))
    return results


def category_average(levels: dict[str, int]) -> float:
    """Average level for a category."""
    if not levels:
        return 1.0
    return sum(levels.values()) / len(levels)


def overall_average(results: dict[str, dict[str, int]]) -> float:
    """Overall average across all categories."""
    all_levels = [l for cat in results.values() for l in cat.values()]
    return sum(all_levels) / len(all_levels) if all_levels else 1.0


def get_rank(avg: float) -> str:
    """Get rank string from average."""
    for rank, threshold in RANK_THRESHOLDS.items():
        if avg >= threshold:
            return rank
    return "Bottom-50%"


def find_weakest(results: dict[str, dict[str, int]], n: int = 3) -> list[tuple[str, str, int]]:
    """Find N weakest skills. Returns [(category, skill_name, level), ...]."""
    all_skills: list[tuple[str, str, int]] = []
    for category, skills in results.items():
        for skill_id, level in skills.items():
            skill_name = SKILL_TREE[category][skill_id]["name"]
            all_skills.append((category, skill_name, level))
    all_skills.sort(key=lambda x: x[2])
    return all_skills[:n]


# --- Growth plan generation ---

GROWTH_ACTIONS: dict[str, list[str]] = {
    "TDD": [
        "Напиши 5 тестов для существующего API (pytest)",
        "Попробуй Red-Green-Refactor: сначала тест, потом код",
        "Добавь conftest.py с фикстурами в один проект",
    ],
    "E2E Testing": [
        "Напиши один Playwright тест для aragant.pro",
        "Добавь screenshot-сравнение в тест",
        "Настрой playwright.config.ts в одном проекте",
    ],
    "CI/CD": [
        "Добавь .github/workflows/ci.yml в один проект",
        "Настрой ruff check + pytest в CI pipeline",
        "Добавь Claude Code Action для PR review",
    ],
    "Deploy": [
        "Задеплой один проект с health check эндпоинтом",
        "Настрой auto-rollback при падении healthcheck",
        "Добавь Telegram алерт при ошибке деплоя",
    ],
    "Security": [
        "Пройди OWASP Top 10 чеклист для одного API",
        "Добавь rate limiting на публичные эндпоинты",
        "Запусти semgrep --config=auto на проекте",
    ],
    "ADR": [
        "Напиши первый ADR для выбора стека в проекте",
        "Создай docs/adr/ директорию с шаблоном",
        "Зафиксируй решение по архитектуре в ADR формате",
    ],
    "Spec-First": [
        "Напиши spec.md перед следующей фичей",
        "Определи API контракт до написания кода",
        "Добавь docs/plans/ с планом на неделю",
    ],
    "Clean Architecture": [
        "Раздели один проект на src/core/ + src/api/ + src/connectors/",
        "Вынеси бизнес-логику из API роутов в core/",
        "Создай интерфейсы (Protocol) для внешних зависимостей",
    ],
    "Monitoring": [
        "Настрой Sentry SDK в одном проекте",
        "Добавь /health эндпоинт с проверкой DB/Redis",
        "Настрой Telegram алерт на новые Sentry issues",
    ],
    "Error Handling": [
        "Добавь tenacity retry для всех внешних API вызовов",
        "Настрой structured logging (JSON) в одном проекте",
        "Пофикси 3 открытых Sentry issues",
    ],
    "Docker": [
        "Напиши multi-stage Dockerfile для Python проекта",
        "Добавь healthcheck в docker-compose.yml",
        "Настрой Docker networking между сервисами",
    ],
    "API Design": [
        "Добавь Pydantic модели для всех эндпоинтов",
        "Настрой автогенерацию OpenAPI документации",
        "Добавь версионирование API (/v1/, /v2/)",
    ],
    "Database Design": [
        "Создай Alembic миграцию для существующих моделей",
        "Оптимизируй N+1 запрос через selectinload",
        "Добавь индексы для частых WHERE/JOIN запросов",
    ],
    "Estimation": [
        "Записывай оценку vs реальное время для 5 задач",
        "Разбивай задачи на части < 2 часов",
        "Веди лог рефлексий в reflexion.md",
    ],
    "Python": [
        "Добавь строгие type hints во все функции одного модуля",
        "Перепиши sync код на async/await",
        "Используй Pydantic для валидации всех входных данных",
    ],
    "TypeScript": [
        "Включи strict mode в tsconfig.json",
        "Замени все any на конкретные типы",
        "Используй Zod для runtime валидации",
    ],
    "System Design": [
        "Нарисуй C4 диаграмму для одного проекта",
        "Спроектируй очередь задач (Redis + worker)",
        "Добавь кеширование для тяжёлого запроса",
    ],
    "Prompt Engineering": [
        "Создай CLAUDE.md для нового проекта",
        "Напиши 3 кастомных агента для повторяющихся задач",
        "Добавь Context7 проверку для каждой библиотеки",
    ],
    "Multi-Agent": [
        "Запусти параллельных агентов через /parallel",
        "Создай team JSON для pipeline задачи",
        "Используй Agent Teams для code + test параллельно",
    ],
    "Self-Learning": [
        "Добавь 3 новых instinct файла для частых паттернов",
        "Обнови GLOBAL_MEMORY.md с решениями за неделю",
        "Настрой auto-checkpoint после крупных задач",
    ],
    "Git": [
        "Используй conventional commits (feat/fix/refactor) неделю",
        "Попробуй git worktree для параллельной работы",
        "Настрой pre-commit hooks в одном проекте",
    ],
}

XP_PER_LEVEL = {1: 50, 2: 100, 3: 150, 4: 200}
TIME_ESTIMATES = {1: "~20 мин", 2: "~30 мин", 3: "~1 час", 4: "~2 часа"}


def generate_growth_plan(
    results: dict[str, dict[str, int]],
    weakest: list[tuple[str, str, int]],
) -> list[dict[str, str]]:
    """Generate concrete growth actions for weakest skills."""
    plan: list[dict[str, str]] = []
    for category, skill_name, level in weakest:
        actions = GROWTH_ACTIONS.get(skill_name, ["Изучи тему через Context7 / mega-research"])
        action = actions[0] if actions else "Практикуйся"
        xp = XP_PER_LEVEL.get(level, 50)
        time_est = TIME_ESTIMATES.get(level, "~30 мин")
        plan.append({
            "category": category,
            "skill": skill_name,
            "level": level,
            "action": action,
            "xp": str(xp),
            "time": time_est,
            "target_level": str(min(level + 1, 5)),
        })
    return plan


def generate_weekly_tip(results: dict[str, dict[str, int]]) -> str:
    """Generate a contextual weekly tip based on weakest area."""
    cat_avgs = {cat: category_average(levels) for cat, levels in results.items()}
    weakest_cat = min(cat_avgs, key=cat_avgs.get)  # type: ignore[arg-type]

    tips = {
        "Качество": (
            "Код без тестов -- это черновик, не продукт. "
            "Начни с 1 теста перед каждой фичей -- это дешевле, чем дебаг потом."
        ),
        "DevOps": (
            "Деплой руками -- это техдолг. "
            "Один раз настрой CI/CD и забудь. git push = деплой."
        ),
        "Архитектура": (
            "Код без структуры растёт как сорняк. "
            "Раздели на слои сейчас -- потом спасибо скажешь."
        ),
        "Разработка": (
            "Количество кода не равно качеству. "
            "Пиши меньше, но с типами и валидацией."
        ),
        "Управление": (
            "Спеки и ADR кажутся бюрократией, пока не приходится "
            "вспоминать через месяц зачем ты это написал."
        ),
        "AI-Dev": (
            "AI усиливает твои навыки, но не заменяет их. "
            "Понимай что делает AI-код, не копируй слепо."
        ),
    }
    return tips.get(weakest_cat, "Фокусируйся на самом слабом месте -- там максимальный ROI.")


# --- Output formatters ---

def format_tree(results: dict[str, dict[str, int]], detail: bool = False) -> str:
    """Format skill tree as text output."""
    lines: list[str] = []
    lines.append("=" * 50)
    lines.append("  SKILL TREE -- Текущий уровень")
    lines.append("=" * 50)
    lines.append("")

    cat_avgs: dict[str, float] = {}
    for category, skills in results.items():
        avg = category_average(skills)
        cat_avgs[category] = avg
        rounded = round(avg)
        bar = progress_bar(rounded)
        rank_name = LEVEL_NAMES.get(rounded, "?")
        marker = ""
        if rounded <= 2:
            marker = " <-- КАЧАТЬ"
        lines.append(f"  {category:20s} {bar} {rounded}/5 ({rank_name}){marker}")

        if detail:
            for skill_id, level in skills.items():
                skill_name = SKILL_TREE[category][skill_id]["name"]
                skill_bar = progress_bar(level)
                lines.append(f"    {skill_name:22s} {skill_bar} {level}/5")
            lines.append("")

    avg_overall = overall_average(results)
    rank = get_rank(avg_overall)
    lines.append("")
    lines.append(f"  ОБЩИЙ УРОВЕНЬ: {avg_overall:.1f}/5 ({rank})")
    lines.append(f"  ДО TOP-1%: {'все категории >= 4/5' if avg_overall < 4.5 else 'ТЫ УЖЕ ТАМ!'}")

    # What needs the most improvement
    weak_cats = sorted(cat_avgs.items(), key=lambda x: x[1])
    needs = []
    for cat, avg in weak_cats:
        if avg < 4.0:
            diff = 4.0 - avg
            needs.append(f"{cat} +{diff:.1f}")
    if needs:
        lines.append(f"  Нужно прокачать: {', '.join(needs[:3])}")

    return "\n".join(lines)


def format_plan(plan: list[dict[str, str]], tip: str) -> str:
    """Format growth plan as text."""
    lines: list[str] = []
    lines.append("")
    lines.append("=" * 50)
    lines.append("  ПЛАН ПРОКАЧКИ (эта неделя)")
    lines.append("=" * 50)
    lines.append("")

    for i, item in enumerate(plan, 1):
        cat = item["category"]
        skill = item["skill"]
        level = item["level"]
        target = item["target_level"]
        action = item["action"]
        xp = item["xp"]
        time = item["time"]

        lines.append(f"  {i}. {cat} / {skill} (уровень {level} -> {target})")
        lines.append(f"     Задача: {action}")
        lines.append(f"     Награда: +{xp} XP  |  Время: {time}")
        lines.append("")

    lines.append("-" * 50)
    lines.append(f"  СОВЕТ НЕДЕЛИ:")
    lines.append(f"  \"{tip}\"")
    lines.append("-" * 50)

    return "\n".join(lines)


def format_telegram(results: dict[str, dict[str, int]], plan: list[dict[str, str]], tip: str) -> str:
    """Format for Telegram with Markdown."""
    lines: list[str] = []
    lines.append("*SKILL TREE -- Growth Report*")
    lines.append(f"_{datetime.now().strftime('%Y-%m-%d %H:%M')}_")
    lines.append("")

    for category, skills in results.items():
        avg = round(category_average(skills))
        bar = progress_bar(avg)
        rank_name = LEVEL_NAMES.get(avg, "?")
        lines.append(f"`{category:15s} {bar} {avg}/5 ({rank_name})`")

    avg_overall = overall_average(results)
    rank = get_rank(avg_overall)
    lines.append("")
    lines.append(f"*Overall: {avg_overall:.1f}/5 ({rank})*")
    lines.append("")

    lines.append("*Plan:*")
    for i, item in enumerate(plan, 1):
        lines.append(f"{i}. *{item['skill']}* ({item['level']}->{item['target_level']}): {item['action']}")

    lines.append("")
    lines.append(f"_{tip}_")

    return "\n".join(lines)


def send_telegram(text: str) -> bool:
    """Send message to Telegram."""
    if not TELEGRAM_BOT_TOKEN:
        print("[!] TELEGRAM_BOT_TOKEN not set. Skipping Telegram send.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[!] Telegram send failed: {e}")
        return False


def save_skill_tree(results: dict[str, dict[str, int]], plan: list[dict[str, str]]) -> None:
    """Save skill tree state to permanent memory."""
    SKILL_TREE_FILE.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d")
    lines: list[str] = []
    lines.append("# Skill Tree Progress")
    lines.append("")
    lines.append(f"## Last updated: {now}")
    lines.append("")

    for category, skills in results.items():
        avg = round(category_average(skills))
        lines.append(f"### {category}: {avg}/5")
        for skill_id, level in skills.items():
            skill_name = SKILL_TREE[category][skill_id]["name"]
            lines.append(f"- {skill_name}: {level}/5")
        lines.append("")

    avg_overall = overall_average(results)
    rank = get_rank(avg_overall)
    lines.append(f"## Overall: {avg_overall:.1f}/5 ({rank})")
    lines.append("")

    lines.append("## Current Growth Plan")
    for i, item in enumerate(plan, 1):
        lines.append(f"{i}. {item['skill']} ({item['level']}->{item['target_level']}): {item['action']}")
    lines.append("")

    # Append history entry instead of overwriting
    if SKILL_TREE_FILE.exists():
        existing = SKILL_TREE_FILE.read_text(encoding="utf-8", errors="replace")
        history_marker = "## History"
        if history_marker in existing:
            # Extract old history
            history_start = existing.index(history_marker)
            old_history = existing[history_start:]
            lines.append(old_history.rstrip())
        else:
            lines.append("## History")

        lines.append(f"- {now}: overall {avg_overall:.1f}/5 ({rank})")
    else:
        lines.append("## History")
        lines.append(f"- {now}: overall {avg_overall:.1f}/5 ({rank})")

    SKILL_TREE_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[+] Skill tree saved to {SKILL_TREE_FILE}")


# --- Main ---

def main() -> None:
    parser = argparse.ArgumentParser(description="Growth Engine -- skill tree + growth plan")
    parser.add_argument("--telegram", action="store_true", help="Send report to Telegram")
    parser.add_argument("--detail", action="store_true", help="Show detailed breakdown per skill")
    parser.add_argument("--save", action="store_true", default=True, help="Save skill tree (default: true)")
    parser.add_argument("--no-save", action="store_true", help="Do not save skill tree")
    args = parser.parse_args()

    if not GAMIFY_DB.exists():
        print(f"[!] gamify.db not found at {GAMIFY_DB}")
        print("[!] Run gamification engine first to create the database.")
        sys.exit(1)

    db = GamifyDB(GAMIFY_DB)
    try:
        results = evaluate_all(db)
        weakest = find_weakest(results, n=3)
        plan = generate_growth_plan(results, weakest)
        tip = generate_weekly_tip(results)

        # Print skill tree
        tree_text = format_tree(results, detail=args.detail)
        print(tree_text)

        # Print growth plan
        plan_text = format_plan(plan, tip)
        print(plan_text)

        # Save to file
        if not args.no_save:
            save_skill_tree(results, plan)

        # Send to Telegram
        if args.telegram:
            tg_text = format_telegram(results, plan, tip)
            if send_telegram(tg_text):
                print("\n[+] Report sent to Telegram")
            else:
                print("\n[!] Failed to send to Telegram")

    finally:
        db.close()


if __name__ == "__main__":
    main()
