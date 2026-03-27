# MarketAI: Plan v2 — 100% Architecture + Remaining Tasks

## Context

Волна 1 завершена (commit 0ae6c5d6). Из 10-слойной CTO-архитектуры внедрено ~75%.
Дмитрий хочет: (1) довнедрить оставшиеся 25% слоёв, (2) закрыть оставшиеся задачи.
**Режим: многоагентный — параллельное исполнение через Team Mode.**

## Что уже СДЕЛАНО (не трогаем)
- Волна 1: UnifiedEngine, Yandex Auth, Sentry 11K fix, API Docs, Security Headers
- SuperClaude v4.3.0, obra/superpowers 3164 skills, Serena + Sentry MCP
- 109 MCP серверов, Memory 3-layer, Pre-commit hooks

---

## ВОЛНА 2A: Довнедрение 10 слоёв до 100% (2-3 часа)

### 2A.1 Parry — Prompt Injection Scanner (15 мин)
**Слой 6. Почему не сделано**: установлен как plugin, но хуки не подключены в settings.json.
**Действия:**
- Прочитать `~/.claude/plugins/parry/` — найти конфиг хуков
- Добавить PreToolUse + PostToolUse хуки в `~/.claude/settings.json`
- Проверить что сканер блокирует тестовую инъекцию

### 2A.2 Dippy — Permission Fatigue Resolver (15 мин)
**Слой 6. Почему не сделано**: установлен, но PreToolUse хук не подключён.
**Действия:**
- Прочитать `~/.claude/plugins/dippy/` — найти хук конфиг
- Добавить PreToolUse хук для auto-approve read-only bash команд
- Проверить что `ls | grep`, `cat file | head` авто-одобряются

### 2A.3 Полный SDD Pipeline (30 мин)
**Слой 4. Почему не сделано**: cc-sdd установлен, но не используется систематически.
**Действия:**
- Создать шаблон SDD workflow в `docs/specs/TEMPLATE.md`
- Настроить /kiro:* команды для MarketAI (steering file с проектным контекстом)
- Прогнать тестовую фичу через полный 5-gate pipeline
- Задокументировать workflow в CLAUDE.md

### 2A.4 ADR систематизация (20 мин)
**Слой 10. Почему не сделано**: шаблон есть, но ADR не пишутся регулярно.
**Действия:**
- Создать ADR для уже принятых решений:
  - `docs/adr/001-polza-ai-as-primary-llm.md`
  - `docs/adr/002-unified-engine-variant-b.md`
  - `docs/adr/003-ym-url-sanitizer.md`
- Добавить правило в CLAUDE.md: "каждое архитектурное решение → ADR"

### 2A.5 Grafana Dashboards (30 мин)
**Слой 8. Почему не сделано**: Prometheus метрики собираются, но dashboards не созданы.
**Действия:**
- Создать `monitoring/grafana/dashboards/marketai-overview.json`
  - AI generation rate, latency p50/p95/p99
  - Error rate by marketplace
  - Token usage (billing)
- Создать `monitoring/grafana/provisioning/` конфиг
- Добавить Grafana в docker-compose.services.yml (если нет)

### 2A.6 Quality Sentinel Hook (20 мин)
**Слой 6. Почему не сделано**: частичная реализация, нет Stop-хука с тестами.
**Действия:**
- Добавить Stop хук в settings.json: при завершении ответа Claude запускает `ruff check` + `python -m pytest tests/ -x -q`
- Если тесты падают — Claude получает ошибку и обязан исправить

---

## ВОЛНА 2B: Оставшиеся бизнес-задачи (параллельно с 2A)

### 2B.1 Sentry: Fix Ozon UUID→int (3840 events) (30 мин)
**PYTHON-FASTAPI-1N**: "invalid literal for int() with base 10: UUID"
**Действия:**
- Найти место в коде где review_external_id (UUID) парсится как int
- Исправить на правильный тип
- Проверить через Sentry что ошибка исчезла

### 2B.2 Sentry: Fix Ozon questions DB type error (200 events) (30 мин)
**PYTHON-FASTAPI-2Y/2X**: "invalid input for query argument $10: str as int"
**Действия:**
- Найти SQL query в sync коннекторе где str передаётся вместо int
- Исправить приведение типов
- Проверить через marketai-db MCP

### 2B.3 Sentry: YM Rate Limit Backoff (45 events) (20 мин)
**PYTHON-FASTAPI-1A**: "420 Enhance your Calm"
**Действия:**
- Добавить exponential backoff в `src/connectors/yandex/client.py`
- Tenacity retry с wait_exponential при 420/429

### 2B.4 Telegram Auth (1 час)
**Действия:**
- Создать `/auth/telegram` endpoint в auth_router.py
- Telegram Login Widget verification (hash check)
- Привязка telegram_id к User модели (проверить поле)
- Frontend: кнопка "Войти через Telegram" на Login.tsx

### 2B.5 Deploy подготовка (30 мин)
**Действия:**
- Проверить docker-compose.prod.yml актуальность
- Создать `docs/runbook/deployment.md` — пошаговый чеклист
- Создать `.env.example` с полным списком переменных

---

## Многоагентное исполнение (Team Mode)

```
Команда: marketai-wave2 (5 агентов параллельно)

Agent 1 (devops-engineer):     2A.1 Parry + 2A.2 Dippy + 2A.6 Quality Sentinel
Agent 2 (python-developer):    2B.1 Ozon UUID fix + 2B.2 DB type fix + 2B.3 YM backoff
Agent 3 (python-developer):    2B.4 Telegram Auth
Agent 4 (architect):           2A.3 SDD Pipeline + 2A.4 ADR
Agent 5 (devops-engineer):     2A.5 Grafana + 2B.5 Deploy prep

Зависимости: нет (все задачи независимы)
Ожидаемое время: 2-3 часа с параллелизацией
```

