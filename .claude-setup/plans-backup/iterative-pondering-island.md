# Plan: MarketAI — AI Quality, Real-time Dashboard, Competitive Edge

## Context

Сервис запущен и работает. E2E тестирование показало:
- Login, Dashboard, Reviews, Questions, Chats — работают
- AI генерация работает, НО: нет PubMed ссылок, нет cross-sell, системные заметки видны клиенту
- Dashboard показывает 500 отзывов (порция), а не реальное кол-во по каждому кабинету
- Paperclip: 22 done, 12 todo, 5 новых задач (MAR-41-45) поставлены

**Главные цели пользователя:**
1. AI ответы мирового класса: научные ссылки, cross-sell, персонализация, CTA на консультацию
2. Real-time dashboard с полным кол-вом по каждому кабинету/маркетплейсу
3. Конкурентное преимущество — на 10 голов выше конкурентов
4. Всё работает через Claude CLI (Sonnet), не API

---

## Phase A: AI Quality Fix (CRITICAL — Claude Code, ~3 часа)

### A.1 Fix PubMed References — Empty `[]`
**Problem**: AI генерация возвращает `pubmed_refs: []` — научные источники не подтягиваются
**Files**: `src/ai/engine.py`, `src/ai/pubmed.py`, `src/ai/rag.py`
**Fix**:
- Проверить что PubMed Entrez API вызывается при генерации
- Убедиться что PUBMED_API_KEY задан в .env
- Проверить что RAG pipeline включает pubmed search по product ingredients
- Результат: 6 научных ссылок в каждом ответе (номер статьи, авторы, журнал)

### A.2 Fix Cross-sell — Returns `none`
**Problem**: Товарные рекомендации не генерируются
**Files**: `src/ai/cross_sell.py`, `src/ai/engine.py`
**Fix**:
- Проверить что products таблица mapped правильно (354 товара в БД)
- Проверить cross_sell.py логику подбора товаров по категории
- Товар должен быть `is_available=True` в том же магазине
- Результат: 2-3 рекомендации с названиями и SKU

### A.3 Remove System Notes from AI Output
**Problem**: "⚠ Примечание для команды" и "Системное замечание" видны в ответе
**Files**: `src/ai/engine.py`, `src/ai/guardrails.py`, `src/ai/prompts.py`
**Fix**:
- Добавить post-processing: strip всё после `> ⚠` или `> **Системное`
- Или добавить в промпт: "NEVER include system notes, warnings, or internal comments"

### A.4 Enhance Prompt for Selling Quality
**Files**: `src/ai/prompts.py`
**Requirements from user**:
- Имя покупателя (если есть в отзыве)
- Полный контекст товара: название, описание, характеристики, состав
- 6 научных источников (PubMed): номер статьи, авторы, журнал
- Cross-sell: 2-3 товара из того же магазина
- CTA: "Напишите нам в чат магазина для бесплатной консультации с нутрициологом, тренером, специалистом по БАД и спортивному питанию"
- Ответ должен быть продающим, полезным, конвертирующим
- Аккуратно — не навредить бизнесу

### A.5 Product Mapping Check
**Problem**: WB reviews 0% have product_id (69K reviews unlinked)
**Files**: `src/connectors/wb/client.py`, `src/services/sync_engine.py`
**Fix**: Link product_id during WB sync (match by SKU/article)

---

## Phase B: Real-time Dashboard (Claude Code + Paperclip, ~2 часа)

### B.1 Per-Cabinet Stats
**Problem**: Dashboard показывает общие цифры, не per-cabinet
**Files**: `src/api/routers/dashboard.py`, `frontend-react/src/pages/Dashboard.tsx`
**Fix**:
- API endpoint: `/api/v1/dashboard` должен возвращать breakdown по shop_id:
  ```json
  {
    "shops": [
      {"name": "Арагант Ozon", "reviews_total": 13334, "reviews_unanswered": 8500, "questions": 5, "chats_active": 150},
      {"name": "IP Markov WB", "reviews_total": 1585, "reviews_unanswered": 1200, ...}
    ]
  }
  ```
