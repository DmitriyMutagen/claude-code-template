---
name: qa-verifier
description: Full QA verification chain — checks end result as real user. Scores quality 1-10, blocks deploy if below 7. Use after any feature completion.
---

# /qa-verify — End Result Quality Assurance

## When to Use
- After completing any feature (auto-triggered by result-verifier hook)
- Before deploy
- When user says "проверь", "протестируй", "верифицируй"

## QA Chain: 4 Steps

### Step 1: Data Correctness Check
- Query real data via MCP (marketplace, DB, API)
- Compare what's in DB vs what's displayed on frontend
- Check: names, numbers, dates, prices match source
- Score: 0-10

### Step 2: E2E Browser Test
- Open in Playwright (use playwright MCP or Bash)
- Navigate key pages
- Take screenshots
- Check for: 500 errors, 404, empty pages, broken images
- Score: 0-10

### Step 3: Business Logic Verification
- Does the feature do what was specified?
- Are edge cases handled? (empty data, large dataset, special chars)
- Does error handling work? (show message, not crash)
- Score: 0-10

### Step 4: User Experience Check
- Is it intuitive? (would Дмитрий understand without explanation?)
- Are labels in correct language (Russian)?
- Is loading fast? (<3 seconds)
- Score: 0-10

## Final Score
Average of 4 scores. Format:

```
QA Score: 8.5/10

  Данные: 9/10 (все совпадают с БД)
  E2E: 8/10 (1 мелкий UI баг)
  Логика: 9/10 (edge cases обработаны)
  UX: 8/10 (загрузка 2.1с)

  Вердикт: READY FOR DEPLOY
  Баги: 1 minor (описание)
```

If score < 7: NOT READY — list what to fix
If score 7-8: READY with notes
If score 9-10: EXCELLENT

## Integration
Called by result-verifier hook when code changes detected.
Results saved to ~/.claude/memory/decay-7d/qa-YYYY-MM-DD-N.md
