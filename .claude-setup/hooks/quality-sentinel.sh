#!/bin/bash
# Quality Sentinel Hook (Stop Event)
# Analyzes changed files for risky patterns and runs tests

# Get changed files
CHANGED=$(git diff --name-only 2>/dev/null)
if [ -z "$CHANGED" ]; then
    exit 0
fi

WARNINGS=""

# Check for risky patterns in Python files
PY_FILES=$(echo "$CHANGED" | grep '\.py$')
if [ -n "$PY_FILES" ]; then
    for f in $PY_FILES; do
        [ ! -f "$f" ] && continue

        # try/except without logging
        if grep -qP 'except.*:\s*$' "$f" 2>/dev/null; then
            WARNINGS="$WARNINGS\n  [RISK] $f: bare except without logging — add Sentry.captureException()?"
        fi

        # Raw SQL strings
        if grep -qP '(execute|raw)\s*\(\s*f"|\.format\(' "$f" 2>/dev/null; then
            WARNINGS="$WARNINGS\n  [RISK] $f: possible raw SQL — use parameterized queries"
        fi

        # async without await
        if grep -qP 'async\s+def' "$f" 2>/dev/null; then
            if ! grep -qP 'await\s' "$f" 2>/dev/null; then
                WARNINGS="$WARNINGS\n  [RISK] $f: async def without await — synchronous call?"
            fi
        fi

        # os.environ direct access
        if grep -qP 'os\.environ\[' "$f" 2>/dev/null; then
            WARNINGS="$WARNINGS\n  [INFO] $f: direct os.environ access — use config/settings instead?"
        fi
    done
fi

if [ -n "$WARNINGS" ]; then
    echo "Quality Sentinel detected patterns to review:"
    echo -e "$WARNINGS"
fi
