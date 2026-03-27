# Автономная ночная разработка — Архитектура и внедрение

## Context

Дмитрий хочет настроить систему автономной ночной разработки уровня Sleepless Agent. Цель: днём планировать задачи (Telegram/CLI), ночью агенты автономно пишут код, утром — готовые ветки/PR. Глобально на ВСЕ проекты + запустить MarketAI этой ночью.

**Решения:** Без бюджетного лимита (watchdog на зацикливание). Mac + VPS. Все задачи MarketAI за ночь. Сразу Sleepless Agent уровень.

## Архитектура: Sleepless Agent (полная)

```
                    ┌─────────────────────────────────────────────┐
                    │        SLEEPLESS AGENT DAEMON                │
                    │     ~/.claude/sleepless/daemon.py            │
                    │     (systemd/launchd, работает 24/7)        │
                    └──────────────┬──────────────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                     ▼
     ┌──────────────┐    ┌──────────────┐     ┌──────────────┐
     │  INPUT LAYER  │    │  SCHEDULER   │     │   REPORTER   │
     │               │    │              │     │              │
     │ - Telegram bot│    │ - Cron tasks │     │ - Telegram   │
     │   /task cmd   │    │ - Sentry     │     │   каждые 30м │
     │ - CLI: sleepy │    │   auto-triage│     │ - Утренний   │
     │   add "..."   │    │ - Periodic   │     │   дайджест   │
     │ - night-queue │    │   sync check │     │ - Ошибки     │
     │   .json       │    │              │     │   мгновенно  │
     └──────┬───────┘    └──────┬───────┘     └──────────────┘
            │                   │
            ▼                   ▼
     ┌─────────────────────────────────────┐
     │          TASK QUEUE (Redis)          │
     │  Приоритеты: critical > high > normal│
     │  Статусы: pending → running → done   │
     └──────────────┬──────────────────────┘
                    │
                    ▼
     ┌─────────────────────────────────────┐
     │         WORKER MANAGER              │
     │  (запускает tmux-сессии)            │
     │                                     │
     │  Правила:                           │
     │  - Max 2 параллельных воркера       │
     │  - RPI: research → plan → implement │
     │  - Two Strikes → skip               │
     │  - Max 60 мин / задача              │
     │  - Merge Contract: ТОЛЬКО ветки     │
     └──────────────┬──────────────────────┘
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
    tmux:worker-1  tmux:worker-2  (idle)
    claude --print claude --print
    project A      project B
```

## Компоненты для создания

### 1. `~/.claude/sleepless/daemon.py` — Главный демон
Python-скрипт (запускается через launchd на Mac, systemd на VPS):
- Слушает: night-queue.json + Redis queue + Telegram webhook
- Управляет воркерами (tmux-сессии с Claude Code CLI)
- Watchdog: мониторит прогресс каждые 5 мин
- Two Strikes: парсит логи, 2 одинаковых фейла → skip
- Reporter: отправляет статус в Telegram

### 2. `~/.claude/sleepless/worker.sh` — Воркер-обёртка
Bash-скрипт запускаемый в tmux:
- `cd` в проект
- `git checkout -b {branch}`
- `claude --print --permission-mode bypassPermissions -p "{prompt}"`
- Логирует output в `~/.claude/sleepless/logs/{task-id}.log`
- При завершении: git add + commit + статус в Redis
- При ошибке: retry 1 раз, потом skip

### 3. `~/.claude/sleepless/telegram_bot.py` — Telegram интерфейс
Используем существующий бот @marketai_auth_bot (или telegram-notify MCP):
- `/task {project} {prompt}` — добавить задачу
- `/status` — текущий статус всех воркеров
- `/queue` — очередь задач
- `/stop` — остановить ночной цикл
- `/results` — результаты завершённых задач
- Автоматические уведомления: старт/финиш/ошибка задачи

### 4. `~/.claude/sleepless/cli.py` — CLI интерфейс
```bash
sleepy add "Deploy MarketAI to VPS" --project ~/Documents/marketai --priority high
sleepy add "Fix questions bug" --project ~/Documents/marketai --priority normal
sleepy status          # показать статус
sleepy queue           # очередь
sleepy start           # запустить daemon
sleepy stop            # остановить
sleepy results         # результаты
sleepy digest          # утренний отчёт
```

