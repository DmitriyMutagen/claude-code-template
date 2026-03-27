---
name: growth-coach
description: Персональный коуч прокачки до уровня Top-1% архитекторов. Анализирует текущий уровень, строит план обучения, предлагает конкретные задачи для роста. Запускай еженедельно или после /daily-review.
---

# /growth-coach -- Прокачка до Top-1%

## Когда запускать
- Еженедельно (автоматически через /improver)
- После /daily-review если есть метрики Junior/Mid
- Когда чувствуешь что застрял
- Когда говоришь "что прокачать", "чего не хватает", "как стать лучше"

## Skill Tree -- Дерево навыков

Каждый навык имеет уровень 1-5:
1 = Не знаю / не делаю
2 = Пробовал / понимаю концепцию
3 = Делаю с помощью AI / не уверен
4 = Делаю уверенно / стабильно
5 = Мастер / могу научить других

### Архитектура (Architecture)
- [ ] Clean Architecture (разделение слоёв)
- [ ] API Design (REST, GraphQL, контракты)
- [ ] Database Design (нормализация, индексы, миграции)
- [ ] System Design (масштабирование, кеширование, очереди)
- [ ] Microservices vs Monolith (когда что)
- [ ] Event-Driven Architecture
- [ ] C4 Diagrams (визуализация архитектуры)

### Разработка (Development)
- [ ] Python (async, типы, Pydantic, FastAPI)
- [ ] TypeScript (strict mode, generics)
- [ ] React/Next.js (хуки, SSR, оптимизация)
- [ ] SQL (сложные запросы, оптимизация)
- [ ] Docker (multi-stage, compose, networking)
- [ ] Git (branching, rebase, worktrees)

### Качество (Quality)
- [ ] TDD (Red-Green-Refactor)
- [ ] E2E Testing (Playwright)
- [ ] Code Review (находить баги в чужом коде)
- [ ] Security (OWASP Top 10, input validation)
- [ ] Performance (profiling, N+1, caching)
- [ ] Error Handling (graceful, Sentry, retry)

### DevOps & Deploy
- [ ] CI/CD (GitHub Actions)
- [ ] Docker Production (healthchecks, logging)
- [ ] Nginx (reverse proxy, SSL, caching)
- [ ] Monitoring (Sentry, healthchecks, alerts)
- [ ] Rollback Strategy
- [ ] Infrastructure as Code

### Управление (Management)
- [ ] Spec-First Development
- [ ] ADR (фиксация решений)
- [ ] RFC (обсуждение перед реализацией)
- [ ] Prioritization (что делать первым)
- [ ] Technical Debt Management
- [ ] Estimation (оценка в часах, не днях)

### AI-Assisted Development
- [ ] Prompt Engineering (точные задачи для AI)
- [ ] Multi-Agent Orchestration (параллельные агенты)
- [ ] AI Code Review (знать когда AI ошибается)
- [ ] Context Management (CLAUDE.md, memory, rules)
- [ ] Self-Learning Systems (CL v2.1, instincts)

## Процесс оценки

### Step 1: Собрать данные
Читаем:
1. ~/.claude/gamification/gamify.db -- метрики (коммиты, тесты, деплои)
2. ~/.claude/homunculus/instincts/personal/ -- какие паттерны уже выучены
3. ~/.claude/memory/permanent/reflexion.md -- на чём спотыкался
4. ~/.claude/memory/permanent/flowwhisper-analysis.md -- болевые точки из голоса
5. Competitive rankings из gamification engine -- где Junior/Mid

### Step 2: Оценить каждый навык (1-5)
На основе данных автоматически оценить:
- Есть тесты в проектах? -> TDD level
- Есть CI/CD? -> DevOps level
- Есть ADR в docs/adr/? -> Management level
- Коммиты с "feat:" vs "fix:"? -> Development level
- Используются параллельные агенты? -> AI-Dev level

### Step 3: Найти слабые места
Навыки с уровнем 1-2 = зона роста.
Приоритизировать по ВЛИЯНИЮ на бизнес:
1. Что блокирует деплой? -> FIX FIRST
2. Что вызывает переделки? -> FIX SECOND
3. Что замедляет работу? -> OPTIMIZE

### Step 4: Создать план прокачки

Формат вывода:
```
SKILL TREE -- Текущий уровень

Архитектура:     ███░░ 3/5 (Senior)
Разработка:       ██░░░ 2/5 (Mid)  <- КАЧАТЬ
Качество:        █░░░░ 1/5 (Junior) <- ПРИОРИТЕТ
DevOps:          ██░░░ 2/5 (Mid)
Управление:      ███░░ 3/5 (Senior)
AI-Dev:          ████░ 4/5 (Elite)

ОБЩИЙ УРОВЕНЬ: Mid-Senior (Top 30%)
ДО TOP-1%: нужно качество x3, devops x2

ПЛАН ПРОКАЧКИ (эта неделя):
1. КАЧЕСТВО: Напиши 5 тестов для Aragant API
   -> Как: /tdd в проекте marketai
   -> Результат: уровень 1->2 (+50 XP)
   -> Время: ~30 мин

2. DEVOPS: Задеплой Bionovacia с health check
   -> Как: docker compose up + /qa-verify
   -> Результат: уровень 2->3 (+100 XP)
   -> Время: ~1 час

3. РАЗРАБОТКА: Изучи async/await через Context7
   -> Как: /mega-research "python async patterns"
   -> Результат: понимание concurrency (+25 XP)
   -> Время: ~20 мин чтения

СОВЕТ НЕДЕЛИ:
"Твоя главная проблема -- код пишется быстро,
но без тестов. Каждый баг стоит 3x времени.
Начни с 1 теста перед каждой фичей."
```

### Step 5: Отправить в Telegram
Краткий summary + топ-3 задачи для прокачки.

### Step 6: Обновить skill-tree файл
Сохранить в ~/.claude/memory/permanent/skill-tree.md
Трекать прогресс по неделям.

## Автоматизация

Запуск через Python:
```bash
python3 ~/.claude/gamification/growth-engine.py              # print skill tree + plan
python3 ~/.claude/gamification/growth-engine.py --telegram   # send to Telegram
python3 ~/.claude/gamification/growth-engine.py --detail     # detailed breakdown per skill
```
