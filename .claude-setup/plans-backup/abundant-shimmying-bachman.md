# Plan: pandas_data_worker + rich_content_generator + pipeline integration

## Context
Step 1 (KNOWN_SHEETS + discovered_ids.json) is already applied — verified in codebase.
Remaining: create ETL worker for CSV aggregation, create Rich-TZ generator, integrate both into local_pipeline.

Working dir: `/Users/Dmitrij/Documents/Orchestrator/агенты/wb_content_factory`

---

## Step 1: KNOWN_SHEETS — SKIP (already correct)
- `src/analyze_sheets.py:38-59` has 4 correct entries
- `output/sheets_analysis/discovered_ids.json` has 4 correct entries
- Docstring already says "4 смарт-таблиц"

---

## Step 2: Create `src/pandas_data_worker.py` (~300 lines)

### CSV directories verified:
| Section | Directory | Key CSVs |
|---------|-----------|----------|
| ad_payback | `Окупаемость_рекламы_Версия_1/` | `РНП_по_периодам.csv`, `!Воронка_продаж.csv`, `Настройки.csv` |
| queries | `Таблица__Эффективность_поисковых_запросов/` | `Анализ.csv` (3014 rows), `Рекламная_статистика_по_КЗ.csv`, `Отчёт.csv` |
| trends | `НЭП_Тренды_V3/` | `Сводная.csv` (35 rows), `Растущий_тренд_по_слову.csv` |
| naming | `Формирование_наименования/` | `Сведение.csv` (3935 rows) |
| products | `25_02_2026_07_27_Общие_характеристики_одним_файлом/` | `Товары.csv` (269 rows) |

### Structure:
- Class `PandasDataWorker(base_dir=config.TABLES_DATA_DIR)`
- Helpers: `_safe_read_csv()`, `_to_numeric_safe()`, `_read_kv_config()`
- 5 aggregation methods + `aggregate_all()` + `save_summary()`
- CLI with `--section` arg

### Key CSV parsing details (verified from actual files):
- `РНП_по_периодам.csv`: row 1 = meta/dates, row 2 = headers → skiprows=1
- `!Воронка_продаж.csv`: row 1 = "Детальный отчет...", row 2 = headers → skiprows=1
- `Настройки.csv`: rows 1-4 = kv config (Налог, Эквайринг, Логистика), row 5+ = SKU table
- `Анализ.csv`: row 1 = "Настройки" meta, row 2 = headers → skiprows=1
- `Рекламная_статистика_по_КЗ.csv`: row 1 = group headers, row 2 = real columns → skiprows=1
- `Сводная.csv`: standard header row
- `Растущий_тренд_по_слову.csv`: standard header, Дельта column
- `Сведение.csv`: first ~14 rows = config, row 15 = data headers → skiprows=14
- `Товары.csv`: rows 1-2 = meta/empty, row 3 = headers, row 4 = descriptions → skiprows=3, drop iloc[0]

### Imports:
- `pandas`, `csv`, `json`, `argparse`, `sys` from stdlib
- `src.config` — `TABLES_DATA_DIR`, `PROJECT_ROOT`

---

## Step 3: Create `src/rich_content_generator.py` (~250 lines)

### Structure:
- Class `RichContentGenerator(connector=None, llm=None)`
- Property `llm` with lazy init via `LocalLLM()`
- Methods: `load_algorithm_data()`, `load_ranking_factors()`, `generate_rich_brief()`, `generate_for_result()`, `save_rich_tz()`
- CLI with `--article` arg

### Key project imports (verified):
- `src.google_sheets_connector.GoogleSheetsConnector` — `read_all(spreadsheet_id)` returns `List[Dict]`
- `src.local_llm.LocalLLM` — `chat(messages, temperature, max_tokens)` returns `str`
- `src.pipeline.PipelineResult` — has `.briefs`, `.segmentation.segments`, `.product`
- `src.tz_generator.ContentBrief` — has `photo_type`, `composition`, `background`, `color_scheme`, `visual_notes`
- `src.segmentation.Segment` — has `name`, `target_audience`, `dominant_intention`
- `src.config` — `PROJECT_ROOT`, `DOCS_DIR` (confirmed `docs/FINAL_KNOWLEDGE_BASE.md` exists)