- Frontend: таблица с per-cabinet breakdown

### B.2 Real Count (Not Limited to 500)
**Problem**: Reviews page shows "500 отзывов" — это page limit, не total
**Files**: `src/api/routers/reviews.py`
**Fix**: API уже возвращает `total: 462760` — проблема в frontend пагинации display

### B.3 Auto-refresh
**Problem**: Данные не обновляются без ручного refresh
**Fix**: `setInterval` каждые 60 сек для dashboard, или WebSocket

---

## Phase C: Competitive Research + Unique Features (Paperclip + Claude Code)

### C.1 Research Competitors (Paperclip задача)
- Изучить otveto.ru, ReviewReply, SageSure, Shulex VOC
- Собрать список их фич
- Выявить что у нас есть уникального и чего не хватает

### C.2 Unique Features to Add
Based on existing competitor analysis (see `memory/project_competitor_analysis.md`):

| Feature | У конкурентов | У нас | Priority |
|---------|-------------|-------|----------|
| Chrome Extension | otveto.ru | Нет | HIGH |
| Answer Templates | otveto.ru (100+) | Нет (MAR-42) | HIGH |
| AI Categorization | SageSure | Нет (MAR-43) | MEDIUM |
| PubMed Citations | Никто | Есть (но broken) | CRITICAL FIX |
| Per-task Model Routing | Никто | Есть | Unique |
| Scientific RAG | Никто | Есть (нужен fix) | Unique |
| Real-time Sync | Некоторые | Есть | Parity |
| Multi-marketplace | otveto.ru | Ozon+WB+YM | Parity |
| Freemium | otveto.ru | Есть (30/мес) | Parity |

**Our unique edge (no one else has):**
1. PubMed scientific citations in responses
2. BAD/supplement niche-specific prompts
3. Per-task model routing (Claude for chats, Gemini for reviews)
4. Cross-sell based on actual store inventory

### C.3 Features to Add for 10x Advantage
1. **Sentiment Trend Dashboard** — графики тональности по дням
2. **Competitor Review Scanner** — парсинг отзывов конкурентов
3. **Auto-response for 5-star** — автоматическая отправка без модерации для 5-звёзд
4. **Review Response A/B Testing** — тест разных стилей ответов
5. **Telegram Bot** — уведомления о негативных отзывах + quick approve
6. **Chrome Extension** — ответы прямо на странице маркетплейса
7. **Nutrition Expert AI Agent** — для чата: полноценный нутрициолог-консультант
8. **QR-code in response** — ссылка на консультацию через QR

---

## Phase D: Paperclip Task Review + New Tasks

### Current Paperclip Status: 22 done, 17 todo

### New Tasks to Create:
1. **CEO**: Review AI response quality, check prompts for selling effectiveness
2. **Backend Eng**: Fix PubMed integration (empty refs), fix cross-sell (none)
3. **Frontend Eng**: Per-cabinet dashboard stats, auto-refresh
4. **AI Eng**: Enhance prompts — add CTA, scientific refs format, remove system notes
5. **Researcher**: Competitor deep-dive — otveto.ru feature list, pricing, UX

---

## Phase E: Execution Order

```
NOW (Claude Code):
├── A.3: Remove system notes from AI output
├── A.1: Debug PubMed refs (why empty)
├── A.2: Debug cross-sell (why none)
├── A.4: Enhance prompts
└── Commit + Push

PARALLEL (Paperclip):
├── MAR-41: Skeleton loaders (Frontend)
├── MAR-42: Answer templates (Backend)
├── MAR-43: AI categorization (AI Eng)
├── MAR-44: E2E tests (QA)
├── MAR-45: Docker + /health (DevOps)
└── NEW: Per-cabinet dashboard, competitor research

NEXT SESSION:
├── B: Dashboard improvements
├── C: Chrome Extension MVP
└── WB product_id linking
```