### 5. `~/.claude/night-queue.json` — Задачи MarketAI на сегодня
5 задач (Docker deploy, E2E тесты, AI quality, Questions баг, Rate limiter) — последовательно по приоритету.

### 6. `~/.claude/sleepless/config.yaml` — Конфигурация
```yaml
max_parallel_workers: 2
max_task_minutes: 60
watchdog_interval_minutes: 5
no_progress_timeout_minutes: 30
two_strikes_enabled: true
merge_contract: true  # never merge to main
telegram_bot_token: ${TELEGRAM_BOT_TOKEN}  # from .env
telegram_chat_id: "926967075"  # Dmitriy
reporter_interval_minutes: 30
morning_digest_hour: 8
projects:
  marketai:
    path: /Users/Dmitrij/Documents/marketai
    default_branch: main
  mcp-servers:
    path: /Users/Dmitrij/Documents/mcp servers
    default_branch: main
  soulway-b2b:
    path: /Users/Dmitrij/Documents/soulway-b2b
    default_branch: main
  wb-content-factory:
    path: ~/Documents/агенты/wb_content_factory
    default_branch: main
  b2b-outreach:
    path: ~/Documents/Orchestrator/b2b_outreach
    default_branch: main
```

### 7. LaunchAgent (Mac) — автозапуск
`~/Library/LaunchAgents/com.claude.sleepless.plist` — запускает daemon.py при логине.

### 8. Глобальный CLAUDE.md — секция Night Mode
Инструкции для агентов в ночном режиме:
- Merge Contract: только feature/* и fix/* ветки
- Коммитить каждый значимый шаг
- RPI: research → plan → implement
- Max 2 попытки на одну ошибку → skip
- Не трогать .env, credentials
- При непонятной ситуации → пометить задачу blocked, перейти дальше

## Файлы для создания

| Файл | Назначение |
|------|------------|
| `~/.claude/sleepless/daemon.py` | Главный демон (queue + workers + watchdog) |
| `~/.claude/sleepless/worker.sh` | Обёртка для Claude CLI в tmux |
| `~/.claude/sleepless/telegram_bot.py` | Telegram бот для управления |
| `~/.claude/sleepless/cli.py` | CLI `sleepy` для добавления задач |
| `~/.claude/sleepless/config.yaml` | Конфигурация |
| `~/.claude/sleepless/requirements.txt` | Python зависимости |
| `~/.claude/night-queue.json` | Задачи MarketAI на сегодня |
| `~/Library/LaunchAgents/com.claude.sleepless.plist` | Автозапуск на Mac |
| `~/.claude/CLAUDE.md` | EDIT — добавить Night Mode секцию |

## Задачи MarketAI на СЕГОДНЯ

| # | Задача | Ветка | Max мин | Приоритет |
|---|--------|-------|---------|-----------|
| 1 | Docker deploy на VPS | feature/night-docker-deploy | 90 | critical |
| 2 | E2E Playwright тесты | feature/night-e2e-tests | 60 | high |
| 3 | AI quality test (5 отзывов) | feature/night-ai-quality | 45 | high |
| 4 | Questions "Без товара" баг | fix/night-questions-sku | 45 | normal |
| 5 | Rate limiter (ADR-007) | feature/night-rate-limiter | 45 | normal |

## Верификация

1. Запустить daemon.py → убедиться что слушает queue
2. `sleepy add "Test task"` → убедиться задача в очереди
3. Проверить tmux-сессия создалась и Claude работает
4. Проверить Telegram получил уведомление
5. Проверить watchdog работает (kill зависший процесс)
6. Запустить полный цикл из 5 задач MarketAI
7. Утром: проверить результаты по каждой задаче

## Порядок реализации

1. `~/.claude/sleepless/` — директория + config.yaml
2. `daemon.py` — core logic (queue, worker manager, watchdog)
3. `worker.sh` — Claude CLI wrapper
4. `telegram_bot.py` — уведомления + команды
5. `cli.py` — `sleepy` CLI
6. `night-queue.json` — задачи MarketAI
7. LaunchAgent plist — автозапуск
8. CLAUDE.md — Night Mode секция
9. Тестовый запуск → 1 задача
10. Полный запуск → 5 задач MarketAI на ночь
