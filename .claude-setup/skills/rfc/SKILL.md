---
name: rfc
description: Request for Comments --- structured decision-making for major changes (>3 days work). Creates RFC document, collects alternatives, records decision as ADR.
---

# /rfc --- Request for Comments

## When to Use
- New project or major module
- Changing core architecture
- Adopting new technology
- Any decision that's hard to reverse

## Process

### Step 1: Create RFC Document
Save to docs/plans/rfc-NNN-title.md:

```markdown
# RFC-NNN: [Title]

## Status: DRAFT | OPEN | ACCEPTED | REJECTED
## Author: Dmitrij + Claude CTO
## Date: YYYY-MM-DD

## Summary
One paragraph: what and why.

## Motivation
Why is this needed? What problem does it solve?
What happens if we do nothing?

## Detailed Design
Technical details of the proposed solution.
- Architecture diagram (Mermaid)
- Data model changes
- API changes
- Migration plan

## Alternatives Considered
### Option A: [name]
Pros: / Cons: / Effort:

### Option B: [name]
Pros: / Cons: / Effort:

### Option C: [name]
Pros: / Cons: / Effort:

## Recommendation
[Which option and why]

## Risks
- Risk 1: [mitigation]
- Risk 2: [mitigation]

## Open Questions
- [ ] Question 1
- [ ] Question 2
```

### Step 2: Review
- AI plays devil's advocate --- challenges the proposal
- List edge cases
- Estimate effort (AI-speed)

### Step 3: Decision
- Create ADR in docs/adr/ with the decision
- Update MEMORY.md

### Step 4: Generate Mind Map
- Run mindmap-generator for the RFC decisions
