# MarketAI — Comprehensive Audit + QC Module Plan

## Context
Resuming MarketAI QA session. Multiple issues found in previous session:
- Inbox sort order bug fixed (new reviews now surfaced first)
- Anonymous name filter fixed in engine.py
- Ozon has 3,373 unprocessed reviews vs 1,098 in DB — sync gap
- 21 new Ozon questions, 359 unread chats pending
- QC module spec written at docs/plans/2026-03-22-quality-control-module.md
- User requested: stop Paperclip at 127.0.0.1:3100, then full service audit

## Immediate Actions (in order)

### 1. Stop Paperclip Process
- `curl -X POST http://127.0.0.1:3100/api/shutdown` or kill process on port 3100
- `lsof -ti:3100 | xargs kill -9`

### 2. Ensure Backend Running
- Start backend on port 8001 if not running:
  `DATABASE_URL=postgresql+asyncpg://marketai:marketai@localhost:5432/marketai JWT_SECRET_KEY=dev-secret-key-for-local-testing-only-32chars uvicorn src.api.main:app --reload --port 8001`
- Verify: `curl http://localhost:8001/health`

### 3. MCP-Based Data Audit (science-api + marketplace APIs)
- Verify all 18 MCP servers responding (health checks)
- Check marketai-db stats: reviews, products, shops, sync_runs
- science-api: test PubMed/OpenFDA integration for actual product names (протеин, БАД)
- marketai_review_stats enum bug: verify "responded" status handling

### 4. Sync Gap Investigation
- Read src/connectors/ozon/connector.py and src/services/sync_engine.py
- Find why sync_runs table is empty (never records runs)
- Fix pagination/limit bug causing 3,373 → 1,098 discrepancy
- Key file: `src/services/sync_engine.py`

### 5. Browser QA (frontend http://localhost:5173)
- Reviews page: confirm sort order fix works, check AI response quality
- Questions page: 21 new Ozon questions visible?
- Chats page: 359 unread counter, draft quality
- Check "Покупатель" no longer appears in AI responses

### 6. QC Module Implementation (Sprint 1 — Core)
Spec at: `marketai/docs/plans/2026-03-22-quality-control-module.md`

Files to create:
- `src/ai/qc_classifier.py` — severity 1-5 classification with keyword triggers
- `src/services/qc_service.py` — batch analysis, pattern detection
- `alembic/versions/011_qc_tables.py` — product_qc_scores, qc_incidents, qc_patterns tables
- `src/api/routers/quality_control.py` — QC API endpoints
- `frontend-react/src/pages/QualityControl.tsx` — QC dashboard

Key triggers to detect:
- Health: "камни", "сухое молоко", "заболел", "отравился", "в больницу"
- Fraud: "не протеин", "не соответствует", "подделка", "другой товар"
- Packaging: "грамм не соответствует", "вес меньше", "вскрытый"

Science integration (via science-api MCP):
- OpenFDA CAERS for adverse event lookup
- PubMed for ingredient safety research
- RF compliance for Russian regulatory context

## Verification
1. Backend health: `curl http://localhost:8001/health`
2. QC API: `curl -H "Authorization: Bearer <token>" http://localhost:8001/api/v1/quality-control/stats`
3. MCP: `marketai_db_health` + `marketai_review_stats`
4. Browser: localhost:5173/quality-control renders dashboard
5. science-api test: `science_fda_safety` on "protein powder"
