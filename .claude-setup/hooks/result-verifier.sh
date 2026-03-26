#!/bin/bash
# Result Verifier — BLOCKING Stop Hook for Claude Code
# Prevents "done" without actual verification of changes.
# Reads JSON from stdin (Claude Code hook format).
# Exit 0 = allow stop. Print JSON with "block" decision = block stop.

set -euo pipefail

# --- Safety valve: prevent infinite loop ---
# Use parent PID as session identifier (stable across hook invocations in one session)
COUNTER_FILE="/tmp/claude-result-verifier-count-${PPID}"

BLOCK_COUNT=0
if [[ -f "$COUNTER_FILE" ]]; then
    BLOCK_COUNT=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)
    # Validate it's a number
    if ! [[ "$BLOCK_COUNT" =~ ^[0-9]+$ ]]; then
        BLOCK_COUNT=0
    fi
fi

# If blocked 3+ times already, allow stop to prevent infinite loop
if [[ "$BLOCK_COUNT" -ge 3 ]]; then
    rm -f "$COUNTER_FILE" 2>/dev/null
    exit 0
fi

# --- Helper: increment block counter and output block JSON ---
block() {
    local reason="$1"
    BLOCK_COUNT=$((BLOCK_COUNT + 1))
    echo "$BLOCK_COUNT" > "$COUNTER_FILE"
    echo "{\"decision\": \"block\", \"reason\": \"$reason\"}"
    exit 0
}

# --- Detect changed files via git ---
# Try both staged and unstaged changes; handle non-git directories gracefully
CHANGED=""
if command -v git &>/dev/null; then
    CHANGED=$(git diff --name-only HEAD 2>/dev/null || true)
    STAGED=$(git diff --cached --name-only 2>/dev/null || true)
    if [[ -n "$STAGED" ]]; then
        CHANGED=$(printf '%s\n%s' "$CHANGED" "$STAGED" | sort -u)
    fi
    # Also check untracked files that were likely created this session
    UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null || true)
    if [[ -n "$UNTRACKED" ]]; then
        CHANGED=$(printf '%s\n%s' "$CHANGED" "$UNTRACKED" | sort -u)
    fi
fi

# Trim empty lines
CHANGED=$(echo "$CHANGED" | sed '/^$/d')

# --- No changes at all: read-only session, allow stop ---
if [[ -z "$CHANGED" ]]; then
    rm -f "$COUNTER_FILE" 2>/dev/null
    exit 0
fi

# --- Only .md files changed: allow stop ---
NON_MD=$(echo "$CHANGED" | grep -v '\.md$' || true)
if [[ -z "$NON_MD" ]]; then
    rm -f "$COUNTER_FILE" 2>/dev/null
    exit 0
fi

# --- Classify what changed ---
HAS_CODE=false
HAS_FRONTEND=false
HAS_API=false
HAS_DB=false

CODE_FILES=$(echo "$CHANGED" | grep -E '\.(py|ts|tsx|js|jsx)$' || true)
FRONTEND_FILES=$(echo "$CHANGED" | grep -E '\.(tsx|jsx|html|css|scss|svelte|vue)$' || true)
API_FILES=$(echo "$CHANGED" | grep -E '(api/|routes/|router|endpoint|handler).*\.(py|ts|js)$' || true)
DB_FILES=$(echo "$CHANGED" | grep -E '(models/|migrations/|alembic|schema|prisma)' || true)

[[ -n "$CODE_FILES" ]] && HAS_CODE=true
[[ -n "$FRONTEND_FILES" ]] && HAS_FRONTEND=true
[[ -n "$API_FILES" ]] && HAS_API=true
[[ -n "$DB_FILES" ]] && HAS_DB=true

# If no code files changed (only configs, yml, json, etc.) — allow stop
if [[ "$HAS_CODE" == false ]]; then
    rm -f "$COUNTER_FILE" 2>/dev/null
    exit 0
fi

# --- Check for verification signals ---
# We look for recent evidence that tests or verification were performed.
# Check bash history / recent commands in /tmp for signs of testing.

VERIFIED=false

# 1. Check if pytest/vitest/jest/playwright ran recently (last 5 min)
# Look for test result files
RECENT_TEST_RESULTS=$(find /tmp -maxdepth 2 -name '*.xml' -newer /tmp/.claude-session-start 2>/dev/null | head -1 || true)
if [[ -n "$RECENT_TEST_RESULTS" ]]; then
    VERIFIED=true
fi

# 2. Check for recent screenshots (E2E / frontend verification)
if [[ "$HAS_FRONTEND" == true ]]; then
    RECENT_SCREENSHOTS=$(find /tmp -maxdepth 3 -name '*.png' -mmin -10 2>/dev/null | head -1 || true)
    SCREENSHOTS_DIR=$(find . -maxdepth 3 -type d -name 'screenshots' 2>/dev/null | head -1 || true)
    if [[ -n "$SCREENSHOTS_DIR" ]]; then
        RECENT_SCREENSHOTS=$(find "$SCREENSHOTS_DIR" -name '*.png' -mmin -10 2>/dev/null | head -1 || true)
    fi
    if [[ -n "$RECENT_SCREENSHOTS" ]]; then
        VERIFIED=true
    fi
fi

# 3. Check shell history for test/verification commands (last 20 commands)
HIST_FILE="${HISTFILE:-$HOME/.zsh_history}"
if [[ -f "$HIST_FILE" ]]; then
    RECENT_CMDS=$(tail -30 "$HIST_FILE" 2>/dev/null || true)
    if echo "$RECENT_CMDS" | grep -qiE '(pytest|vitest|jest|playwright|npm test|bun test|curl|httpx|ruff check|tsc --noEmit|npm run build|pnpm build)'; then
        VERIFIED=true
    fi
fi

# 4. Check Claude's own observations directory for test evidence
# Claude Code creates temp files; check for recent test-related ones
if find /tmp -maxdepth 1 -name 'claude-*' -mmin -5 2>/dev/null | head -1 | grep -q .; then
    # If Claude ran commands recently, check for test patterns in recent /tmp files
    TEST_EVIDENCE=$(find /tmp -maxdepth 1 \( -name '*test*' -o -name '*result*' -o -name '*junit*' \) -mmin -10 2>/dev/null | head -1 || true)
    if [[ -n "$TEST_EVIDENCE" ]]; then
        VERIFIED=true
    fi
fi

# 5. Check if a .test-ran or .verified marker exists (other hooks/scripts can set this)
if [[ -f /tmp/.claude-tests-passed ]] && [[ $(find /tmp/.claude-tests-passed -mmin -30 2>/dev/null) ]]; then
    VERIFIED=true
fi

# --- Decision ---

if [[ "$VERIFIED" == true ]]; then
    rm -f "$COUNTER_FILE" 2>/dev/null
    exit 0
fi

# Not verified — block with specific reason based on what changed

if [[ "$HAS_FRONTEND" == true ]]; then
    block "Frontend-файлы изменены (${FRONTEND_FILES%%$'\\n'*}...). Сделай скриншот или E2E-тест перед завершением."
fi

if [[ "$HAS_API" == true ]]; then
    block "API-файлы изменены. Проверь эндпоинты: запусти тесты или curl-запрос."
fi

if [[ "$HAS_DB" == true ]]; then
    block "Модели/миграции изменены. Проверь: alembic heads, тесты на модели, миграция применяется."
fi

# Generic code change without verification
block "Код изменён без верификации. Запусти тесты, сделай E2E-проверку или проверь результат вручную."