---

## Step 4: Integrate into `src/local_pipeline.py`

### 4a: data_summary loading (between lines 362-369, before seg_prompt is built)
- Add `_format_data_summary(summary: dict) -> str` helper function (module-level, above `run_local_pipeline`)
- Inside `run_local_pipeline`, after line 362 (`print("  KB недоступна...")`), load `output/data_summary.json` if exists
- Append `data_context` string to the segmentation prompt via `_build_segmentation_prompt_with_context`
- Actual insertion point: between line 362 and line 369 (`seg_prompt = ...`)

### 4b: Rich content hook (after line 445, after DOCX path print)
- Import `RichContentGenerator` in try/except at module top or inline
- After line 445 (`print(f"  DOCX: {docx_path}")`), add:
  ```python
  try:
      from .rich_content_generator import RichContentGenerator
      rcg = RichContentGenerator(llm=llm)
      rich_tz = rcg.generate_for_result(result)
      if rich_tz:
          rich_path = rcg.save_rich_tz(rich_tz, output_dir)
          print(f"  Rich ТЗ: {rich_path}")
  except Exception as e:
      print(f"  Rich ТЗ: пропущено ({e})")
  ```
- Wrapped in try/except for graceful failure — pipeline continues even if rich gen fails

---

## Files

| File | Action |
|------|--------|
| `src/pandas_data_worker.py` | **Create** (~300 lines) |
| `src/rich_content_generator.py` | **Create** (~250 lines) |
| `src/local_pipeline.py` | **Modify** (add ~30 lines) |

---

## Progress
- [ ] Step 2: `src/pandas_data_worker.py` — TO CREATE (files verified missing)
- [ ] Step 3: `src/rich_content_generator.py` — TO CREATE (files verified missing)
- [ ] Step 4: Integrate into `src/local_pipeline.py`
- [ ] Verification

## Verified CSV details (re-checked 2026-02-28):
- `Настройки.csv`: rows 1-4 are KV pairs (Налог=0.06, Эквайринг=0.015, Логистика за 1 литр=60, доп литр=15), row 5 = SKU table header
- `Сводная.csv`: standard header row 1 (Группа, Словоформы, Ключевая фраза, Предмет, Кластер, Частотность 30 дней, Тренд...)
- `Сведение.csv`: rows 1-13 = config (СЕО ядро section headers), row 14 = blank, row 15 = data headers (Ключевая фраза, Частота, Класс частотности...)
- `Товары.csv`: row 1 = group headers (Основная информация...), row 2 = empty, row 3 = column headers, row 4 = descriptions, row 5+ = data
- `!Воронка_продаж.csv` exists in `Окупаемость_рекламы_Версия_1/`
- `GoogleSheetsConnector.read_all(spreadsheet_id)` returns `List[Dict[str, Any]]` via `get_all_records()`
- `LocalLLM.chat(messages, temperature, max_tokens)` returns `str`
- `ContentBrief` fields: photo_type, composition, background, color_scheme, visual_notes (all str)
- `config.TABLES_DATA_DIR` = `PROJECT_ROOT / "tables_data"`
- `config.DOCS_DIR` = `PROJECT_ROOT / "docs"` (contains `FINAL_KNOWLEDGE_BASE.md`)

## Verification
1. `python3 -m src.pandas_data_worker` — must produce `output/data_summary.json`
2. `python3 -c "from src.pandas_data_worker import PandasDataWorker; print('OK')"`
3. `python3 -c "from src.rich_content_generator import RichContentGenerator; print('OK')"`
4. `python3 -m pytest tests/ -v` — existing tests must pass
