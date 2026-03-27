# Plan: Production-Grade Connectors for All Remaining Data Sources

## Status: READY FOR APPROVAL

## Context
- DB: SQLite at `data/bionovacia.db`, currently 4930 ingredients, 11 categories
- Existing connectors: dsld_client, openfoodfacts_client, fsa_client, moysklad_client, external_apis (stub)
- Existing harvest pattern: sync `sqlite3` directly, `httpx.AsyncClient`, `asyncio.run(main())`
- UPSERT by `name_en.lower()` — check existing set, skip duplicates
- Category classification via CATEGORY_KEYWORDS dict + EN_TO_RU mapping for Russian names
- No `beautifulsoup4` in deps yet — need to add for HTML parsing (iherb, grls, examine, consumerlab, eu_novel_food)

## Architecture

All 8 connectors follow the same pattern as existing code:
```
src/connectors/{name}_client.py   — async client class with tenacity retry
scripts/harvest_{name}.py         — standalone script, sync sqlite3 UPSERT
```

Each connector class:
- `__init__`: base_url, headers, httpx.AsyncClient (reused within session)
- Methods decorated with `@retry(stop=stop_after_attempt(3), wait=wait_exponential(...))`
- Rate limiting via `asyncio.Semaphore` + `asyncio.sleep()`
- Returns normalized dicts ready for DB insert
- Sentry breadcrumbs + exception capture
- Fallback responses on failure

Each harvest script:
- `DB_PATH = Path(__file__).parent.parent / "data" / "bionovacia.db"`
- Reuses `CATEGORY_KEYWORDS` and `EN_TO_RU` from harvest_dsld.py (extract to shared util)
- `insert_ingredients()` function with UPSERT logic
- Progress logging, error counting
- Standalone runnable with `DATABASE_URL` env or default path

## New dependency needed
- `beautifulsoup4>=4.12.0` — for HTML parsing (iherb, grls, examine, consumerlab, eu_novel_food)
- `lxml>=5.0.0` — fast HTML parser backend for bs4

## Shared Utility: `scripts/_shared.py`
Extract from `harvest_dsld.py`:
- `CATEGORY_KEYWORDS` dict
- `EN_TO_RU` dict
- `classify_ingredient(name: str) -> str`
- `get_ru_name(en_name: str) -> str`
- `make_uuid() -> str`
- `insert_ingredients(conn, ingredients) -> int` — generic UPSERT
- `get_db_path() -> Path`

## Connectors Detail

### 1. iherb_client.py — iHerb Product Scraper
- **Method**: httpx scraping with realistic headers, User-Agent rotation
- **Rate limit**: 1 req/2s (Semaphore + sleep)
- **Search**: `https://www.iherb.com/search?kw={query}&p={page}`
- **Product page**: parse supplement facts table from HTML
- **Extract**: product name, brand, ingredients list with amounts, serving size, price, rating
- **Risk**: anti-bot protection — mitigate with realistic headers, random delays (2-5s)
- **Fallback**: if blocked (403/captcha), log and skip — we still get data from other pages
- **Estimated yield**: 500-2000 unique ingredients from supplement products

### 2. grls_client.py — GRLS Russian BAD Registry
- **Method**: httpx + BeautifulSoup scraping of `https://grls.rosminzdrav.ru/`
- **Rate limit**: 1 req/3s (government server, be polite)
- **Search**: POST form-based search for "БАД" products
- **Extract**: product name, manufacturer, composition text, registration number, date
- **Parse composition**: regex extraction of ingredient names from free-text composition field
- **Unique value**: ONLY source of officially registered Russian BADs
- **Estimated yield**: 200-500 unique ingredients from composition parsing

### 3. examine_client.py — Examine.com Scraper
- **Method**: httpx + BeautifulSoup
- **Rate limit**: 1 req/2s
- **Index**: `https://examine.com/supplements/` — list of 400+ supplements
- **Detail page**: `/supplements/{slug}/` — summary, research grades, dosage, interactions
- **Extract**: supplement name, summary, research grade (A-F), recommended dosage, human study count, key effects
- **Unique value**: GOLD STANDARD research evidence grades
- **Estimated yield**: 400+ supplements with research quality data
- **Maps to**: description, effects, recommended_dose_mg, study-backed evidence

### 4. efsa_client.py — EFSA European Food Safety Authority
- **Method**: httpx REST API (JSON responses)
- **API base**: `https://open.efsa.europa.eu/api/`
- **Endpoints**: food catalog, nutrient data, health claims
- **Rate limit**: 1 req/1s (public API)
- **Extract**: approved health claims per ingredient, novel food status, safe intake levels
- **Maps to**: efsa_status, daily_limit_mg, effects (from health claims)
- **Estimated yield**: 200-400 ingredients with EU regulatory data