---

## Verification

```bash
# AI response quality check
TOKEN=$(cat /tmp/marketai-token.txt)
curl -s -X POST "http://localhost:8001/api/v1/ai/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"review_text":"Креатин хороший","rating":5,"marketplace":"ozon","product_name":"Креатин SoulWay"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'PubMed: {len(d.get(\"pubmed_refs\",[]))} refs'); print(f'Cross-sell: {d.get(\"cross_sell_products\",\"none\")}'); print('System notes visible' if 'Системное' in d.get('ai_draft','') else 'Clean output')"

# Dashboard per-cabinet
curl -s "http://localhost:8001/api/v1/admin/sync-status" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Paperclip progress
curl -s http://127.0.0.1:3100/api/companies/f9486b3f.../issues | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Done: {sum(1 for i in d if i[\"status\"]==\"done\")}/{len(d)}')"
```

## Phase F: AI Response Quality — 10/10 Score

### F.1 Quality Scoring Criteria
Каждый AI-ответ должен набирать 10/10 по параметрам:

| Параметр | Вес | Описание |
|----------|-----|----------|
| Человечность | 2/10 | Не звучит как робот, живое общение, российский менталитет |
| Научность | 2/10 | 6 PubMed ссылок с номерами, авторами, журналом |
| Продающесть | 2/10 | Cross-sell 2-3 товара, CTA на консультацию |
| Полезность | 1/10 | Реально решает вопрос/проблему покупателя |
| Персонализация | 1/10 | Имя, контекст товара, характеристики |
| Безопасность | 1/10 | Нет мед. советов, нет обещаний, guardrails |
| Форматирование | 1/10 | Читаемо, структурировано, не перегружено |

### F.2 Anti-AI Detection (Human-like Writing)
**Problem**: Тексты не должны быть "яичными" (AI-generated, robotic)
**Solution**:
- Промпт: "Пиши как реальный менеджер по работе с клиентами. НЕ используй: 'Мы рады', 'Благодарим за обращение', 'Мы ценим ваш отзыв'. Пиши просто, по-человечески, как общение в мессенджере."
- Добавить вариативность: разные приветствия, разный порядок блоков
- Российский менталитет: прямолинейность, конкретика, без канцеляризмов
- Найти skill `avoid-ai-writing` или `beautiful-prose` для anti-AI patterns

### F.3 Quality Evaluation Loop
- После генерации — автоматическая оценка ответа по 7 критериям
- Если score < 8/10 → перегенерация с feedback
- Использовать `src/ai/guardrails.py` для quality gate

---

## Phase G: 12-Source Scientific API Stack

### Current: 7 sources already integrated
1. PubMed (pubmed.py) - ACTIVE, key set
2. USDA FoodData (usda.py) - ACTIVE, DEMO_KEY
3. NIH DSLD (dsld.py) - ACTIVE, no key
4. OpenFDA CAERS (openfda.py) - ACTIVE, no key
5. Semantic Scholar (semantic_scholar.py) - ACTIVE, free
6. NIH ODS Fact Sheets (ods_factsheets.py) - ACTIVE, no key
7. Local Supplement DB (supplement_db.py) - 100+ profiles, 144 synergy rules

### To Add: 5 new sources
8. **NCCIH HerbList** → `src/ai/nccih.py` (herbs, alternative medicine)
9. **OpenAlex** → `src/ai/openalex.py` (10M+ papers, free, citations)
10. **Cochrane** → `src/ai/cochrane.py` (systematic reviews)
11. **ExerciseDB** → `src/ai/exercisedb.py` (exercise-supplement)
12. **Open Food Facts** → `src/ai/openfoodfacts.py` (barcode → ingredients)

