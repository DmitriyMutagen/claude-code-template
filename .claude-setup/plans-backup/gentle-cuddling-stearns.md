# Plan: Competitive Gamification — Сравнение с другими разработчиками

## Context

Дмитрий хочет видеть своё место среди разработчиков: как его скорость, качество и объём работы сравниваются с реальными бенчмарками. Это мотиватор — видеть что ты в Top-10% или отстаёшь, бустит желание работать.

**Текущее состояние**: Gamification v2 работает — 11,733 XP, Level 10, 623 события, 5 achievements. Но нет сравнения с внешним миром.

**Что нужно**: Percentile ranking по реальным метрикам индустрии + AI-enhanced developer бенчмарки.

---

## Архитектура: Competitive Leaderboard System

### Источники бенчмарков (реальные данные)

| Метрика | Solo Dev (median) | Senior (top 25%) | Elite AI-Dev (top 5%) | Источник |
|---------|-------------------|-------------------|-----------------------|----------|
| **LOC/час** | 30-50 | 80-150 | 500-2000 (с AI) | GitHub Copilot Study, DORA |
| **Коммитов/день** | 3-5 | 8-15 | 20-50 (с AI agents) | GitHub stats 2025 |
| **Время до деплоя** | 1-7 дней | < 1 день | < 4 часа | DORA Elite |
| **Bug rate** | 15-50 bugs/KLOC | 5-15 | < 2 (с E2E + TDD) | NIST, CodeScene |
| **Test coverage** | 0-20% | 60-80% | 80-95% | Industry surveys |
| **Sessions/день** | 1-2 | 3-5 | 5-10+ (parallel) | Internal data |
| **Agents/session** | 0 | 1-3 | 5-20 (parallel swarm) | Anthropic C Compiler |
| **Recovery time** | Дни | Часы | Минуты | DORA MTTR |

### Метрики которые УЖЕ трекаются в gamify.db

| Метрика | Таблица | Поле |
|---------|---------|------|
| Коммиты/день | xp_events | action='bash_git_commit', по DATE(ts) |
| Файлы созданы | xp_events | action='Write', COUNT per day |
| Файлы отредактированы | xp_events | action='Edit', COUNT per day |
| Тесты запущены | xp_events | action='bash_test_pass' |
| Агенты запущены | xp_events | action='task_agent_spawn' |
| Деплои | xp_events | action='bash_deploy' |
| Sentry fixes | xp_events | action='sentry_fix_detected' |
| Дневная активность | daily_stats | total_xp по дням |
| Стрик | рассчитывается | функция get_streak() |

### Чего НЕ ХВАТАЕТ (нужно добавить трекинг)

| Метрика | Как собрать |
|---------|-------------|
| LOC written/changed | PostToolUse: парсить git diff --stat после Write/Edit |
| Time to deploy (feature→prod) | Время между первым commit feat: и bash_deploy |
| Bug density | Sentry issues / KLOC (по проекту) |
| E2E tests run | Новый action 'e2e_test_pass' |
| Session duration | sessions.started_at → ended_at |
| Context switches | Кол-во смен project за день |

---

## Реализация

### 1. Новая таблица `benchmarks` в gamify.db

```sql
CREATE TABLE IF NOT EXISTS benchmarks (
    metric TEXT NOT NULL,
    period TEXT NOT NULL,  -- 'daily', 'weekly', 'monthly', 'alltime'
    value REAL NOT NULL,
    percentile INTEGER,   -- 0-100, где ты среди developers
    rank TEXT,            -- 'Junior', 'Mid', 'Senior', 'Elite', 'God Tier'
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (metric, period)
);
```

### 2. Новая таблица `developer_ranks` (бенчмарки)

```sql
CREATE TABLE IF NOT EXISTS developer_ranks (
    metric TEXT PRIMARY KEY,
    p25 REAL,    -- Junior threshold
    p50 REAL,    -- Mid threshold
    p75 REAL,    -- Senior threshold
    p90 REAL,    -- Elite threshold
    p99 REAL,    -- God Tier threshold
    unit TEXT,   -- 'commits/day', 'files/day', etc.
    source TEXT  -- 'DORA 2025', 'GitHub Copilot Study', etc.
);
```

