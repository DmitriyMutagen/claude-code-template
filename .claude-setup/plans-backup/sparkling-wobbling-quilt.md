# План: Глобальная настройка Serena + Инфраструктура Enterprise Solo-Dev

## Контекст

У Дмитрия 102K+ строк кода в MarketAI и нескольких проектах (SoulWay B2B, WB Content Factory, Content Factory, Bio-STM, Bionovacia). Стандартные AI-инструменты захлёбываются на таком масштабе — теряют контекст, галлюцинируют и ломают архитектуру. Цели:

1. **Настроить Serena MCP глобально** — чтобы была всегда активна для всех проектов
2. **Добавить поддержку TypeScript** (React-фронтенд в MarketAI)
3. **Определить лучшие инструменты для enterprise solo-dev** на основе исследования
4. **Подключить Sentry MCP** для отслеживания ошибок прямо из Claude Code

---

## Часть 1: Настройка Serena

### СДЕЛАНО (эта сессия)
- Serena активирована для MarketAI по пути `/Users/Dmitrij/Documents/marketai`
- Записано 5 memory-файлов: `project_overview`, `suggested_commands`, `code_style`, `task_completion`, `codebase_structure`
- Проект зарегистрирован в `~/.serena/serena_config.yml`

### TODO: Добавить поддержку TypeScript

**Файл**: `/Users/Dmitrij/Documents/marketai/.serena/project.yml`

Изменить строку 29:
```yaml
languages:
- python
```
На:
```yaml
languages:
- python
- typescript
```

### TODO: Настроить Serena для остальных проектов

```
mcp__plugin_serena_serena__activate_project({project: "/Users/Dmitrij/Documents/soulway-b2b"})
mcp__plugin_serena_serena__activate_project({project: "/Users/Dmitrij/Documents/content_factory"})
```

### TODO: Глобальные настройки Serena

**Файл**: `~/.serena/serena_config.yml` — добавить проекты, увеличить таймауты.

---

## Часть 2: ТОП-РАЗРАБОТЧИКИ МИРА — КТО И КАК СТРОИТ ENTERPRISE В ОДИНОЧКУ

### A. Борис Черни — создатель Claude Code (Anthropic)

**Кто**: Инженер Anthropic, создал Claude Code. Его воркфлоу стало вирусным — VentureBeat, InfoQ, Slashdot писали о нём.

**Его конкретный сетап**:
- **5 параллельных сессий Claude Code** в терминале (5 git-чекаутов одного репо, табы 1-5)
- Плюс **5-10 сессий на claude.ai/code** в браузере
- Флаг `--teleport` для переноса сессий между локалом и вебом
- Запускает сессии **с iPhone утром** через Claude iOS app
- **Модель**: Opus с thinking mode для ВСЕГО. Причина: "меньше руления, лучше tool use, итого быстрее Sonnet"

**CLAUDE.md**:
- Единый файл в git, ~2.5K токенов
- Обновляется **несколько раз в неделю** всей командой
- Документируют ошибки Claude — чтобы не повторялись
- Стиль-гайды: "Всегда `bun`, не `npm`", команды для тестов/линтинга

**Суб-агенты** (папка `.claude/agents/`):
| Агент | Роль |
|-------|------|
| `code-simplifier` | Чистка кода после реализации |
| `verify-app` | E2E тестирование перед шипом |
| `code-architect` | Проектирование архитектуры |
| `build-validator` | Валидация билда |
| `oncall-guide` | Гайд по дежурству |

**MCP серверы**:
- **Slack** — поиск и отправка сообщений автономно
- **BigQuery** — аналитические запросы через `bq` CLI
- **Sentry** — получение логов ошибок

**Хуки**:
- **PostToolUse**: автоформат после генерации кода (`bun run format || true`)

**Пермишены**: Через `/permissions` — разрешённые безопасные команды (`Bash(bun run test:*)`, `Bash(find:*)`) в `.claude/settings.json`

**Ключевой принцип**: "Дай Claude способ верифицировать свою работу. С этим feedback loop качество x2-x3."