### Fix: ingredient_parser.py — add English key mapping
### Fix: USDA — get production API key (not DEMO_KEY)
### Paperclip tasks: AI Eng → NCCIH+OpenAlex, Backend → Cochrane+OpenFoodFacts

## Phase H: Regulatory Compliance Layer (RU/EAEU)

### Add to AI prompts as safety guardrails:
- "Это БАД, не лекарство"
- "Перед применением ознакомьтесь с противопоказаниями"
- "Не является заменой разнообразного питания"
- "Проверьте индивидуальную переносимость компонентов"

### Regulatory sources to integrate into `supplement_db.py`:
- ТР ТС 021/2011 (безопасность пищевой продукции)
- ТР ТС 029/2012 (пищевые добавки, ароматизаторы)
- Роспотребнадзор реестр БАДов
- МР 2.3.1.2432-08 (нормы потребления)

### For guardrails.py — add checks:
- No medical/treatment claims in AI output
- Mandatory disclaimer for BAD products
- No mixing BAD with "лечение" or "лекарство"

## Phase I: Smart Cross-Sell Recommendation System

### Current Problems:
- CrossSellMatrix DB table = EMPTY (0 rows)
- UI shows manual input only, no auto-population
- WB shops: prices = 0 (not synced)
- Ozon: 88% products unavailable (sync bug)
- Candidates hardcoded to max 2 (cross_sell.py line 128)

### Architecture: Auto-Populate Recommendations Per Shop
1. **On product sync** → auto-generate CrossSellMatrix entries using synergy_rules.json
2. **Per-shop catalog** → only recommend products available in THAT shop
3. **Scientific basis** → each recommendation has PMID + reason
4. **Price-aware** → show price, calculate bundle discount
5. **Rotation** → top 5-10 recommendations per product, rotate in responses

### Implementation:
- `src/ai/cross_sell.py`: add `populate_cross_sell_matrix(shop_id, db)` function
- `src/api/routers/store_settings.py`: add endpoint `POST /cross-sell/auto-populate`
- Frontend Settings: show auto-generated recommendations with edit capability
- Fix: `candidates[:2]` → respect `store_settings.cross_sell.max_products`

### Fixes needed NOW:
- CTA duplication: DONE (commit 4715d04c)
- PubMed refs [] in API: fix engine.py to populate pubmed_refs from scientific_rag
- Ozon enrichment: use `/products/{id}/enrich` endpoint
- PubMed queries in English: already done (ingredient_parser translates RU→EN)
- AI should translate scientific refs to Russian in response text

## AI Generation Test Results (2026-03-22)
- Model: claude-sonnet-4-6 via CLI
- Review: "Очень порадовал, пьём вместе с сыном" (5 stars, WPC 80 Ваниль)
- Response: human-like, PubMed ref (PMID: 19106243), cross-sell креатин, CTA
- Quality: 8/10 (missing: PubMed refs in API response array, double CTA)
- Time: 86 sec (CLI overhead)
- Cross-sell: креатин300_ананас (matched from product catalog)

## Phase J: Autonomous Monitoring & Self-Healing (после 100% готовности)

### J.1 Loop Mode (`/loop 5m`)
Каждые 5 минут автоматическая проверка:
- Backend alive? `curl http://localhost:8001/health`
- Errors count? `GET /admin/errors/stats` → если >0, анализ + auto-fix
- Sync running? `GET /admin/sync-status` → если last_sync >30 мин, trigger sync
- New reviews? → если есть new без AI response, запустить генерацию
- При проблеме → auto-fix + отчёт в Telegram

### J.2 Hooks (settings.json)
- `PostToolUse(Edit|Write)` → `pytest tests/ -x --tb=short` (автотесты после каждого изменения)
- `Stop` → snapshot состояния в session-handoff.md + git commit
- `CronCreate` → health-check каждые 10 мин

### J.3 Background Monitoring Agent
- Запуск: `Agent(subagent_type="loop-operator", run_in_background=true)`
- Мониторит: backend logs, sync gaps, data quality, AI response quality
- При ошибке: notification в Telegram + auto-fix если возможно
- Ежедневный отчёт: сколько обработано, качество ответов, ошибки

