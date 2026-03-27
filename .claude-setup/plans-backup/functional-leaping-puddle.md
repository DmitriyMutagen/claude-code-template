# Plan: Neo4j Schema Builder + Milestones 2 & 3

## Context
WB Content Factory needs:
1. **Neo4j enrichment** — add Yandex Market product parsing (132 products from XLSX) and Ozon keyword semantics (10K search queries from queries_report XLSX) to the knowledge graph
2. **Milestones 2 & 3** from `prompt_for_code_agent_v3.md` — Matrix Forge (qa_reviewer, nano_banana_api) and Ad Optimizer (wb_ad_optimizer, bid engine, graph sync)

## Part 1: Neo4j Schema Builder (PARTIALLY DONE)

### Already completed:
- Updated docstring and added `OZON_QUERIES_XLSX_PATH` constant
- Rewrote `read_yandex_products()` using pandas (handles complex XLSX header structure: row 0 = groups, row 1 = column names, row 2 = descriptions, row 3+ = data)
- Added `read_ozon_keywords()` — reads 10K Ozon search queries via calamine engine, returns list of dicts with text, popularity, trend_28d/7d, cart metrics, order metrics, source="Ozon"

### Remaining in neo4j_schema_builder.py:

**File:** `/Users/Dmitrij/Documents/Orchestrator/агенты/wb_content_factory/src/neo4j_schema_builder.py`

1. **Add `upsert_ozon_keyword()` to `Neo4jGraphBuilder`** — MERGE Keyword node with Ozon metrics (popularity, trends, conversions), link to Marketplace "Ozon" via `[:FOUND_ON]`
2. **Update `upsert_product()`** — add `barcode` and `yandex_market_id` fields for Yandex products
3. **Update `build_graph()`** — add step [4/4] for Ozon keywords ingestion
4. **Update CLI `main()`** — add `--keywords` flag for keywords-only mode
5. **Update `get_stats()`** — include Intention node count

## Part 2: Milestone 2 — Matrix Forge

### 2a. `qa_reviewer.py` (NEW)
- Validates Dify/LLM output before saving
- Checks: SEO-Title <= 60 chars, no keyword spam, all required keys present, no hallucinations/stop-words
- Reject → re-send to Dify with error context
- Uses LocalLLM (Qwen) config

### 2b. `nano_banana_api.py` (NEW)
- Connector for image generation API
- Accepts Rich-TZ (8 blocks: background, angle, audience pain points)
- Returns image URLs → saves to Neo4j linked to card version

### 2c. Update `batch_runner.py`
- Wire through `dify_pipeline.py` for orchestration
- Product → Dify → segments → per-segment SEO-Title + Description + Rich-TZ
- Save generation results as Neo4j nodes linked to Product

## Part 3: Milestone 3 — Ad Optimizer

### 3a. `wb_ad_optimizer.py` (NEW)
- Daemon/scheduler for automatic bid management
- Reads WB API metrics (CTR, CPO, orders)
- Business rules: separate campaigns (Shelf vs Search), CPO > 300₽ → minimum bid, bid steps of 50₽ in 200-250₽ range

### 3b. Google Sheets integration for Unit Economics
- Read target CPO from Sheets, write actual CPO back
- ROI negative → alert in logs/sheet

### 3c. Neo4j Graph Sync
- Add conversion weights to Keyword nodes and TARGETS relationships
- High-converting keywords → higher weight → priority in future Title generation

## Verification
1. `python3 -m src.neo4j_schema_builder --test` — verify Yandex parsing + Ozon keywords (1 product, limited keywords)
2. `python3 -m src.neo4j_schema_builder --keywords` — verify 10K keyword import
3. `python3 -c "from src.qa_reviewer import QAReviewer; print('OK')"` — import check
4. `python3 -c "from src.wb_ad_optimizer import WBAdOptimizer; print('OK')"` — import check
5. Run existing tests: `python3 -m pytest tests/test_pipeline.py`
