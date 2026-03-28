#!/usr/bin/env python3
"""
Creator Coaching — рекомендации от Top-100 creators.
Анализирует задачу и подбирает релевантный референс.

Usage:
    python3 creator_coaching.py deploy
    python3 creator_coaching.py api
    python3 creator_coaching.py speed
    python3 creator_coaching.py architecture
    python3 creator_coaching.py seo
    python3 creator_coaching.py testing
    python3 creator_coaching.py ai
    python3 creator_coaching.py startup
    python3 creator_coaching.py infra
    python3 creator_coaching.py quality
    python3 creator_coaching.py solo
    python3 creator_coaching.py general
"""
import json
import sys
from pathlib import Path

GAMIFY_DIR = Path.home() / ".claude" / "gamification"
CREATORS_DB_PATH = GAMIFY_DIR / "top100_creators.json"


def load_creators() -> dict:
    if CREATORS_DB_PATH.exists():
        with open(CREATORS_DB_PATH) as f:
            return json.load(f)
    return {}


TASK_TO_CREATORS: dict[str, list[str]] = {
    "deploy": ["Werner Vogels", "Guillermo Rauch", "Pieter Levels"],
    "api": ["Patrick Collison", "Martin Fowler", "Werner Vogels"],
    "speed": ["Pieter Levels", "Marc Lou", "DHH (David Heinemeier Hansson)"],
    "architecture": ["Martin Fowler", "Sam Newman", "Gregor Hohpe"],
    "seo": ["Rand Fishkin", "Eli Schwartz", "Brian Dean (Backlinko)"],
    "testing": ["Kent Beck", "Andrej Karpathy", "Martin Fowler"],
    "ai": ["Andrej Karpathy", "Sam Altman", "Harrison Chase"],
    "startup": ["Pieter Levels", "Paul Graham", "DHH (David Heinemeier Hansson)"],
    "infra": ["Werner Vogels", "Mitchell Hashimoto", "Kelsey Hightower"],
    "quality": ["Martin Fowler", "Uncle Bob (Robert C. Martin)", "Kent Beck"],
    "solo": ["Pieter Levels", "Marc Lou", "Tony Dinh"],
    "frontend": ["Guillermo Rauch", "Evan You", "Theo Browne (t3dotgg)"],
    "database": ["Martin Fowler", "Rich Hickey", "Werner Vogels"],
    "security": ["Uncle Bob (Robert C. Martin)", "Werner Vogels", "Martin Fowler"],
    "devops": ["Mitchell Hashimoto", "Kelsey Hightower", "Werner Vogels"],
    "product": ["Paul Graham", "DHH (David Heinemeier Hansson)", "Sahil Lavingia"],
    "general": ["Martin Fowler", "Pieter Levels", "Werner Vogels"],
}