## Верификация

1. **Hooks**: parry блокирует тестовую injection, Dippy auto-approves `ls | grep`
2. **Sentry**: 3 ошибки resolved (UUID, DB type, rate limit)
3. **Telegram**: login через Telegram Widget → получаем JWT
4. **Grafana**: dashboard открывается, метрики отображаются
5. **SDD**: тестовая фича проходит 5 gates
6. **Quality Sentinel**: при ошибке в коде Claude автоматически фиксит
7. **ADR**: 3 документа в docs/adr/
8. **Тесты**: 791+ passed, 0 regressions
9. **E2E Browser**: полный прогон всех страниц через Playwright

## ЧЕКЛИСТ 100%: Все 10 слоёв CTO-архитектуры

### Слой 1: Clean Architecture — 80% → 100%
- [x] Presentation→Application→Domain←Infrastructure соблюдается
- [x] api/ → services/ → ai/ ← connectors/ структура
- [x] UnifiedEngine создан (adapter pattern)
- [ ] **TODO**: Мигрировать оставшиеся 6 роутеров на UnifiedEngine (ozon, wb, chats, questions, reviews, generation)
- [ ] **TODO**: Разбить engine.py (1746 строк) на модули по 300-400 строк

### Слой 2: SuperClaude — 90% → 100%
- [x] v4.3.0 установлен, 31 команда /sc:*
- [x] Confidence Check работает
- [x] Когнитивные персоны (--architect, --security)
- [x] Wave→Checkpoint→Wave применяется
- [ ] **TODO**: Документировать используемые /sc:* команды в CLAUDE.md (какие, когда)

### Слой 3: obra/superpowers — 70% → 100%
- [x] 3164 скилла установлены
- [x] Auto-activation хук работает
- [x] /brainstorming и /writing-plans используются
- [ ] **TODO**: Принудительный TDD — добавить правило в CLAUDE.md: "для фич >1 дня обязателен /superpowers:test-driven-development"
- [ ] **TODO**: Прогнать 1 фичу через полный цикл brainstorm→plans→worktree→TDD→verify→finish

### Слой 4: SDD (cc-sdd) — 50% → 100%
- [x] cc-sdd установлен, /kiro:* доступны
- [ ] **TODO 2A.3**: Создать steering file для MarketAI
- [ ] **TODO 2A.3**: Создать шаблон `docs/specs/TEMPLATE.md`
- [ ] **TODO 2A.3**: Прогнать Telegram Auth через полный SDD 5-gate pipeline
- [ ] **TODO**: Добавить в CLAUDE.md: "фичи >1 дня → обязательный SDD pipeline"

### Слой 5: Memory Architecture — 85% → 100%
- [x] 3 слоя памяти (global + project + topical)
- [x] Decay система (permanent/7d/30d)
- [x] MEMORY.md обновляется каждую сессию
- [x] Checkpoints сохраняются
- [ ] **TODO**: Установить vexp для AST-графовой памяти (опционально, HIGH effort)
- [x] Можно жить без vexp — файловая память покрывает 95% кейсов

### Слой 6: Hooks — 60% → 100%
- [x] Pre-commit hooks (ruff + ast-grep + secret detection)
- [x] SessionStart hooks (memory restore)
- [x] UserPromptSubmit hooks (skill activation)
- [ ] **TODO 2A.1**: Подключить Parry к PreToolUse/PostToolUse хукам
- [ ] **TODO 2A.2**: Подключить Dippy к PreToolUse хуку
- [ ] **TODO 2A.6**: Добавить Quality Sentinel Stop хук (тесты при завершении)

### Слой 7: Субагенты — 90% → 100%
- [x] Clone Pattern через Agent()
- [x] Team Mode (marketai-wave1 отработал)
- [x] 5 профилей в .claude/agents/
- [x] Model routing (Opus координатор, Sonnet исполнители)
- [ ] **TODO**: Добавить профили для недостающих ролей (devops-engineer, content-writer)

### Слой 8: Observability — 75% → 100%
- [x] Sentry MCP подключён, активно используется
- [x] Prometheus метрики в src/api/metrics.py
- [ ] **TODO 2A.5**: Создать Grafana dashboards (AI latency, errors, business metrics)
- [ ] **TODO**: Prometheus alerting rules (alert при error rate >5%)
- [ ] **SKIP**: Laminar (OTel) — overkill для текущего масштаба, внедрить при >100 клиентов

### Слой 9: MCP серверы — 95% → 100%
- [x] 109 серверов подключены
- [x] Context7, Serena, Playwright, marketplace-api, science-api — используются
- [x] Стратегия "5 мощных шлюзов" соблюдается
- [ ] **TODO**: Документировать топ-10 MCP и когда их использовать (в CLAUDE.md)

### Слой 10: Документация — 70% → 100%
- [x] CLAUDE.md (global + project) с CTO-паттернами
- [x] Memory/, checkpoints/, Todo/Done паттерн
- [ ] **TODO 2A.4**: Создать 3 ADR для принятых решений
- [ ] **TODO 2A.4**: Добавить правило "каждое arch решение → ADR" в CLAUDE.md
- [ ] **TODO**: Добавить "Heavy Words" словарь в CLAUDE.md (YAGNI, KISS, SOLID, DRY)

---

## Итоговый результат

После выполнения всех задач:
- **10 слоёв CTO-архитектуры: 100%** внедрены и применяются
- **Sentry: 3 critical ошибки** закрыты (UUID, DB type, rate limit)
- **Telegram Auth** работает через полный SDD pipeline
- **Deploy** документирован и готов
- **Production readiness: ~90%** (оставшиеся 10% = YuKassa billing, отложен по решению owner)