> **Источник**: [howborisusesclaudecode.com](https://howborisusesclaudecode.com), [VentureBeat](https://venturebeat.com/technology/the-creator-of-claude-code-just-revealed-his-workflow-and-developers-are), [InfoQ](https://www.infoq.com/news/2026/01/claude-code-creator-workflow/)

---

### B. IndyDevDan — Agentic Engineer (YouTube: @IndyDevDan)

**Кто**: 15+ лет в продакшене, 2M+ просмотров на YouTube, создатель платных курсов по agentic coding. НЕ ютубер-попсец — реально шипит в прод.

**Курсы**:
- **Tactical Agentic Coding (TAC)** — для mid/senior инженеров, Claude Code как основа
- **Principled AI Coding (PAIC)** — 6 часов глубокого контента, language-agnostic

**8 тактик агентного кодирования**:
1. **12 рычагов влияния** — максимизация автономности агента через контекст, модель, промпт, инструменты
2. **Planning-First Engineering** — агенты создают план ДО выполнения (80/20 агентного кодирования)
3. **PITER Framework** — паттерн single-agent для автономного завершения задач
4. **Closed Loop Prompts** — самокорректирующиеся системы со стратегическими feedback loops
5. **Specialized Agent Roles** — выделенные агенты Review и Documentation
6. **ZTE (Zero-Touch Engineering)** — кодовая база шипит сама себя автономно
7. **The Agentic Layer** — мета-тактика: системы-строящие-системы
8. **AI Developer Workflows (ADWs)** — комбинация детерминированного кода с недетерминированными агентами

**Философия**: Переход от "в цикле" (промптинг) к "вне цикла" (автономные системы). Инженер не пишет код — он командует флотом агентов через спецификации.

> **Источник**: [agenticengineer.com](https://agenticengineer.com/tactical-agentic-coding), [YouTube @IndyDevDan](https://youtube.com/@IndyDevDan), [indydevdan.com](https://indydevdan.com/)

---

### C. Addy Osmani — Director Google Cloud AI (ex-Chrome DevTools)

**Кто**: 14 лет в Google, создал Lighthouse, DevTools, Core Web Vitals. Сейчас — Director Google Cloud AI. Написал книгу "Beyond Vibe Coding".

**Его подход к Claude Code Swarms**:
- **Agent Teams** — координированные swarms AI-агентов, работающие параллельно
- Один session = team lead, делегирует задачи teammates
- Каждый teammate — **свой контекстный окно**, работают независимо
- Teammates общаются друг с другом напрямую

**Лучшие юзкейсы по Osmani**:
| Сценарий | Как работает |
|---------|------------|
| Исследование | Несколько teammates исследуют разные аспекты проблемы параллельно, потом challenge findings друг друга |
| Новые модули | Каждый teammate владеет отдельной частью, не мешая другим |
| Дебаг | Teammates тестируют разные гипотезы параллельно, сходятся к ответу быстрее |
| Кросс-слой | Frontend, backend, тесты — каждый слой у своего teammate |

**Принцип**: 80% планирование и ревью, 20% выполнение. Чем лучше спеки — тем лучше выхлоп агента.

> **Источник**: [addyosmani.com/blog/claude-code-agent-teams](https://addyosmani.com/blog/claude-code-agent-teams/), книга "Beyond Vibe Coding" ([beyond.addy.ie](https://beyond.addy.ie/))

---

### D. McKay Wrigley — 3 AI-агента одновременно

**Кто**: AI-предприниматель, educator, создатель Takeoff AI. Активен в Twitter/X.

**Его воркфлоу**:
- Команда `ai` в терминале запускает **3 агента одновременно**: Claude Code + Gemini CLI + Codex CLI
- Полностью синхронизированные окна
- Промптинг голосом
- Hit send — все 3 работают над задачей — **выбираешь победителя**

**Связка с Obsidian**: Claude Code + Obsidian = интеллектуальная система для thinking, research, организации.

> **Источник**: [X @mckaywrigley](https://x.com/mckaywrigley/status/1937978348862578846), [mckaywrigley.substack.com](https://mckaywrigley.substack.com/p/claude-agent)

---

### E. Pieter Levels — $3M/год solo, 40+ стартапов

**Кто**: Самоучка, создал NomadList, RemoteOK, PhotoAI и ещё 40+ продуктов. $170K/месяц. 0 сотрудников. Был на Lex Fridman Podcast.

**Стек**:
- Минимальные зависимости — PHP + jQuery + vanilla (да, в 2026!)
- Один VPS, одна БД, монолит
- Запуск за часы, а не месяцы
- AI (Cursor + Claude) для скорости прототипирования

**Karpathy о нём**: "Cloud+AI делает модель Levels всё более жизнеспособной — один человек может запускать несколько компаний на миллиардные оценки."

> **Источник**: [Lex Fridman #440](https://gist.github.com/m0o0scar/1bc64f4fe050147f0c45155f05cb5e54), [fast-saas.com/blog/pieter-levels-success-story](https://www.fast-saas.com/blog/pieter-levels-success-story/)

---

### F. Andrej Karpathy — Software 2.0, AutoResearch

**Кто**: Ex-Tesla AI Director, co-founder OpenAI, создатель Eureka Labs. Сменил весь воркфлоу на LLM-driven за несколько недель.

**Подход**:
- Минимальные зависимости: Python + LLM API + GPU
- Построил **AutoResearch** — автономный AI-агент для исследований в 630 строках кода
- Получил **NVIDIA DGX Station GB300** для локальных экспериментов
- Философия: "Код переходит от ручного написания к управлению через natural language"

> **Источник**: [Karpathy AutoResearch](https://www.abhs.in/blog/andrej-karpathy-autoresearch-autonomous-ai-ml-experiments-2026), [X @karpathy](https://x.com/karpathy/status/1828210213620748655)

---

### G. Zen Van Riel — Claude Code Swarms эксперт

**Кто**: AI-инженер, блогер. Обнаружил скрытый "swarm mode" в Claude Code до официального анонса.

**Ключевые идеи**:
- Один агент архитектурит, другой реализует, третий ревьюит — всё координированно
- "AI pair programmer" переходит в "AI development team"
- Инструмент `claude-sneakpeek` для доступа к фичам до релиза
- Умение проектировать **роли агентов, протоколы коммуникации, декомпозицию задач** — это то, что отличает топов от остальных

> **Источник**: [zenvanriel.com/ai-engineer-blog/claude-code-swarms](https://zenvanriel.com/ai-engineer-blog/claude-code-swarms-multi-agent-orchestration/)

---

### H. Данные из Anthropic — 2026 Agentic Coding Trends Report

**Официальный отчёт Anthropic** с кейсами крупнейших компаний:

| Компания | Масштаб | Результат |
|---------|--------|----------|
| **Rakuten** | 12.5M строк кода | 99.9% точность модификаций за 7 часов автономной работы |
| **TELUS** | Enterprise telecom | Экономия 500,000 часов |
| **Zapier** | 97% adoption среди инженеров | Полная интеграция в workflow |
| **CRED** | Финтех | Кейс в отчёте |

**8 трендов**:
1. Роли инженеров смещаются к надзору за агентами
2. Multi-agent координация — норма, а не эксперимент
3. Human-AI collaboration паттерны
4. Масштабирование агентного кодирования за пределы инженерии
5. Разработчики используют AI в 60% работы
6. Но только 0-20% задач можно ПОЛНОСТЬЮ делегировать
7. Организации: 30-79% ускорение циклов разработки
8. Безопасность как архитектурный принцип с первого дня

> **Источник**: [Anthropic Agentic Coding Report 2026 (PDF)](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf), [resources.anthropic.com](https://resources.anthropic.com/2026-agentic-coding-trends-report)

---

### I. Успешные соло-фаундеры 2026 года

| Кто | Продукт | Выручка | Стек |
|-----|---------|---------|------|
| **Maor Shlomo** | Base44 (no-code platform) | Продан Wix за **$80M** | AI-генерация, solo, 250K юзеров |
| **Danny Postma** | HeadshotPro | **$300K/мес** | AI headshots, из Бали |
| **Nick Dobos** | BoredHumans (100+ AI tools) | **$8.8M ARR** | Самоучка, indie hacker |

**Статистика**: 38% бизнесов с семизначной выручкой в 2026 — соло-основатели с AI-workflow.

> **Источник**: [crazyburst.com/ai-saas-solo-founder-success-stories-2026](https://crazyburst.com/ai-saas-solo-founder-success-stories-2026/), [greyjournal.net](https://greyjournal.net/hustle/grow/solo-founders-million-dollar-ai-businesses-2026/)

---

## Часть 3: Что взять себе прямо сейчас

### Из сетапа Бориса Черни (создатель Claude Code):
1. **5 параллельных сессий** — ты уже умеешь через tmux/agent teams
2. **PostToolUse хук автоформатирования** — добавить `ruff format` после каждой генерации
3. **Суб-агенты verify-app и code-simplifier** — создать для MarketAI
4. **Sentry MCP** — он это использует, тебе тоже надо
5. **@.claude в PR** для автодобавления в CLAUDE.md — подключить GitHub Action

### Из курса IndyDevDan:
1. **Planning-First** — ты уже делаешь через Plan Mode
2. **Closed Loop Prompts** — добавить верификацию в каждый агентный workflow
3. **ZTE (Zero-Touch Engineering)** — цель: кодовая база шипит сама себя

### Из подхода Addy Osmani:
1. **80/20 правило**: 80% планирование, 20% выполнение
2. **Agent Teams по слоям**: frontend-teammate, backend-teammate, test-teammate

### Из Anthropic Report:
1. **Rakuten-подход**: 12.5M строк = 99.9% точность. Ключ: специализированные агенты в параллельных context windows

---

## Часть 4: Шаги реализации

### Шаг 1: Serena TypeScript support (5 мин)
### Шаг 2: Установить ast-grep (`brew install ast-grep`) (5 мин)
### Шаг 3: Добавить ruff + mypy pre-commit хуки (15 мин)
### Шаг 4: Зарегистрировать другие проекты в Serena (10 мин)
### Шаг 5: Глобальная memory Serena (`global/dmitrij_workflow`) (5 мин)
### Шаг 6: Подключить Sentry MCP (10 мин)
### Шаг 7: Создать суб-агенты verify-app и code-simplifier (10 мин)
### Шаг 8: PostToolUse хук автоформатирования (5 мин)

---

## Проверка

1. `mcp__plugin_serena_serena__find_symbol({name_path_pattern: "AIEngine"})` — класс в engine.py
2. После TypeScript: `get_symbols_overview` на `.tsx` файлы
3. `pytest tests/ -v` — тесты не сломаны
4. `sg -p '$X.get_current_user' marketai/src/` — ast-grep работает
5. Sentry MCP: `sentry:seer` запрос к ошибкам

---

## Все источники

### Топ-разработчики
- [Boris Cherny workflow](https://howborisusesclaudecode.com)
- [VentureBeat: Creator of Claude Code](https://venturebeat.com/technology/the-creator-of-claude-code-just-revealed-his-workflow-and-developers-are)
- [IndyDevDan: Agentic Engineer](https://agenticengineer.com/tactical-agentic-coding)
- [Addy Osmani: Claude Code Swarms](https://addyosmani.com/blog/claude-code-agent-teams/)
- [Addy Osmani: Beyond Vibe Coding](https://beyond.addy.ie/)
- [McKay Wrigley: 3 agents simultaneously](https://x.com/mckaywrigley/status/1937978348862578846)
- [Pieter Levels: $3M/yr solo](https://www.fast-saas.com/blog/pieter-levels-success-story/)
- [Karpathy: AutoResearch](https://www.abhs.in/blog/andrej-karpathy-autoresearch-autonomous-ai-ml-experiments-2026)
- [Zen Van Riel: Claude Swarms](https://zenvanriel.com/ai-engineer-blog/claude-code-swarms-multi-agent-orchestration/)

### Отчёты и исследования
- [Anthropic 2026 Agentic Coding Trends](https://resources.anthropic.com/2026-agentic-coding-trends-report)
- [Solo founder success stories 2026](https://crazyburst.com/ai-saas-solo-founder-success-stories-2026/)
- [AI Tools for Large Codebases](https://www.openaitoolshub.org/en/blog/ai-coding-tools-large-codebases)
- [13 Best AI Tools Complex Codebases](https://www.augmentcode.com/tools/13-best-ai-coding-tools-for-complex-codebases)
- [Best AI Coding Agents 2026](https://www.faros.ai/blog/best-ai-coding-agents-2026)

### Инструменты
- [Serena MCP GitHub](https://github.com/oraios/serena)
- [Best MCP Servers Claude Code](https://www.bannerbear.com/blog/8-best-mcp-servers-for-claude-code-developers-in-2026/)
- [Claude Code Enterprise Governance](https://www.scalekit.com/blog/claude-code-enterprise-mcp-governance)
- [Structuring Claude Code for Production](https://dev.to/lizechengnet/how-to-structure-claude-code-for-production-mcp-servers-subagents-and-claudemd-2026-guide-4gjn)