INSIGHTS: dict[str, dict[str, str]] = {
    "Pieter Levels": {
        "insight": "Ship it in 24h or don't ship it",
        "metric": "Revenue from day 1",
        "action": "Запусти MVP сегодня. Не завтра. Stripe link + лендинг = продукт.",
        "quote": "Your first version should embarrass you",
        "emoji": "🚀",
    },
    "Marc Lou": {
        "insight": "Boilerplate is the product — don't reinvent the base",
        "metric": "1 week from zero to $1 MRR",
        "action": "Используй готовый шаблон. Не трать время на настройку стека.",
        "quote": "Stop building features. Start building marketing.",
        "emoji": "⚡",
    },
    "Martin Fowler": {
        "insight": "Make implicit explicit — задокументируй решение",
        "metric": "ADR coverage 100%",
        "action": "Создай ADR для этого решения (20 мин) в docs/adr/",
        "quote": "Any fool can write code a computer understands. Good programmers write code humans understand.",
        "emoji": "📐",
    },
    "Werner Vogels": {
        "insight": "Everything fails, all the time",
        "metric": "Healthcheck + Sentry везде, rollback < 5 min",
        "action": "Добавь /health endpoint, Docker healthcheck и Sentry DSN",
        "quote": "You build it, you run it",
        "emoji": "🛡️",
    },
    "Patrick Collison": {
        "insight": "7 lines to get started — сделай API простым",
        "metric": "5 мин до первого вызова для нового разработчика",
        "action": "Проверь: можно ли интегрировать твой API за 7 строк кода?",
        "quote": "The best API is one you never have to read docs for",
        "emoji": "💎",
    },
    "DHH (David Heinemeier Hansson)": {
        "insight": "Convention over configuration — меньше решений, больше скорость",
        "metric": "Monolith first, profitable day 1",
        "action": "Не изобретай структуру проекта. Используй /new-project шаблон.",
        "quote": "Optimize for happiness",
        "emoji": "🏗️",
    },
    "Andrej Karpathy": {
        "insight": "Simplest solution first — сложность добавь потом если нужно",
        "metric": "No premature optimization",
        "action": "Make it work → make it right → make it fast. В этом порядке.",
        "quote": "The hottest new programming language is English",
        "emoji": "🧠",
    },
    "Sam Newman": {
        "insight": "Start with monolith, migrate to microservices only with evidence",
        "metric": "PMF first, then architecture",
        "action": "Монолит — до тех пор пока не будет чёткого доказательства что нужны микросервисы.",
        "quote": "Services own their data — no shared databases",
        "emoji": "🏛️",
    },
    "Guillermo Rauch": {
        "insight": "Preview deployments for every PR — каждый коммит деплоится",
        "metric": "git push = production deploy в < 2 мин",
        "action": "Настрой Vercel/Railway для preview deployments на каждый PR.",
        "quote": "Ship to edge — static is the new dynamic",
        "emoji": "🌐",
    },
    "Kent Beck": {
        "insight": "TDD: Red → Green → Refactor",
        "metric": "Test first, code second",
        "action": "Напиши падающий тест ПЕРЕД кодом. Потом пусть AI его пройдёт.",
        "quote": "Make it work → make it right → make it fast",
        "emoji": "🧪",
    },
    "Sam Altman": {
        "insight": "AI-first architecture — не AI как добавка, а как основа",
        "metric": "Evals before shipping any AI feature",
        "action": "Добавь eval/scoring для AI-фич. Без метрик = без контроля качества.",
        "quote": "Intelligence is going to be essentially free soon",
        "emoji": "🤖",
    },
    "Mitchell Hashimoto": {
        "insight": "Infrastructure as code — treat infra like software",
        "metric": "Zero manual infra steps",
        "action": "Если ты делаешь что-то руками на сервере — напиши это в Terraform/Docker.",
        "quote": "Developer tools create lock-in through love, not force",
        "emoji": "⚙️",
    },
    "Paul Graham": {
        "insight": "Do things that don't scale — первые 100 юзеров руками",
        "metric": "Talk to 10 users this week",
        "action": "Поговори с реальными пользователями сегодня. Не строй — общайся.",
        "quote": "Make something people want",
        "emoji": "💡",
    },
    "Rand Fishkin": {
        "insight": "10x content — не на 10% лучше, а в 10 раз ценнее",
        "metric": "DA через editorial links, не купленные",
        "action": "Создай одну выдающуюся страницу вместо десяти посредственных.",
        "quote": "SEO = brand + content + technical + links (all four)",
        "emoji": "📈",
    },
    "Eli Schwartz": {
        "insight": "Product-Led SEO — SEO встроен в продукт, не добавлен потом",
        "metric": "Core pages > 1000 thin pages",
        "action": "Сделай 10 великолепных страниц вместо 1000 тонких.",
        "quote": "Build the product users search for, then optimize",
        "emoji": "🎯",
    },
    "Uncle Bob (Robert C. Martin)": {
        "insight": "Single Responsibility Principle — один класс, одна причина меняться",
        "metric": "SOLID coverage",
        "action": "Проверь: у каждого модуля одна ответственность? Если нет — декомпозируй.",
        "quote": "Clean code reads like well-written prose",
        "emoji": "✨",
    },
    "Harrison Chase": {
        "insight": "LLMs need orchestration, not just prompting",
        "metric": "Evals = unit tests for AI",
        "action": "Добавь LangSmith tracing или хотя бы логирование к каждому LLM вызову.",
        "quote": "Evals are the unit tests of AI",
        "emoji": "🔗",
    },
    "Rich Hickey": {
        "insight": "Simple made easy — simple и easy это не одно и то же",
        "metric": "Immutable data, no complecting",
        "action": "Разделяй данные, логику и состояние явно. Не смешивай.",
        "quote": "Simple ain't easy",
        "emoji": "🎭",
    },
    "Kelsey Hightower": {
        "insight": "Don't start with Kubernetes — start with what you know",
        "metric": "Container-first, Kubernetes только при >10 сервисах",
        "action": "Docker Compose для локала, один VPS для старта. Kubernetes потом.",
        "quote": "Simplicity is a feature",
        "emoji": "📦",
    },
    "Gregor Hohpe": {
        "insight": "Architect rides the elevator — между стратегией и кодом",
        "metric": "Message queues решают большинство distributed problems",
        "action": "Нарисуй C4 диаграмму для этой системы. Если не можешь — архитектура непонятна.",
        "quote": "Good architecture reduces future effort",
        "emoji": "🏢",
    },
    "Sahil Lavingia": {
        "insight": "Async-first company — без митингов, документировано всё",
        "metric": "Profitable over growth",
        "action": "Запиши решение в документ вместо звонка. Async beats sync.",
        "quote": "Building a business is just finding people with problems and solving them",
        "emoji": "📝",
    },
    "Tony Dinh": {
        "insight": "Multiple small products > one big product",
        "metric": "$1.5M/year solo, zero team",
        "action": "Не ставь всё на одну лошадь. 5 малых продуктов диверсифицируют риск.",
        "quote": "Developer tools = best niche for solo devs",
        "emoji": "🎪",
    },
    "Evan You": {
        "insight": "Fast feedback loops = productive development",
        "metric": "Vite: 5x быстрее Webpack",
        "action": "Используй Vite для любого нового frontend проекта. HMR < 100ms.",
        "quote": "Developer experience is everything",
        "emoji": "⚡",
    },
    "Theo Browne (t3dotgg)": {
        "insight": "Type safety all the way down — TypeScript на всех уровнях",
        "metric": "Zero any, strict mode",
        "action": "Включи strict: true в tsconfig. Фиксируй ошибки сейчас, не в production.",
        "quote": "If you're using REST between frontend and backend you own, you're doing it wrong",
        "emoji": "🔒",
    },
    "Brian Dean (Backlinko)": {
        "insight": "Skyscraper: найди топ контент, сделай 10x лучше, промоутируй",
        "metric": "One ultimate guide > 100 thin articles",
        "action": "Найди лучший материал по теме. Сделай вдвое длиннее и полезнее.",
        "quote": "One great page beats 100 mediocre ones",
        "emoji": "🏙️",
    },
    "Paul Graham": {
        "insight": "Do things that don't scale — первые 100 юзеров руками",
        "metric": "Weekly growth rate as north star",
        "action": "Поговори с реальными пользователями сегодня. Не строй — общайся.",
        "quote": "Make something people want",
        "emoji": "💡",
    },
    "Jason Fried": {
        "insight": "Shape Up: 6-week cycles, no backlogs, calm company",
        "metric": "Async-first: zero meetings by default",
        "action": "Попробуй 6-недельный цикл. Scope down до того что реально сделать.",
        "quote": "Work doesn't have to be crazy",
        "emoji": "🧘",
    },
    "Simon Willison (simonw)": {
        "insight": "SQLite is underrated — правильный инструмент чаще чем думаешь",
        "metric": "LLM tool use = самая мощная фича",
        "action": "Для нового проекта: начни с SQLite. Мигрируй на Postgres когда нужно.",
        "quote": "Build tools that expose data simply",
        "emoji": "🗄️",
    },
    "Danny Postma": {
        "insight": "AI-wrapper is a valid business — wrap AI models, charge for convenience",
        "metric": "$1M in 3 months (HeadshotPro)",
        "action": "Не строй AI с нуля. Оберни Replicate/OpenAI API, добавь UX и цену.",
        "quote": "Find the pain point, wrap an AI model, charge for convenience",
        "emoji": "🎁",
    },
}


