# План: Массовый прогон 91 товара WB + SEO-семантика из 300K запросов

## Context
Прогнать ВСЕ 91 товар (11 Excel-файлов) через v11 QA систему с использованием реальной семантики из 300K+ WB/Ozon запросов. Оригиналы НЕ трогаем. Результат — копии XLSX + полный аудит "было → стало".

## Файлы для изменения
1. **`src/enrichment_pipeline.py`** (704 строки) — KeywordMatcher, CheckpointManager, AuditTracker, промпт, CLI, logging
2. **`src/wb_qa_multilevel.py`** (~1650 строк) — AutoFixer для плейсхолдеров (строка 721, 753-922)

## Входные данные (ВЕРИФИЦИРОВАНО 01.03.2026)

### Товары (11 XLSX)
`~/Downloads/01.03.2026_09.40_Все характеристики по предметам/`:
- Протеин (51K), Креатины (39K), Гейнеры (37K), БАДы (35K)
- Комплексные пищевые добавки (38K), Бустеры тестостерона (31K)
- Добавки для суставов и связок (33K), Аминокислоты (31K)
- Семена пищевые (31K), Аптечки для хранения лекарств (30K), L-карнитины (31K)

### Ключевые запросы (2 основных источника)
1. **300K WB** — `~/Downloads/300 тыс запросов с 27.11.2025 по 24.02.2026.zip` (33MB)
   - Sheet: "Детальная информация", header=1
   - Columns: `Поисковый запрос`, `Количество запросов`
2. **Ozon 10K** — `~/Downloads/queries_report-2026-02-28_18_25.xlsx` (1.2MB)

**ВАЖНО**: SoulWay CSV, Top50 SEO CSV и Keyword universe CSV — НЕ найдены в ~/Downloads. KeywordMatcher загружает только реально существующие файлы (graceful skip).

## Выходная структура
```
output/Processed_01.03.2026_09.40_Все характеристики/
  *.xlsx                    ← 11 копий с обогащёнными полями
  .checkpoints/             ← resume при обрыве
  keywords/                 ← {category}_keywords.json
  ENRICHMENT_REPORT.md      ← сводка: файлы, товары, QA
  AUDIT_BEFORE_AFTER.md     ← "было → стало" каждый товар
```

---

## Реализация

### Шаг 1: KeywordMatcher — `enrichment_pipeline.py` (новый класс ~100 строк)

Вставить ПОСЛЕ строки 48 (после `SEO_COLUMNS`), ПЕРЕД `read_wb_xlsx()`.

```python
import zipfile
import logging

LOG_FILE = config.PROJECT_ROOT / "enrichment_batch.log"
logger = logging.getLogger("enrichment")
# Setup: FileHandler(DEBUG) + StreamHandler(INFO)

CATEGORY_SEARCH_TERMS = {
    "Протеин": ["протеин", "белок", "protein", "сывороточн", "казеин", "изолят"],
    "Креатины": ["креатин", "creatine", "моногидрат"],
    "Гейнеры": ["гейнер", "gainer", "масс"],
    "БАДы": ["бад", "витамин", "добавк", "supplement"],
    "Аминокислоты": ["аминокислот", "bcaa", "amino"],
    "L-карнитины": ["карнитин", "l-carnitine", "жиросжигат"],
    "Бустеры тестостерона": ["тестостерон", "бустер", "tribulus"],
    "Добавки для суставов": ["суставы", "глюкозамин", "хондроитин", "коллаген"],
    "Комплексные пищевые добавки": ["комплекс", "мультивитамин", "спортпит"],
    "Аптечки": ["аптечк", "органайзер", "таблетниц"],
    "Семена пищевые": ["семена", "чиа", "лён", "суперфуд"],
}

# Пути к файлам ключевых запросов
WB_KEYWORDS_ZIP = Path.home() / "Downloads" / "300 тыс запросов с 27.11.2025 по 24.02.2026.zip"
OZON_KEYWORDS_XLSX = Path.home() / "Downloads" / "queries_report-2026-02-28_18_25.xlsx"

class KeywordMatcher:
    """Подбирает реальные поисковые запросы для категории товара."""
    def __init__(self):
        self._df = None  # lazy: pd.DataFrame[query, frequency, source]
        self._cache = {}  # {category: [sorted kw dicts]}

    def _load(self):
        # Загрузить WB 300K из ZIP → pd.read_excel(sheet_name="Детальная информация", header=1)
        # Загрузить Ozon queries
        # Graceful skip если файл не найден
        # Объединить в единый DataFrame [query, frequency, source]

    def get_keywords(self, category: str, top_n=50) -> List[Dict]:
        # Маппинг category → search terms через CATEGORY_SEARCH_TERMS (partial match)
        # Фильтр DataFrame: any(term in query for term in search_terms)
        # Sort by frequency DESC, return top_n as [{query, freq, source}]

    def save_category_keywords(self, output_dir: Path):
        # Для каждой категории → keywords/{cat}_keywords.json
```