### J.4 Когда настраивать
- ПОСЛЕ того как сервис на 100% готов и протестирован
- ПОСЛЕ деплоя на сервер
- Loop mode + hooks = для dev/staging
- Background agent = для production

---

## Phase K: Server Deployment (после локальных тестов)

### K.1 Подготовка
- Docker Compose prod: `docker-compose.prod.yml`
- SSL/HTTPS через nginx + certbot
- Env vars на сервере (DATABASE_URL, API keys)
- Claude Code CLI установлен на сервере

### K.2 Деплой
- `scp` или `git clone` на сервер
- `docker-compose -f docker-compose.prod.yml up -d`
- Проверка health endpoint
- Настройка cron для sync + watchdog

### K.3 Автономная работа
- Claude Code на сервере в loop mode
- Автоматическая обработка новых отзывов
- Мониторинг через Telegram бот
- Self-healing при ошибках

---

## Phase L: Visual E2E Testing — Priority Pages

### L.1 Questions Page (PRIORITY — "самая сырая")
- Проверить: вопросы тянутся для КАЖДОГО кабинета (Ozon, WB, YM)
- Проверить: вопросы только от покупателей (не системные)
- Проверить: AI генерация ответов на вопросы работает
- Проверить: корректная привязка к товару

### L.2 Chats Page (PRIORITY — "самая сырая")
- Проверить: загружаются ТОЛЬКО чаты с покупателями (не техподдержка, не уведомления)
- Ozon: чаты через `/v2/chat/list` — фильтровать по типу
- WB: чаты через questions API
- YM: чаты через партнёрский API
- Проверить: AI-ответы в чатах работают
- Проверить: нет системных/рекламных сообщений в списке

### L.3 All Other Pages — визуальный прогон
- Dashboard: per-cabinet stats отображаются
- Reviews: фильтры, AI generation, expand response
- Shops: настройки, cross-sell recommendations
- Settings: AI models, max_tokens, temperature
- Analytics + Admin/Monitoring

## COMPLETED TASKS LOG (2026-03-22)
- [x] Git cleanup: 17 скриптов удалены, 7 логических коммитов
- [x] Frontend build: 0 TS ошибок, 633 tests passed
- [x] AI Engine: cross-sell fix, system notes strip, ingredient parser English
- [x] Промпты: human-like, anti-AI, CTA, научные ссылки
- [x] Product enrichment: Ozon 141/141, WB 80-83/83, YM 50/50
- [x] Max tokens: 1000 → 8000 для всех магазинов
- [x] Model: claude-sonnet-4-6 через CLI
- [x] Guardrails: regulatory disclaimers (ТР ТС), re-gen protection
- [x] 5301 ошибок очищены, BUG-01 + BUG-02 исправлены
- [x] Paperclip: 53 задачи, 24 done, интервалы ускорены (10мин → 2мин)
- [x] Scientific RAG: triggers on product_name (not just composition)
- [x] 18 коммитов pushed to GitHub
- [ ] Dashboard per-cabinet (agent working)
- [ ] Cross-sell auto-populate (agent working)
- [ ] Autonomous monitoring setup
- [ ] Server deployment

---

## Critical Files
| File | Action |
|------|--------|
| `src/ai/engine.py` | System notes strip (DONE), cross-sell fix (DONE) |
| `src/ai/prompts.py` | Enhance: CTA, scientific format, anti-AI, selling tone |
| `src/ai/ingredient_parser.py` | Add English key mapping |
| `src/ai/scientific_rag.py` | Add 5 new sources to parallel pipeline |
| `src/services/scientific_cache.py` | TTL config for new sources |
| `src/api/routers/dashboard.py` | Per-cabinet stats |
| `src/connectors/wb/client.py` | Link product_id during sync |
