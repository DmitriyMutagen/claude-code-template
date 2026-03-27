---
name: tech-radar
description: Technology Radar — quarterly review of tools, frameworks, and approaches. Adopt/Trial/Assess/Hold classification inspired by ThoughtWorks.
---

# /tech-radar — Technology Radar

## When to Use
- Quarterly review (every 3 months)
- When considering a new technology
- When deciding to drop/replace a tool

## Quadrants

### 1. Languages & Frameworks
### 2. Tools & Infrastructure
### 3. Platforms & Services
### 4. Techniques & Approaches

## Rings

| Ring | Meaning | Action |
|------|---------|--------|
| ADOPT | Proven, use by default | Use in all new projects |
| TRIAL | Worth trying, low risk | Use in 1 project to validate |
| ASSESS | Interesting, needs research | Deep research before using |
| HOLD | Stop using, replace | Migrate away when possible |

## Current Radar (auto-generate from projects)

Analyze all 6 projects to build the radar:

### Languages & Frameworks
- ADOPT Python 3.11+ (all backend projects)
- ADOPT FastAPI (Aragant, Bionovacia, Content Factory)
- ADOPT React / Next.js (frontends)
- ADOPT Three.js (SoulWay B2B — 3D)
- TRIAL TypeScript (moving to strict)
- HOLD N8N (replacing with Python scripts — unreliable)

### Tools & Infrastructure
- ADOPT Docker + Compose (all deploys)
- ADOPT GitHub Actions CI/CD
- ADOPT Claude Code + Agent Teams
- ADOPT PostgreSQL
- ADOPT Redis
- TRIAL Neo4j (Bionovacia only)
- TRIAL Playwright (E2E testing — adopting)
- ASSESS SonarQube (tech debt detection — assess)
- HOLD N8N workflows (replace with Python)

### Platforms & Services
- ADOPT VPS TimeWeb (94.198.219.232)
- ADOPT GitHub
- ADOPT Sentry (error tracking)
- ADOPT Telegram (notifications)
- TRIAL Netlify (SoulWay only)
- ASSESS Vercel (assess for frontends)
- ASSESS Railway (assess as VPS alternative)

### Techniques & Approaches
- ADOPT CL v2.1 (Continuous Learning)
- ADOPT Spec-First Development
- ADOPT Parallel Agent Execution
- ADOPT ADR (Architecture Decision Records)
- TRIAL TDD (adopting, not consistent yet)
- TRIAL E2E Testing (adopting)
- ASSESS Campaign Files (multi-day persistence)
- ASSESS Ars Contexta (knowledge graph)

## Quarterly Review Process
1. Analyze git log for technology usage across all projects
2. Check which tools caused problems (from reflexion.md)
3. Research new tools (mega-research)
4. Update radar
5. Generate mind map
6. Save to docs/tech-radar-YYYY-QN.md
