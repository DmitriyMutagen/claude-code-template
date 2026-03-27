# WB Content Factory — Полный Аудит Архитектуры + Улучшение Плана

## Context
Пользователь предоставил все исходные материалы проекта: майнд-карты, транскрипты, таблицы данных, архитектурные планы, Google Sheets. Задача — провести полный архитектурный аудит через все 8 кастомных скилов, найти дыры и предложить улучшения.

**Критический баг:** SKU 50 (Креатин) — LLM timeout 600s в Dify. Нужно исправить ПЕРЕД запуском батча.

## Фаза 0: Завершить установку скилов (DONE)

✅ Переписано 8 скилов: roadmap-generator, docs-architect, architecture, neo4j, repo-rag, data-analysis, stitch, local-llm
✅ Переписано 5 стабов: async-python-patterns, agent-memory-systems, workflow-automation, rag-engineer, ai-agents-architect
✅ Создан новый скил: wb-marketplace
⏳ Обновить skills index (000_SKILLS_INDEX.md) — добавить новые скилы

## Фаза 1: Сбор материалов (READ-ONLY)

Прочитать все исходные данные параллельно:

### Файлы проекта
- `/Users/Dmitrij/Documents/Orchestrator/агенты/wb_content_factory/` — весь проект
- Файлы планов: `ROADMAP.md`, `IMPLEMENTATION_PLAN.md`, `prompt_for_code_agent.md`
- Файлы данных: `ФАКТОРЫ_И_ДОЛИ_...md`, `FINAL_KNOWLEDGE_BASE.md`
- Slides OCR: `slides_ocr/` папка
- Tables: `tables_data/` папка

### Google Sheets (читать через WebFetch или gh)
- https://docs.google.com/spreadsheets/d/1rKbV2nGZvnzZZVC6nuGy_h-MRBVyCFPd8ufLNQUMNAc
- https://docs.google.com/spreadsheets/d/1LSx8bg5PvqLbZLMWX0ZfPltUanZdybkqtXVXbB84yaY
- https://docs.google.com/spreadsheets/d/1X6kRrEPDHRE94PmglkZu83xdo2i-fzkes_dPPZ6JvXs

## Фаза 2: Аудит через 8 Скилов

### /stitch — Data Lineage Audit
- Откуда данные? (Google Sheets → JSON → batch_runner)
- Куда идут? (Dify → DOCX/JSON/MD)
- Где разрывы в цепочке?
- Что теряется при трансформации?

### /architecture — System Design Audit
- Dify как единственный источник истины — правильно ли это?
- Узкие места: LLM timeout, последовательная обработка
- ADR: почему Dify, а не прямые LLM-вызовы?
- Масштабируемость: что будет при 10,000 SKU?

### /docs-architect — Module Map
- Все зависимости src/*.py
- Sequence diagrams для ключевых флоу
- API contracts (что принимает, что возвращает каждая функция)

### /roadmap-generator — Plan Audit
- Есть ли roadmap? Актуален ли он?
- Что в backlog, что в progress, что done?
- Critical path: что блокирует финальный результат?

### /data-analysis — Data Quality Audit
- Качество данных в bionovacia_target_skus.json
- Completeness: есть ли пустые поля (Описание, Бренд)?
- Output качество: success rate в output/*.json
- Keyword coverage из tables_data/

### /repo-rag — Code Quality Search
- Найти все TODO, FIXME, HACK
- Найти все hardcoded paths
- Найти все места без error handling
- Найти дублирующийся код

### /neo4j — Knowledge Graph
- Структура: Product → Segment → Keyword → Content
- Какие связи не моделируются сейчас?
- Что можно улучшить в RAG через граф-поиск?

### /local-llm — LLM Strategy Audit
- Текущий: Qwen2.5-72B в Dify → таймаут 600s
- Альтернативы: OpenRouter (Claude), Anthropic API, Ollama
- Cost/speed matrix для всех 175 SKU
- Рекомендация: какой LLM использовать для каждого шага

## Фаза 3: Критические Дыры (Предварительный анализ)

### Дыра 1: LLM Timeout (КРИТИЧНО)
- **Проблема**: Qwen2.5-72B не справляется за 600s
- **Влияние**: 0% success rate для большинства SKU
- **Фикс**: Создать `src/openrouter_pipeline.py` с Claude Sonnet via OpenRouter
- **Файлы**: `src/dify_pipeline.py`, `src/batch_runner.py`, `.env`

### Дыра 2: Нет тестов (ВЫСОКИЙ РИСК)
- **Проблема**: Нет ни одного теста в src/
- **Влияние**: Любой рефакторинг может сломать пайплайн незаметно
- **Фикс**: pytest для critical path (segmentation parsing, TZ generation, file export)

### Дыра 3: Нет валидации output
- **Проблема**: Пустые DOCX сохраняются как "успешные"
- **Влияние**: Ложное ощущение прогресса в batch.log
- **Фикс**: Проверять len(result.briefs) > 0 перед сохранением

### Дыра 4: Нет RAG качества
- **Проблема**: Неизвестно, какие KB chunks используются для каждого товара
- **Влияние**: Плохой RAG = плохие сегменты
- **Фикс**: Логировать retrieved chunks, оценивать relevance score

### Дыра 5: Нет мониторинга
- **Проблема**: batch.log есть, но нет метрик (success rate, avg time, token usage)
- **Влияние**: Нельзя отслеживать улучшения
- **Фикс**: Дашборд в NIGHT_REPORT.md + Prometheus/Grafana (опционально)

## Фаза 4: Улучшенный план

### Немедленно (до запуска батча)
1. **Fix LLM**: Создать `src/openrouter_pipeline.py` → OpenRouter + Claude Sonnet
2. **Validate output**: Проверка `len(briefs) > 0` перед save_docx
3. **Test**: Запустить 3 SKU с новым pipeline, убедиться в качестве

### Краткосрочно (следующая неделя)
4. **Tests**: pytest для critical path
5. **Async batch**: Конвертировать batch_runner в async (3x speedup)
6. **RAG evaluation**: Тест набор для kb retrieval
7. **Monitoring**: Success rate dashboard

### Среднесрочно
8. **Google Sheets integration**: Двусторонняя синхронизация (статус → Sheets)
9. **Neo4j knowledge graph**: Product→Segment→Keyword граф
10. **Quality scoring**: Автоматическая оценка качества ТЗ

## Фаза 5: Имплементация

После аудита — немедленно начинать с:
```
src/openrouter_pipeline.py   — новый pipeline через OpenRouter
src/batch_runner.py          — переключить на openrouter_pipeline
tests/test_pipeline.py       — базовые тесты
```

## Верификация

```bash
# Тест нового pipeline
source /Users/Dmitrij/Documents/Orchestrator/агенты/.venv/bin/activate
python3 -m src.openrouter_pipeline --sku 50  # Должен завершиться за <60s

# Проверка качества
python3 -c "
import json
from pathlib import Path
results = list(Path('output').glob('168510155_*.json'))
for f in results[-1:]:
    data = json.loads(f.read_text())
    segs = data.get('segmentation', {}).get('segments', [])
    print(f'SKU 50: {len(segs)} сегментов, {len(data.get(\"briefs\", []))} ТЗ')
"
```