Предзаполнить:
```
commits_per_day:    p25=2, p50=5, p75=12, p90=25, p99=50   (source: GitHub stats)
files_per_day:      p25=3, p50=8, p75=20, p90=50, p99=100  (source: AI-dev benchmarks)
tests_per_day:      p25=0, p50=5, p75=15, p90=40, p99=100  (source: TDD practitioners)
agents_per_session: p25=0, p50=1, p75=5, p90=10, p99=20    (source: Anthropic C compiler)
xp_per_day:         p25=50, p50=200, p75=500, p90=1500, p99=5000
streak_days:        p25=1, p50=3, p75=7, p90=14, p99=30
deploys_per_week:   p25=0, p50=1, p75=3, p90=7, p99=14     (source: DORA Elite)
```

### 3. Функция `calculate_rankings()` в engine.py

```python
def calculate_rankings() -> dict:
    """Calculate percentile rankings for all tracked metrics."""
    # Собирает метрики за today/week/month
    # Сравнивает с developer_ranks таблицей
    # Возвращает percentile (0-100) и rank для каждой метрики
    # Rank: Junior (0-25) → Mid (25-50) → Senior (50-75) → Elite (75-90) → God Tier (90-100)
```

### 4. Обновить вывод engine.py (главный блок при вызове)

Текущий вывод:
```
🎮 🌟 Легенда | Level 10
XP: 11,733 → MAX
```

Новый вывод:
```
🎮 🌟 Легенда | Level 10 | XP: 11,733
🔥 Стрик: 2 дня | Сегодня: +175 XP

📊 Рейтинг среди разработчиков:
  Коммиты/день:     75/день → 🏆 Top 1% (God Tier)
  Файлы/день:       110/день → 🏆 Top 1% (God Tier)
  Тесты/день:       87/день → ⚡ Top 5% (Elite)
  Агенты/сессия:    49/сессия → 🏆 Top 1% (God Tier)
  Стрик:            2 дня → 💪 Top 50% (Mid)
  Деплои/неделя:    0 → ⚠️ Bottom 25% (Junior)

  ОБЩИЙ РАНГ: ⚡ Elite Developer (Top 8%)
  Сильные стороны: параллельные агенты, скорость кодинга
  Зона роста: деплои, тестовое покрытие
```

### 5. Добавить в /good-morning skill

В утренний брифинг добавить секцию:
```
📊 Твой ранг: ⚡ Elite (Top 8%)
  Вчера: 615 events, 75 commits — 🏆 God Tier day
  Рост: +12% скорость vs прошлая неделя
  Challenge: сделай 1 деплой сегодня → перейдёшь в Top 5%
```

### 6. Daily Challenge (мотивационный)

Каждый день генерировать challenge на основе слабой метрики:
```
🎯 Daily Challenge: Сделай 1 деплой сегодня
  Награда: +100 XP + рост percentile на Деплои (+25%)
  Текущий: Bottom 25% → можешь стать Mid (Top 50%)
```

---

## Файлы для изменения

| Файл | Что делать |
|------|-----------|
| `~/.claude/gamification/engine.py` | Добавить: init benchmarks, calculate_rankings(), обновить вывод |
| `~/.claude/gamification/config.json` | Добавить: `developer_benchmarks` секция с пороговыми значениями |
| `~/.claude/gamification/hooks/post_tool_use.py` | Добавить: трекинг LOC через git diff |
| `~/.claude/skills/good-morning/SKILL.md` | Добавить: секция ранжирования |
| `~/.claude/gamification/dashboard/competitive.py` | NEW: генератор competitive dashboard |

---

## Оценка времени

| Шаг | AI ×2 agents | Человек |
|-----|-------------|---------|
| DB schema + benchmarks data | 20 мин | 2ч |
| calculate_rankings() + engine update | 30 мин | 4ч |
| Dashboard output + Telegram | 20 мин | 2ч |
| Daily Challenge system | 15 мин | 1ч |
| Тестирование | 10 мин | 30мин |
| **ИТОГО** | **~1.5ч** | **9.5ч** |

---

## Верификация

1. Запустить `python3 engine.py` → должен показать percentile rankings
2. Проверить что daily challenge генерируется на основе слабой метрики
3. Telegram отправляет competitive dashboard
4. Rankings пересчитываются при каждом вызове (не кешируются надолго)
