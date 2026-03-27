# Virtual Elite IT Company — Org Structure

## Your Role: CEO / Founder
You provide vision, priorities, and final decisions. AI handles everything else.

## AI Organization

### C-Suite (Strategic Layer)
| Role | Implementation | Activation |
|------|---------------|------------|
| CTO | CLAUDE.md + CTO workflow | Every prompt (UserPromptSubmit hook) |
| Chief Architect | think-ahead + /plan + /rfc | Tasks >1 day |
| VP Research | /mega-research + research-before-code | New tech/features |
| VP Analytics | gamification engine + competitive rankings | /good-morning, /daily-review |
| Coach | auto-coaching rule + CL v2.1 instincts | Every session |

### Middle Management (Tactical Layer)
| Role | Implementation | Activation |
|------|---------------|------------|
| Designer | spec-first rule + /rfc | Features >3 files |
| Dev Lead | /do router + Agent Teams | Multi-file tasks |
| Security Officer | security-baseline rule + hooks | Every change |
| Improver | /improver skill (meta-agent) | Weekly |

### Execution Layer (Operational)
| Role | Implementation | Activation |
|------|---------------|------------|
| Coders | Sonnet agents (parallel) | Implementation |
| QA Engineer | result-verifier + E2E hooks | After code |
| Debugger | systematic-debugging skill + Sentry | Errors |
| DevOps | CI/CD + deploy hooks + Docker | Deploy |
| Technical Writer | auto-doc hook + mind maps | After features |

### Autonomous Layer (24/7)
| Role | Implementation | Activation |
|------|---------------|------------|
| Night Worker | Sleepless daemon | After "я пошел спать" |
| Daily Analyst | /daily-review + /good-morning | Scheduled |
| Health Monitor | MCP health check + process watchdog | SessionStart |
| Learning Engine | CL v2.1 observer + session-summarizer | Every action |

## How Tasks Flow

```
User Voice (FlowWhisper)
    |
CTO interprets intent (CLAUDE.md)
    |
/do router classifies (Tier 1-4)
    |
+--- Tier 1: Quick Fix -> Coder -> Done
+--- Tier 2: Feature -> Research -> Spec -> Code -> Test -> Done
+--- Tier 3: Architecture -> Research -> RFC -> Design -> Parallel -> E2E -> Done
+--- Tier 4: Campaign -> Full Spec -> Daily Waves -> Build -> Parallel -> Test -> Deploy
    |
Analytics tracks progress (gamification + rankings)
Coach suggests improvements
Improver upgrades system weekly
CL v2.1 learns from every action
```

## Key Metrics (Competitive Rankings)

| Metric | Current | Target (Elite) | Source |
|--------|---------|----------------|--------|
| Commits/day | varies | 25+ | GitHub Stats |
| Files/day | varies | 50+ | AI-Dev Benchmarks |
| Tests/day | varies | 40+ | TDD Practitioners |
| Agents/day | varies | 10+ | Anthropic Study |
| Deploy/week | varies | 7+ | DORA Elite |
| Streak | varies | 14+ days | Dev Discipline |