### Шаг 2: CheckpointManager — `enrichment_pipeline.py` (новый класс ~60 строк)

Вставить после KeywordMatcher.

```python
class CheckpointManager:
    def __init__(self, checkpoint_dir: Path):
        self.dir = checkpoint_dir
        self.dir.mkdir(parents=True, exist_ok=True)

    def save(self, file_name, row_idx, enriched, qa, before_data):
        # → .checkpoints/{file_stem}_{row_idx}.json

    def get_processed(self, file_name) -> set:
        # Сканировать .checkpoints/{file_stem}_*.json → set of row_idx

    def load(self, file_name, row_idx) -> dict:
        # Загрузить один checkpoint

    def check_pause_stop(self) -> str:
        # Проверить наличие PAUSE/STOP файлов в PROJECT_ROOT
        # return 'run' | 'pause' | 'stop'
```

### Шаг 3: AuditTracker — `enrichment_pipeline.py` (новый класс ~100 строк)

```python
class AuditTracker:
    def __init__(self):
        self.records = []
        self.file_stats = {}

    def record_before(self, product, file_name):
    def record_after(self, product, enriched, qa):
    def write_report(self, output_dir, total_time):
        # ENRICHMENT_REPORT.md — таблица: Категория | Товаров | QA ср. | PASS | FAIL
    def write_audit(self, output_dir):
        # AUDIT_BEFORE_AFTER.md — "было → стало" по каждому товару
```

### Шаг 4: NotebookLM resilience — `enrichment_pipeline.py` строка 207

Заменить `NotebookLMSource.ask()` (строки 207-217):
- Добавить retry loop (3 попытки) с backoff [5, 10, 20]s
- Auth error → reconnect (self._connector = None → _init())
- Graceful degradation: если NotebookLM недоступен, продолжить без него

**КРИТИЧНО**: Убрать жёсткую проверку `if not notebooklm.is_available: return {}` в `run_enrichment()` (строки 576-582) → заменить на warning.

### Шаг 5: Усиление промпта — `enrichment_pipeline.py`

**ENRICHMENT_SYSTEM_PROMPT** (строки 286-346): добавить секцию ХАРАКТЕРИСТИКИ после строки 344:
```
═══ ХАРАКТЕРИСТИКИ (ПРИОРИТЕТ!) ═══
1. Заполняй ВСЕ поля (100% target). <80% = -15-25% видимости.
2. Каждое поле — конкретное значение, НЕ плейсхолдер.
3. Числовые поля — ЧИСЛО + единица ("500 г", "30 порций").
```

**enrich_product()** (строки 358-529):
- Добавить `keyword_matcher: KeywordMatcher = None` в параметры
- В user_prompt добавить секции ВЧ-ЗАПРОСОВ и ХАРАКТЕРИСТИК
- В selective regen loop: сохранять характеристики при перегенерации SEO-полей

### Шаг 6: AutoFixer для плейсхолдеров — `wb_qa_multilevel.py`

**Строка 721**: `auto_fixable=False` → `auto_fixable=True`

**AutoFixer.fix()** — добавить после строки 905 (после WORD_SPAM):
```python
elif v.rule_id == "PLACEHOLDER_VALUES":
    for col, val in list(fixed.items()):
        if col in SKIP_COLUMNS_FOR_COMPLETENESS:
            continue
        val_str = str(val).strip().lower()
        for ph in PLACEHOLDER_VALUES:
            if val_str == ph.lower():
                fixed[col] = ""
                applied.append(f"Очищен плейсхолдер: {col}='{val_str}'")
                break
```

**_check_placeholders()** — добавить проверку числовых полей после строки 723:
```python
NUMERIC_FIELDS = {"Вес", "Высота", "Ширина", "Длина", "Объём", "Количество"}
for col, val in enriched.items():
    if any(nf.lower() in col.lower() for nf in NUMERIC_FIELDS):
        val_str = str(val).strip()
        if val_str and not re.search(r'\d', val_str):
            violations.append(RuleViolation(...))
```

