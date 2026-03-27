# MarketAI — 100% Production Readiness Plan

## Context
Service runs locally (localhost:5173 frontend, localhost:8000 backend). Not public yet — internal use, debugging, polishing. Goal: 100% production-ready code even though deployed locally. All bugs must be fixed. All features working.

Previous session completed: Batch 1-2, 6 AI engine fixes, Humanizer, Quality Gate, 7 audit reports, 731 tests.

## Parallel Agent Execution Plan

### Agent Group 1: Backend Fixes (3 agents)

**Agent 1: Cron scheduler + auto-sync + auto-reply**
- Create `src/tasks/scheduler.py` — ARQ/APScheduler cron setup
- Every 60 min: sync all marketplaces (Ozon + WB + YM)
- Every 5 min: send approved responses
- Every 30 min: REFRESH MATERIALIZED VIEW CONCURRENTLY mv_shop_daily_stats
- Health check cron (verify sync not stalled)
- Files: `src/tasks/scheduler.py`, `src/api/main.py` (startup event)

**Agent 2: Fix remaining backend bugs**
- YM: strip PubMed URLs before sending responses (73 send_errors)
- WB connector: write external_order_id (nm_id) during sync for product linking
- ErrorCollector: fix DATABASE_URL (b2b_intelligence → use app's session)
- Fix 2 flaky tests (rate limiter in test_load.py, test_routers_unit.py)
- CSP header setup in main.py SecurityMiddleware
- Files: `src/connectors/yandex/review_client.py`, `src/connectors/wb/sync.py`, `src/middleware/error_collector.py`, `src/api/main.py`

**Agent 3: RAG store completion + Humanizer for chats/questions**
- Complete RAG indexing (354 products, with 2sec delay between Gemini calls)
- Add Humanizer to `generate_chat_response()` and `generate_question_response()` in engine.py
- Verify RAG search returns real chunks after indexing
- Files: `src/ai/engine.py`, `scripts/reindex_products.py` (create)

### Agent Group 2: Frontend Fixes (2 agents)

**Agent 4: Admin Monitoring + QC page**
- Fix Admin Monitoring page (broken graphs, missing data)
- Embed Sentry error data via API (use /admin/errors endpoint)
- Add QC section: show quality_score + criteria per response
- Show quality_issues and suggestions inline
- Files: `frontend-react/src/pages/AdminMonitoring.tsx`, `frontend-react/src/pages/QualityControl.tsx` (new)

**Agent 5: Analytics + Store Settings upgrade**
- Analytics: cross-cabinet dashboard with recommendations
- Store Settings: cross-sell recommendation block with articul picker
- Reviews: show quality_score badge per response
- Fix rate limiter for E2E tests (shared token in globalSetup)
- Files: `frontend-react/src/pages/Analytics.tsx`, `frontend-react/src/pages/StoreSettings.tsx`, `frontend-react/src/pages/Reviews.tsx`

### Agent Group 3: Data & Integration (1 agent)

**Agent 6: Full marketplace re-sync + product linking**
- Start backend, login, trigger sync/all
- After sync: run WB backfill + YM backfill
- Verify product linking percentages improved
- Check Sentry for new errors during sync
- Report final data counts via MCP marketplace tools
- Files: API calls only (no code changes)

## Hooks (already configured)
1. PostToolUse:Edit .py → ruff format + ruff check --fix
2. PostToolUse:Edit .tsx → tsc --noEmit
3. PreToolUse:Bash (git commit) → sg scan src/ blocks on errors

## Verification
1. `pytest tests/ -k "not test_ozon_chat"` → 730+ passed, 0 failed
2. `cd frontend-react && npm run build` → 0 errors
3. `sg scan src/` → 0 errors
4. Sentry: 0 new unresolved issues
5. All MCP marketplace counts match DB
6. RAG search returns chunks for "протеин"
7. Quality Gate scores 8+ on sample reviews
8. Browser: all pages load, no console errors
