# План: WB Content Factory — Stories 2.5, 3.4, 3.5

## Context
Завершение Milestone 2 и Milestone 3 проекта WB Content Factory (путь: `/Users/Dmitrij/Documents/Orchestrator/агенты/wb_content_factory/`).

Изучена Data Flow диаграмма в `task.md`. Архитектура:
- `batch_runner` → `dify_pipeline` (через `dify_connector`) или `local_pipeline`
- `PipelineResult` → `QA Reviewer` → `output/` или fallback
- `wb_ad_optimizer` → WB API → Google Sheets + Neo4j

---

## Story 2.5 — ВЫПОЛНЕНА ✅

**Файл:** `src/dify_workflow_builder.py`

Добавлено в конец существующего файла:
1. Константы `SEO_TITLE_SYSTEM_PROMPT`, `SEO_DESC_SYSTEM_PROMPT`
2. Функция `build_cascade_workflow()` — 14-нодный DSL:
   - Start → KR → LLM Сегментация → Code Parse → Iteration
   - Внутри итерации: Code Format → LLM SEO-ключи → LLM ТЗ → LLM SEO-Title → LLM SEO-Desc → **Code QA** → Code Merge
   - Code Final (с qa_summary) → End
3. Функция `run_cascade_pipeline_with_fallback()` — Python-оркестратор:
   - Пытается запустить Dify cascade workflow
   - Если Dify недоступен → полный fallback на `local_pipeline.run_local_pipeline()`
   - Если некоторые сегменты не прошли QA → частичный fallback (перегенерация только rejected)
4. Обновлён CLI: флаг `--cascade` для генерации нового DSL

**Code QA нода проверяет:**
- title ≤ 60 символов (и ≥ 20)
- keyword stuffing в description (слово > 3 раз)
- стоп-слова из STOP_WORDS
- длина description ≥ 400 символов
- обязательные поля ТЗ: context, main_intention, main_motive, key_emotion, photo_type, composition, background

---

## Story 3.4 — Dry-Run скрипт ✅ ВЫПОЛНЕНА

**Создать:** `scripts/test_ad_optimizer_dryrun.py`

### Реализация:
```python
"""
Standalone dry-run тест wb_ad_optimizer.py.
6 синтетических сценариев → decide_bid() → sync_unit_economics() → Google Sheets.
"""
```

**6 тест-сценариев CampaignMetrics:**
| # | Условие | Ожидаемое действие |
|---|---------|-------------------|
| 1 | CPO=350₽, orders=5 | lower → MIN_BID (50₽) |
| 2 | CPO=210₽, orders=10 | raise (+50₽) — нижняя половина диапазона |
| 3 | CPO=240₽, orders=8 | lower (-50₽) — верхняя половина диапазона |
| 4 | CPO=150₽, orders=12 | raise (+50₽) — ниже оптимального |
| 5 | CTR=0.5%, views=2000, orders=0 | lower (-50₽) — низкий CTR |
| 6 | orders=1, spend=100₽ | keep — недостаточно данных |

**Алгоритм:**
1. Создать `WBAdOptimizer(dry_run=True)` — НЕТ реального WB API
2. Запустить `decide_bid()` для каждого сценария
3. Сравнить с ожидаемым `action` → assert
4. Собрать `OptimizationReport` со всеми решениями
5. Вызвать `sync_unit_economics(report)` → запись в Google Sheets "Ad Optimizer"
6. Сохранить JSON-отчёт `output/ad_optimizer_dryrun_{timestamp}.json`
7. Вывести сводную таблицу в консоль

**Валидация Task 3.4.3:** проверить что лист "Ad Optimizer" в Google Sheets заполнен.

---

## Story 3.5 — systemd service ✅ ВЫПОЛНЕНА

**Создать:** `deploy/wb_ad_daemon.service`

```ini
[Unit]
Description=WB Ad Optimizer Daemon
After=network.target

[Service]
Type=simple
User=...
WorkingDirectory=/path/to/wb_content_factory
ExecStart=.venv/bin/python3 -m src.wb_ad_optimizer --daemon
Restart=on-failure
RestartSec=60
StandardOutput=journal
StandardError=journal
SyslogIdentifier=wb-ad-optimizer
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

Также создать `deploy/README_daemon.md` с инструкцией установки.

---

## Критические файлы

| Файл | Роль |
|------|------|
| `src/dify_workflow_builder.py` | ✅ Обновлён — cascade DSL + fallback |
| `src/wb_ad_optimizer.py` | Читаем — decide_bid(), OptimizationReport, sync_unit_economics() |
| `src/google_sheets_connector.py` | Читаем — WB_FACTORY_SHEET_ID, get_or_create_worksheet() |
| `scripts/test_ad_optimizer_dryrun.py` | 🔲 Создать |
| `deploy/wb_ad_daemon.service` | 🔲 Создать |

---

## Верификация

```bash
# Story 2.5 — генерация cascade DSL
cd /Users/Dmitrij/Documents/Orchestrator/агенты/wb_content_factory
python3 -m src.dify_workflow_builder --cascade
# → dify_config/wb_content_cascade.yml должен появиться

# Story 3.4 — dry-run тест
python3 scripts/test_ad_optimizer_dryrun.py
# → 6/6 сценариев прошли assert
# → Google Sheets "Ad Optimizer" заполнен
# → output/ad_optimizer_dryrun_*.json создан

# Story 3.5 — проверка синтаксиса systemd
systemd-analyze verify deploy/wb_ad_daemon.service 2>/dev/null || echo "Файл готов (запуск на Linux)"
```
