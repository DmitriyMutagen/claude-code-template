# Plan: ТЗ v8 — Grand Unification (Strict RAG Focus)

## Context
Концептуальная ошибка в v7: `cgm_segmentator.py` генерировал тексты "из головы" через local_llm/Gemini, минуя RAG-базу Dify. Нужно переключить всё на Dify Workflow API.

**Уже выполнено в этой сессии:**
- `src/cgm_segmentator.py` полностью переписан: удалён `local_llm`, подключён `DifyConnector`
- Сегментация идёт через `dify.run_workflow_stream()` (streaming, обход таймаута nginx)
- Удалён отдельный `score_segment` — качество контролирует Dify RAG
- Dify workflow проверен: inputs = `product_name`, `article_wb`, `category`, `brand`, `description`
- RAG включён, workflow проходит: Start → RAG: Базы знаний → LLM: Сегментация ЦА

## Оставшийся шаг: создать `src/run_factory.py`

### Файл: `src/run_factory.py`
Push-button CLI-оркестратор. Команда: `python3 -m src.run_factory --full-cycle`

**Step 1: Ingestion** — загрузка товаров из `graph_db_mock.json` (уже существует, вызов `load_products_from_graph()` из cgm_segmentator)

**Step 2: Dify Matrix** — вызов `run_cgm_pipeline()` из обновлённого `cgm_segmentator.py` (строго через Dify)

**Step 3: Visuals** — чтение JSON из `output/cgm_matrix/`, генерация мок-постеров через Pillow (текст на цветном фоне), складывает в `output/final_cards/[SKU]/[Segment]/`

**Step 4: Packaging** — ZIP-архив `upload_ready_YYYY-MM-DD.zip` + Google Sheets экспорт

### Ключевые зависимости
- `src/cgm_segmentator.py` — `run_cgm_pipeline()`, `export_cgm_to_sheets()`, `load_products_from_graph()`, `CGM_DIR`
- `src/google_sheets_connector.py` — `GoogleSheetsConnector.write_data()`
- `PIL` (Pillow) — уже установлен (v11.3.0)

## Verification
```bash
python3 -m src.run_factory --full-cycle
# Проверить:
# 1. output/cgm_matrix/cgm_*.json — JSON файлы от Dify
# 2. output/final_cards/[SKU]/[Segment]/*.png — мок-постеры
# 3. output/upload_ready_*.zip — финальный архив
# 4. Google Sheets Full_Matrix_Output — заполнен данными
```
