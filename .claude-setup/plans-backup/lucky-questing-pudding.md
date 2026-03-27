# Plan: Chat AI Upgrade + Dashboard/Analytics Fix + E2E Audit

## Context
Previous plan (Phases 1-3) already DONE: AI generation bugs fixed, prompts fixed, frontend enriched.
Now two new blocks:
1. **Chats**: Gemini Flash too weak — need smarter model + UX improvements
2. **Dashboard/Analytics**: Same numbers for all shops — data filtering broken

---

## Block A: Chat AI — Better Model + UX

### A1. Per-task model routing in engine.py
- **File**: `src/config.py` — add `CHAT_MODEL` setting (default: `anthropic/claude-sonnet-4-20250514`)
- **File**: `src/ai/engine.py` — add `model_override` param to `_call_gemini()`, `generate_chat_response()`, `generate_question_response()`
- When `model_override` is set, call that specific provider directly instead of fallback chain
- **File**: `.env` — add `CHAT_MODEL=anthropic/claude-sonnet-4-20250514`
- Keep Gemini Flash as default for reviews (fast + cheap), use Claude for chats/questions (smart)

### A2. Chat UX improvements (Chats.tsx)
- Quick reply templates: 5-7 canned responses for common БАД questions (stored in constants, selectable via chips)
- Product info sidebar: show product name, composition, dosage when chat has linked product
- Keyboard shortcut: Ctrl+Enter → generate AI draft
- Regenerate button in AI draft panel
- Show response time since last buyer message

### A3. Prompts ✅ DONE
- Already fixed to prohibit "информация не указана"

---

## Block B: Dashboard/Analytics Data Fix

### B1. Audit & fix dashboard backend
- **File**: `src/api/routers/dashboard.py` — check all stat queries for `shop_id` WHERE clause
- Verify: total_reviews, unanswered, ai_generated, published all respect shop_id filter
- Fix "Все магазины" (all) vs specific shop aggregation

### B2. Audit & fix analytics backend
- **File**: `src/api/routers/analytics.py` — same shop_id filtering
- Check time-series, rating distribution, sentiment data for shop isolation

### B3. Audit frontend shop filter propagation
- **File**: `frontend-react/src/pages/Dashboard.tsx` — verify shop_id sent in API calls
- **File**: `frontend-react/src/pages/Analytics.tsx` — same check

### B4. Check marketplace sync data integrity
- **Files**: `src/connectors/ozon/`, `src/services/sync_engine.py`
- Verify synced data has correct shop_id associations

---

## Block C: E2E Tests & Audit
- Run full `pytest tests/` including e2e_frontend_test.py
- Add test cases for shop switching on dashboard
- Fix any pre-existing test failures (test_ozon_chat.py event loop issues)

---

## Execution: Parallel Agents
- Agent 1 (coder): Block A1 — model routing in engine.py + config.py
- Agent 2 (coder): Block A2 — Chat UX improvements
- Agent 3 (Explore + coder): Block B1-B3 — Dashboard/Analytics audit + fix
- Agent 4 (tester): Block C — E2E tests

## Verification
1. `pytest tests/` — all tests pass
2. E2E tests pass with running servers
3. Dashboard: switch shops → numbers change
4. Chat AI: generates expert responses with Claude, PubMed refs, no "нет информации"
