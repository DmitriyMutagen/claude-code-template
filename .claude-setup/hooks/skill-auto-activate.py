#!/usr/bin/env python3
"""
Skills Auto-Activation Hook (UserPromptSubmit)
Analyzes user prompt keywords and injects skill activation reminders.
For large tasks — injects MANDATORY instructions, not just reminders.
Without this, skills are ignored in ~90% of cases.
"""
import sys
import os
import json
import re

# Read prompt from environment or stdin
prompt = os.environ.get("CLAUDE_USER_PROMPT", "")
if not prompt:
    try:
        input_data = json.loads(sys.stdin.read())
        prompt = input_data.get("prompt", input_data.get("content", ""))
    except Exception:
        prompt = ""

prompt_lower = prompt.lower()

# ============================================================
# TIER 1: MANDATORY INSTRUCTIONS (large tasks — forced workflow)
# These output as ORDERS, not suggestions
# ============================================================

MANDATORY_PATTERNS = {
    # New feature / module / system
    r"(новая?\s+фич|new\s+feature|новый\s+модул|добавь\s+систем|создай\s+модул|сделай\s+систем|реализуй|implement\s+feature|build\s+.*(module|system|service))": {
        "label": "FEATURE REQUEST",
        "instructions": [
            "1. Confidence Check: rate 0-100%. If <70% — ask clarifying questions FIRST",
            "2. Brainstorm: identify edge cases, dependencies, trade-offs (2-3 alternatives)",
            "3. Create spec in docs/todo/feature-name.md BEFORE any code",
            "4. Break into tasks of 2-5 min each, get sign-off",
            "5. TDD: write failing test FIRST, then minimal code, then refactor",
            "6. Verify: /superpowers:verification-before-completion before claiming done",
        ]
    },
    # Architecture / design / project structure
    r"(архитектур|спроектируй|design\s+(system|arch)|перестрой|restructur|новый\s+проект|new\s+project)": {
        "label": "ARCHITECTURE TASK",
        "instructions": [
            "1. Confidence Check: rate 0-100%. If <70% — research first, DO NOT design",
            "2. Use /sc:design --architect for structured design",
            "3. Present 2-3 architectural alternatives with pros/cons/trade-offs",
            "4. Create ADR in docs/adr/ for the decision",
            "5. Get human approval BEFORE any implementation",
            "6. Use Wave-Checkpoint-Wave for parallel exploration",
        ]
    },
    # Refactoring / rewrite
    r"(рефактор|refactor|перепиш|rewrite|переделай|миграц|migrat)": {
        "label": "REFACTORING",
        "instructions": [
            "1. Use Serena find_referencing_symbols to map ALL dependencies FIRST",
            "2. Write tests covering current behavior BEFORE changing anything",
            "3. Use /superpowers:subagent-driven-development (fresh subagent per task)",
            "4. Make changes in isolated git worktree (/superpowers:using-git-worktrees)",
            "5. Run full test suite after each change, not just at the end",
        ]
    },
    # Deploy / release / production
    r"(деплой|deploy|релиз|release|продакшен|production|запуск|launch)": {
        "label": "DEPLOYMENT",
        "instructions": [
            "1. Run /superpowers:verification-before-completion FIRST",
            "2. Check Sentry for unresolved errors (sentry-mcp: list_issues)",
            "3. Run full test suite: pytest tests/ -v",
            "4. Check pre-commit: pre-commit run --all-files",
            "5. Verify no secrets in code: detect-private-key",
            "6. Create release notes with /sc:document",
        ]
    },
    # Billing / payments / money
    r"(биллинг|billing|оплат|payment|подписк|subscription|тариф|pricing)": {
        "label": "BILLING/PAYMENTS (HIGH RISK)",
        "instructions": [
            "1. Confidence Check: MUST be >90% for payment logic. If not — STOP",
            "2. Create FULL spec in docs/todo/ with all edge cases",
            "3. Security review: /sc:analyze --security on payment code",
            "4. TDD with edge cases: double charges, refunds, race conditions",
            "5. ADR for payment provider choice in docs/adr/",
            "6. NEVER store card data — use provider tokens",
        ]
    },
}

# ============================================================
# TIER 2: SKILL REMINDERS (normal tasks — soft suggestions)
# ============================================================

SKILL_MAP = {
    # Planning
    r"plan|design|структур|проектиров": [
        "Use /superpowers:brainstorming BEFORE planning",
        "Then /superpowers:writing-plans for structured plan"
    ],
    # Testing
    r"test|tdd|тест|coverage|покрыт": [
        "Use /superpowers:test-driven-development (Red-Green-Refactor)"
    ],
    # Bug fixing
    r"bug|fix|ошибк|баг|error|crash|debug|отлад|почин": [
        "Use /superpowers:systematic-debugging",
        "Check sentry-mcp: list_issues BEFORE fixing"
    ],
    # Code review
    r"review|ревью|pr\b|pull.?request": [
        "Use /superpowers:requesting-code-review"
    ],
    # Spec
    r"spec|требован|requirement|спецификац": [
        "Use /kiro:spec-init for Spec-Driven Development"
    ],
    # Branch
    r"branch|ветк": [
        "Use /superpowers:using-git-worktrees for isolated branch"
    ],
    # Documentation
    r"документ|docs|readme|changelog": [
        "Use /sc:document for structured documentation"
    ],
    # Performance
    r"performance|оптимиз|slow|медленн|profil": [
        "Use /sc:analyze --performance"
    ],
    # Security
    r"security|безопасн|owasp|vulnerab|уязвим": [
        "Use /sc:analyze --security"
    ],
    # MCP reminders
    r"отзыв|feedback|ответ.?на.?отзыв": [
        "Use marketai-db MCP for review data"
    ],
    r"товар|product|карточк|sku": [
        "Use marketplace-api MCP for product operations"
    ],
    r"pubmed|наук|science|исследован": [
        "Use science-api MCP for scientific data"
    ],
    r"библиотек|library|документац": [
        "Use Context7 MCP for up-to-date docs"
    ],
    r"навигац|symbol|функци|class|import": [
        "Use Serena MCP for semantic navigation"
    ],
}

# ============================================================
# PROCESSING
# ============================================================

output_parts = []

# Check MANDATORY patterns first (Tier 1)
mandatory_matched = False
for pattern, config in MANDATORY_PATTERNS.items():
    if re.search(pattern, prompt_lower):
        mandatory_matched = True
        label = config["label"]
        instructions = config["instructions"]
        block = f"MANDATORY CTO WORKFLOW — {label}:\n"
        block += "You MUST follow this sequence. Do NOT skip steps.\n"
        for instr in instructions:
            block += f"  {instr}\n"
        output_parts.append(block)
        break  # Only one mandatory block

# Check SKILL reminders (Tier 2) — only if no mandatory matched
if not mandatory_matched:
    activations = []
    for pattern, skills in SKILL_MAP.items():
        if re.search(pattern, prompt_lower):
            activations.extend(skills)

    if activations:
        seen = set()
        unique = [a for a in activations if a not in seen and not seen.add(a)]
        block = "SKILL ACTIVATION REMINDER:\n"
        for skill in unique[:5]:
            block += f"  -> {skill}\n"
        output_parts.append(block)

# Output
if output_parts:
    print("\n".join(output_parts))