### 5. wb_supplements_client.py — Wildberries BAD Products
- **Method**: WB API v2 (GET /content/v2/get/cards/list)
- **Auth**: WB API token from env
- **Filter**: BAD/sport nutrition categories
- **Extract**: product name, brand, composition from description, price, rating
- **Parse composition**: regex extraction from product descriptions
- **Rate limit**: WB API limits (respect X-RateLimit headers)
- **Estimated yield**: 100-300 unique ingredients from marketplace products

### 6. ozon_supplements_client.py — Ozon BAD Products
- **Method**: Ozon Seller API
- **Auth**: Client ID 2003894 + API key from env
- **Endpoints**: POST /v2/product/list, POST /v3/product/info/description
- **Filter**: supplement/BAD categories
- **Extract**: product name, brand, composition parsing from descriptions
- **Rate limit**: Ozon API limits
- **Estimated yield**: 100-300 unique ingredients

### 7. eu_novel_food_client.py — EU Novel Food Catalogue
- **Method**: httpx + BeautifulSoup scraping
- **URL**: `https://webgate.ec.europa.eu/fip/novel_food_catalogue/`
- **Extract**: ingredient name, authorization status, conditions of use, max levels
- **Rate limit**: 1 req/2s
- **Maps to**: efsa_status (authorized/not), daily_limit_mg
- **Estimated yield**: 100-200 novel food ingredients

### 8. consumerlab_client.py — ConsumerLab Scraper
- **Method**: httpx + BeautifulSoup (public pages only)
- **URL**: `https://www.consumerlab.com/`
- **Constraint**: Most content behind paywall — only public summaries
- **Extract**: product categories, publicly available test summaries
- **Rate limit**: 1 req/3s (respect paywall)
- **Estimated yield**: 50-100 supplement quality data points

## Files to Create (16 total)

### Shared utility
1. `scripts/_shared.py` — extracted shared code from harvest_dsld.py

### Connectors (8 files)
2. `src/connectors/iherb_client.py`
3. `src/connectors/grls_client.py`
4. `src/connectors/examine_client.py`
5. `src/connectors/efsa_client.py`
6. `src/connectors/wb_supplements_client.py`
7. `src/connectors/ozon_supplements_client.py`
8. `src/connectors/eu_novel_food_client.py`
9. `src/connectors/consumerlab_client.py`

### Harvest scripts (8 files)
10. `scripts/harvest_iherb.py`
11. `scripts/harvest_grls.py`
12. `scripts/harvest_examine.py`
13. `scripts/harvest_efsa.py`
14. `scripts/harvest_wb_supplements.py`
15. `scripts/harvest_ozon_supplements.py`
16. `scripts/harvest_eu_novel_food.py`
17. `scripts/harvest_consumerlab.py`

### Modified files
18. `pyproject.toml` — add beautifulsoup4, lxml
19. `scripts/harvest_dsld.py` — import from _shared instead of inline dicts
20. `scripts/harvest_all.py` — add new scripts to pipeline
21. `src/connectors/__init__.py` — register new connectors

## Implementation Order
1. `scripts/_shared.py` — extract shared utilities first
2. iherb (most data, highest priority)
3. grls (unique Russian registry data)
4. examine (research evidence grades)
5. efsa (EU regulatory API)
6. wb_supplements + ozon_supplements (marketplace data, similar pattern)
7. eu_novel_food
8. consumerlab (lowest priority, paywall limited)
9. Update harvest_all.py, pyproject.toml, __init__.py

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| iHerb anti-bot blocks | No iHerb data | Realistic headers, random delays, graceful fallback |
| GRLS website changes | No Russian registry data | Parse defensively, log unparseable pages |
| Examine.com structure change | No research grades | Fallback to basic name extraction |
| EFSA API rate limiting | Slow harvest | Respect rate limits, resume from checkpoint |
| WB/Ozon API auth issues | No marketplace data | Check tokens before run, skip gracefully |

## Definition of Done
- [ ] All 8 connectors created with async httpx + tenacity retry
- [ ] All 8 harvest scripts runnable standalone
- [ ] _shared.py extracted, harvest_dsld.py refactored to use it
- [ ] harvest_all.py updated with new scripts
- [ ] pyproject.toml updated with beautifulsoup4 + lxml
- [ ] At least iherb + grls + examine harvests tested (run and verify data)
- [ ] No ruff lint errors in new files
- [ ] Each connector handles errors gracefully (skip failed items, continue)