def get_relevant_creators(task_type: str) -> list[str]:
    """Возвращает топ-3 релевантных создателя для типа задачи."""
    normalized = task_type.lower().strip()
    return TASK_TO_CREATORS.get(normalized, TASK_TO_CREATORS["general"])


def print_creator_insight(task_type: str = "general") -> None:
    creators = get_relevant_creators(task_type)
    creators_db = load_creators()

    db_version = creators_db.get("version", "unknown")
    db_updated = creators_db.get("last_updated", "unknown")

    print(f"\n{'━' * 50}")
    print(f"  CREATOR COACHING: {task_type.upper()}")
    print(f"  База знаний v{db_version} (updated {db_updated})")
    print(f"{'━' * 50}")

    for i, creator_name in enumerate(creators[:3], 1):
        if creator_name in INSIGHTS:
            insight_data = INSIGHTS[creator_name]
            emoji = insight_data["emoji"]
            print(f"\n  {i}. {emoji} {creator_name}")
            print(f"     Принцип: \"{insight_data['insight']}\"")
            print(f"     Метрика: {insight_data['metric']}")
            print(f"     Действие: {insight_data['action']}")
            print(f"     Цитата: \"{insight_data['quote']}\"")
        else:
            print(f"\n  {i}. {creator_name} — профиль в top100_creators.json")

    print(f"\n{'━' * 50}")

    for_task = creators_db.get("creator_comparison", {})
    task_map = {
        "deploy": "for_solo_saas",
        "speed": "for_solo_saas",
        "solo": "for_solo_saas",
        "architecture": "for_enterprise_software",
        "infra": "for_enterprise_software",
        "api": "for_developer_tools",
        "frontend": "for_developer_tools",
        "ai": "for_ai_products",
        "seo": "for_seo_growth",
        "growth": "for_seo_growth",
        "startup": "for_startup_culture",
        "product": "for_startup_culture",
    }
    comparison_key = task_map.get(task_type.lower())
    if comparison_key and comparison_key in for_task:
        comparison = for_task[comparison_key]
        principles = comparison.get("principles", [])
        if principles:
            print(f"\n  Ключевые принципы для '{task_type}':")
            for principle in principles:
                print(f"    • {principle}")
            print()

    print(f"  Полная база: ~/.claude/gamification/top100_creators.json\n")


def list_task_types() -> None:
    print("\nДоступные типы задач:")
    for task in sorted(TASK_TO_CREATORS.keys()):
        creators = TASK_TO_CREATORS[task]
        print(f"  {task:<15} -> {', '.join(creators[:2])}")
    print()


def print_benchmark(task_type: str) -> None:
    creators_db = load_creators()
    benchmarks = creators_db.get("benchmarks_by_creator", {})

    bench_map = {
        "speed": "speed",
        "solo": "solo_building",
        "quality": "quality",
        "architecture": "architecture",
        "seo": "seo",
        "deploy": "speed",
    }

    bench_key = bench_map.get(task_type.lower())
    if bench_key and bench_key in benchmarks:
        print(f"\n  Бенчмарки для '{task_type}':")
        for creator, metrics in benchmarks[bench_key].items():
            print(f"\n  {creator}:")
            if isinstance(metrics, dict):
                for k, v in metrics.items():
                    print(f"    {k}: {v}")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h", "help"):
        print(__doc__)
        list_task_types()
        sys.exit(0)

    if args[0] == "list":
        list_task_types()
        sys.exit(0)

    task = args[0]
    print_creator_insight(task)

    if len(args) > 1 and args[1] == "--bench":
        print_benchmark(task)