### Шаг 7: run_enrichment() интеграция — `enrichment_pipeline.py` строки 536-664

Новая сигнатура:
```python
def run_enrichment(input_dir, output_dir, file_filter, dry_run, limit,
                   resume=False, save_every=5) -> Dict[str, Any]:
```

Порядок:
1. Init KeywordMatcher, CheckpointManager(output_dir/.checkpoints), AuditTracker
2. Init FileRAG, NotebookLMSource (graceful — не блокировать если недоступен)
3. Для каждого файла → для каждого товара:
   - check_pause_stop() → pause/stop/run
   - Skip если resume и уже обработан
   - audit.record_before()
   - enrich_product(..., keyword_matcher=km)
   - audit.record_after()
   - checkpoint.save()
   - Apply enriched to DataFrame
   - Каждые save_every: промежуточное save_enriched_xlsx()
4. km.save_category_keywords(output_dir / "keywords")
5. audit.write_report() + audit.write_audit()

### Шаг 8: CLI — `enrichment_pipeline.py` строки 671-704

Добавить аргументы:
- `--resume`: resume=True
- `--save-every N`: save_every=N (default 5)

---

## Принципы
1. Оригиналы НЕ трогаем — только копии в output/
2. Структура WB XLSX 1:1 — row1-4 не трогаем
3. Checkpoint каждый товар — обрыв не теряет прогресс
4. Graceful degradation — отсутствие NotebookLM/файлов не блокирует batch
5. Полный аудит — "было → стало" по каждому полю

## Exploration Notes (verified 01.03.2026)

### enrichment_pipeline.py — verified line numbers
- Line 47: `SEO_COLUMNS` — insert new code AFTER this line
- Lines 207-217: `NotebookLMSource.ask()` — no retry logic, catches exceptions
- Lines 286-346: `ENRICHMENT_SYSTEM_PROMPT` — **NB: lines 338-344 already have a ХАРАКТЕРИСТИКИ section** → ENHANCE it (replace lines 338-344 with stronger version)
- Lines 358-364: `enrich_product()` signature
- Lines 536-542: `run_enrichment()` signature
- Lines 575-582: Hard NotebookLM check (`return {}`)
- Lines 671-704: CLI/main()
- Existing imports: json, shutil, time, Path, typing, httpx, pandas, config — need to add `zipfile`, `logging`, `re` (for KeywordMatcher)

### wb_qa_multilevel.py — verified line numbers
- Lines 206-213: `PLACEHOLDER_VALUES` constant
- Lines 216-220: `SKIP_COLUMNS_FOR_COMPLETENESS` set
- Lines 245-253: `RuleViolation` dataclass
- Lines 699-724: `_check_placeholders()` — auto_fixable=False at line 721 ✓
- Lines 740-922: `AutoFixer` class, `fix()` method
- Lines 886-905: WORD_SPAM handling — insert PLACEHOLDER_VALUES handling after line 905 ✓
- Lines 233-237: `NUMERIC_UNITS` regex already exists
- Lines 612-659: `_check_numeric_match()` exists (separate from placeholders)

### Input files status
- **WB 300K ZIP**: EXISTS (33MB) ✓
- **Ozon 10K XLSX**: EXISTS (1.2MB) ✓
- **XLSX product dir**: NOT FOUND at `~/Downloads/01.03.2026_09.40_Все характеристики по предметам/` — code must handle gracefully (it already does via INPUT_DIR validation)

## Верификация
```bash
cd /Users/Dmitrij/Documents/Orchestrator/агенты/wb_content_factory

# 1. Существующие тесты не сломаны
/Users/Dmitrij/Documents/Orchestrator/агенты/.venv/bin/python3 -m pytest tests/ -v

# 2. KeywordMatcher изолированно
python3 -c "from src.enrichment_pipeline import KeywordMatcher; km = KeywordMatcher(); print(km.get_keywords('Протеин', top_n=5))"

# 3. Dry-run одного товара
PYTHONUNBUFFERED=1 python3 -m src.enrichment_pipeline --dry-run --file Креатин

# 4. Полный прогон
PYTHONUNBUFFERED=1 nohup python3 -m src.enrichment_pipeline --all --resume > enrichment.log 2>&1 &

# 5. Мониторинг: tail -f enrichment.log | touch PAUSE | touch STOP
```
