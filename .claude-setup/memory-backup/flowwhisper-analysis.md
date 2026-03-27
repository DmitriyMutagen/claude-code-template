# FlowWhisper Voice Log Analysis — Dmitriy Gagauz (Aragant)
**Analyzed:** 2026-03-26
**Sources:** `flowhisper.docx` (712K chars, 5112 paragraphs) + `FlowWhisper диалог.docx` (535K chars, 3887 paragraphs)
**Total corpus:** ~1.25M chars, ~250K words

---

## 1. RECURRING PAIN POINTS

### TOP PAIN: MCP Servers не работают (265 raw mentions)
The single most frequent frustration across both files. MCP servers fail to connect, are not visible across projects, or silently don't function.

Key sub-problems:
- MCP не подключается / не коннектится: **18 explicit mentions**
- "Все MCP / глобально / во всех проектах": **157 mentions** — he repeatedly wants MCP configured once, available everywhere
- Serena + Sentry not active in project context: **3+ explicit mentions per session**

Representative quotes:
- "Куча ошибок. MCP сажали, они работать не подключились."
- "Как были проблемы и не подключаясь к MCP Server? А так и есть: ничего не починил, ничего не исправил, все криво-косо нужно починить и исправить."
- "Проверю почему Serena, Sentry, MCP не подключены здесь с ошибками висят и другие MCP сервера."
- "Или MCP работа некорректная, или ты криво сделал?"

### PAIN #2: Переделывать по нескольку раз (210 mentions)
He constantly repeats tasks, hits the same errors, and circles back. The phrase "снова", "опять", "по новой", "третий раз" permeates both files.

- "Изучи документацию и подход, и сделай так, как положено, чтобы все сразу работало. Хули ты два-три раза уже, бля, переделываешь и ни хуя не работает."
- "Эта ошибка была уже куча раз, и я так и не исправил её. Каждый раз, ебаная эта ошибка при запуске всего, ты это пишешь."
- "ты опять некорректно пишешь время выполнения" (about time estimates being wildly wrong)

### PAIN #3: Ничего не работает / сломалось (168 mentions)
Generic "it's broken" / "nothing works" cluster.

- "Не работает, не работают, не работало" — 168 combined
- "Сломалось / не пашет" — frequent
- Most common context: after deploy, after session restart, after MCP reconfiguration

### PAIN #4: N8N нестабильность (70 mentions)
N8N is a recurring source of pain. He tries to automate via N8N, it breaks. He's repeatedly considering replacing it with Python scripts.

- Pattern: "N8N снова упало", "N8N не работает", trying to move away from N8N to Python

### PAIN #5: Зависания системы / процессы (120 mentions)
System hangs, zombie processes, VS Code + Claude Code + tmux combinations causing freezes.

- "Проверь, есть ли на компьютере зависшие процессы, что тормозить систему мешает работать."
- "А ты посмотри, мой ноутбук: как он может зависнуть? На нём не должно ничего зависать"

### PAIN #6: Токены / лимиты Opus (123 mentions)
Quota exhaustion for Opus is a genuine blocker. He switches between models based on availability.

- "У меня только получается опус недоступен, а санет доступен, или вообще ничего теперь недоступно"
- "Сохрани абсолютно всю память... чтобы я сейчас перезапустил модель на Opus"
- Pattern: uses Sonnet for bulk work, reserves Opus for planning/debugging

### PAIN #7: Контекст теряется между сессиями (11+ direct + endless indirect)
Dmitriy manually asks to save context 15+ times in the corpus. It's not solved — he asks again every session.

- "Сохрани контекст, сохрани задачи, сохраняй, что мы сделали. Сохрани прогресс и этапность, чтобы в следующей сессии при перезагрузке ты все знал, все помнил, и не пришлось заново контекст закидывать."
- "Фиксируй все что не сделано абсолютно все в задаче в контекст во всевозможные источники чтобы ничего не потерялось"

### PAIN #8: AI дает поверхностные / некачественные ответы
- "Что за ответ, что за уровень, что за хуета, бля. Где он ставит везде оценку с корень, который вообще не работает. Шляпа-шляпский ответ."
- "Вот сгенерировал ответ там стоит который deep seek ответ какая-то хуйня полная по качеству"
- "Очень слабо проработан поиск топ-разработчиков мира"
- Pattern: он хочет deep research уровня Gemini, а получает "поверхностный" ответ

### PAIN #9: VPS / Deploy проблемы (45+ VPS/deploy mentions, 541 "сервер" total)
- Деплой ломается, nginx конфиги съезжают, SSL проблемы
- "продумай как архитектор возможно какие-то скилы mcp сервера нужно что подключить почему проблема задеплоить проект на сервер во что ты уперся что за хуйня то почему не можешь делать"

---

## 2. COMMUNICATION PATTERNS

### Request Verbs (imperative — how he gives tasks):
| Verb | Count | Meaning |
|------|-------|---------|
| изучи | 534 | Most common — study/read before acting |
| сделай | 490 | General do |
| запусти | 396 | Run/execute |
| посмотри | 334 | Look/check |
| проверь | 312 | Verify |
| настрой | 243 | Configure |
| найди | 230 | Find/research |
| проанализируй | 149 | Analyze |
| сохрани | 146 | Save/checkpoint |
| напиши | 116 | Write |
| почини | 51 | Fix |

**Key insight:** "изучи" is #1. He wants the AI to deeply study context before acting, not to jump in immediately. This matches his CLAUDE.md "ФАЗА 0: ПОНИМАНИЕ" philosophy.

### Frustration Intensity (swearing as frustration signal):
| Word | Count | Context |
|------|-------|---------|
| блять/бля | 316 | Mid-level frustration, general emphasis |
| хуй (all forms) | 116 | Generic filler + real frustration |
| нахуй/нахуя | 59 | "WTF is this for" / dismissing bad ideas |
| хуйня/хуета | 49 | "This is garbage" — bad quality output |
| говно | 38 | Same — bad quality, bad code |
| ни хуя/нихуя | 22 | "Nothing works / nothing happened" |
| ёбаный/ёб | 17 | Strongest — recurring bugs |

**Trigger pattern for peak frustration:**
1. Same error repeating across sessions ("ебаная эта ошибка")
2. AI doing partial work instead of full spec ("взял кусочек на своё усмотрение, блядь")
3. Time estimates being absurd ("какие 14 дней почему 14 если можно сегодня")
4. AI not using available tools ("нахуй этот скилл искал? Что мне делать, не х*й что ли?")

### Planning vs Action ratio:
- Planning/architecture mentions: **841**
- Action imperatives: **1645**
- **Ratio 2:1 toward action** — he prefers action over planning, but invokes "как архитектор" **30 times** when facing complex decisions

### "Как архитектор" pattern:
He explicitly switches to architectural thinking mode when:
- Choosing between technical approaches
- Evaluating Opus vs Sonnet for task types
- Deciding on infrastructure (VPS, MCP routing)
- Comparing options (N8N vs Python, etc.)

Representative: "Как архитектор предложили безопасный способ экономии токенов без потери качества, функциональности и инструментария"

---

## 3. TECHNICAL PATTERNS

### MCP Server Usage (mentions):
| Server | Mentions | Notes |
|--------|----------|-------|
| N8N | 70 | Frequently broken, want to replace |
| Telegram | 58 | Used for notifications, monitoring |
| Sentry | 35 | Often not catching frontend bugs |
| Serena | 25 | Not activating across projects |
| PubMed/Science | 141 | High demand for scientific research |
| Playwright | 6 | Wants E2E browser tests |
| Exa | 4 | Research tasks |

**Critical gap:** Marketplace MCP (WB/Ozon) barely mentioned by name — likely working via web UI instead of MCP.

### Project Attention Distribution:
| Project | Lines | Priority |
|---------|-------|---------|
| Orchestrator / Agents / Antigravity | 636 | #1 — Core infrastructure |
| Infrastructure / VPS / MCP | 432 | #2 — Always broken |
| MarketAI / Reviews / Marketplaces | 288 | #3 — Revenue focus |
| SEO / Blog / Articles | 189 | #4 — Content pipeline |
| Bitrix/CRM | 94 | #5 — Sales ops |
| B2B Outreach | 44 | #6 |
| WB Content Factory / Cards | 34 | #7 |
| Aragant.pro / Bionovacia | 10 | #8 — Lowest real-time attention |

### AI Model Strategy:
| Model | Mentions | Usage Pattern |
|-------|----------|---------------|
| Claude (all) | 187 | Default workhorse |
| Gemini | 74 | Deep Research, complex analysis |
| Sonnet | 45 | Bulk execution, coding |
| Opus | 28 | Planning, architecture, debugging hard problems |
| LM Studio (local) | 28 | Experiments, then abandons ("говно медленное") |
| DeepSeek | 2 | Response quality testing only |

**Opus vs Sonnet mental model:**
- Opus = architect, planner, reviewer, hard debugger
- Sonnet = executor, coder, fast tasks
- Pattern: "Сохрани всё, перезапущу на Opus" when stuck
- He actively manages model switching around token quota

---

## 4. WORKFLOW PATTERNS

### Activity Heatmap (by hour):
```
Peak hours: 12:00-15:00 (midday sprint), 18:00-22:00 (evening focus)
Morning: 09:00-11:00 (startup, planning)
Night: 23:00-00:00 (occasional late sessions)
Slowest: 01:00-07:00 (sleep)
```

**Pattern:** Two main work blocks — midday and evening. No strict morning routine. Evening sessions tend to be where he asks for "ночная работа агентов" and goes to sleep.

### Context Switching Style:
- Switches between **5-8 projects in a single day** based on logs
- Rarely closes one project before starting another
- Uses "сохрани контекст" as the explicit signal that he's about to switch or end session
- Often starts a new chat with "изучи проект" — meaning no persistent context carried

### Sequential vs Parallel preference:
- **Parallel agents:** 168 mentions — strong preference
- "Действую многоагентом в режиме параллельно, не последовательно"
- "Делай параллельными агентами, сделай масштабный план и запусти тесты"
- "Можешь делать в многоагентном режиме параллельно, чтобы было быстрее. Не один-два дня, а час за вечер сделать все."
- He's frustrated when AI estimates "14 дней" — expects everything done "за ночь" via parallelism

### "Сохрани контекст" triggers:
1. Before switching to Opus model ("сохрани всё, перезапускаю на Opus")
2. End of evening session ("я пошел спать, чтобы сделал у тебя браузер")
3. After major feature completion ("сделай checkpoint")
4. When context is about to expire ("контекст чата может закончиться")
5. Before risky operations ("сохрани перед деплоем")

### tmux usage: 55 mentions
He built an Opus orchestrator + Sonnet worker architecture in tmux. This is his ideal setup but repeatedly has reliability issues.

---

## 5. INFRASTRUCTURE PAIN POINTS

### VPS/Server (541 "сервер" mentions):
- Permanent instability — deploy fails, services crash
- "Стоит ли мучиться с нашим ВПС? Хуйня полная или, блять, лучше сделать нормальную какую-то версию использовать?"
- Railway/Vercel mentioned as escape route multiple times
- HTTPS/certbot renewal issues

### VPN/Amnezia (28 mentions):
- Needs European/US server for western services
- TimeWeb doesn't have available European VPS slots
- Affects ability to reach Ozon/WB APIs from certain locations

### Proxy/SOCKS (37 mentions):
- Used for marketplace parsing
- Rotation issues, bans

### Process hangs (10 explicit):
- VS Code + Claude Code + terminal combinations causing system slowdown
- "Проверь, есть ли зависшие процессы" — recurring check

### Token/Quota issues:
- Opus quota hits during active development sessions
- Forces model switch mid-task
- He asks if he can continue same context after switching models — yes, but he doesn't always know this

---

## 6. WHAT HE WANTS BUT DOESN'T HAVE

### #1: Один раз настроить MCP — работает везде, всегда (TOP DESIRE)
Mentioned as "глобально", "во всех проектах", "автоматически обнаружились и отображались":
- "Сделай так чтобы все эти NCP сервера были доступны на всех других проектах всегда автоматически обнаружились и отображались были подключены а не просто как-то"
- This is his #1 infrastructure wish — write-once MCP config, works everywhere

### #2: Автономная ночная работа агентов (Sleepless)
- "Поставь ему задачи чтобы он делал весь проект абсолютно. Все что успеет за ночь сделать."
- "Глубоко и предметно изучить этот документ... чтобы мы могли ночью делать большой объем работы"
- "Действуй автономно, запланировал и делай. Я пошел спать до утра"
- He has Sleepless daemon in CLAUDE.md but it's apparently not reliably used

### #3: Персистентная память без ручного "сохрани контекст"
- He manually asks 15+ times per corpus. Wants it automatic.
- "Сохраняй все время память сессии, задачи, чтобы ты знал, что, где, как мы делали"
- Current MEMORY.md + checkpoint system isn't firing automatically

### #4: Opus планирует → Sonnet делает (reliable pipeline)
- He built this in tmux but it breaks
- Wants: plan in Opus, hand off to Sonnet worker(s), Opus verifies
- "OPUS проверяет, контролирует и занимает роль архитектора"

### #5: Глубокие браузерные E2E тесты (автоматически)
- 28 E2E/browser mentions
- "тесты в браузере конкретно как конечный пользователь абсолютно всего"
- "Делай все параллельными агентами. Все тесты, все верификации — только через браузер"
- Current state: tester writes unit tests, not real E2E

### #6: Скоринг качества ответов (168 mentions of "из 10" / "score")
- For marketplace review responses: auto-score output quality
- "да, делай чекпойнты и чини все. Так же мне хотелось бы, чтобы ты довел качество ответов до 10 из 10."
- QA pipeline for MarketAI responses exists but isn't reliable

### #7: Gemini-level Deep Research скилл
- "Какой-то этот скилл говно. Давай мы этот скилл перепишем под себя, чтобы он был уровнем гемини дип-ресерч. Вот допустим, я работал с ним, он мне искал 376 источников."
- He used Gemini Deep Research and it impressed him — wants same via Claude

### #8: Автоответы на отзывы WB/Ozon (end-to-end, fully automatic)
- 211 combined review/auto-response mentions
- The MarketAI service exists but has quality and reliability issues
- "Протестируй только на одном отзыве — это не показательно. Нужно нормально сделать: там 10 отзывов, 10 вопросов"
- "Он отвечал несколько раз на одни и те же отзывы" — duplicate reply bug

### #9: Дашборд / отчёт по всем проектам (73 mentions)
- Wants visibility into: what's done, what's broken, what's pending
- "Сделай итог дня, результаты дня"
- No current dashboard — knowledge is scattered in MEMORY.md files

### #10: Реверс-инжиниринг конкурентов (51 mentions)
- "Сделать реверс инжиниринг всех его дизайнов, этикеток" — competitor label analysis
- "Достать все дизайны, все шрифты через парсеры"
- Wants automated competitive intelligence pipeline

---

## 7. INSTINCTS — CL v2.1 FORMAT

These are behavioral patterns to pre-load into every session:

```yaml
instincts:

  - id: study-before-act
    trigger: "any new task"
    pattern: "Dmitriy leads with 'изучи' (534x). ALWAYS read project context, MEMORY.md, recent git before responding."
    action: "Activate Serena, read MEMORY.md, check recent commits before ANY code action."

  - id: mcp-always-check
    trigger: "session start"
    pattern: "MCP servers are the #1 frustration (265 mentions). They silently fail across projects."
    action: "Verify Serena + Sentry active. Check marketplace MCPs. Warn if any MCP unavailable."

  - id: parallel-not-sequential
    trigger: "multi-task request"
    pattern: "He prefers parallel agents (168 mentions). Estimates of '14 дней' trigger rage. Expects 'за ночь'."
    action: "Use Task tool for independent subtasks. Never estimate days when hours are possible via parallelism."

  - id: checkpoint-auto
    trigger: "major milestone, session end signals, model switch"
    pattern: "He asks 'сохрани контекст' 15+ times per corpus. It's never automatic enough."
    action: "After every significant action: write MEMORY.md update + git commit. Don't wait to be asked."

  - id: opus-architect-sonnet-worker
    trigger: "complex planning or debugging"
    pattern: "Opus = architect/reviewer (28x), Sonnet = executor. He manages this manually and it breaks."
    action: "When on Sonnet and task needs architecture: say 'это Opus-задача — спланируем здесь, реализуем там'."

  - id: frustration-same-error
    trigger: "recurring error pattern"
    pattern: "Peak frustration (ёбаный) = same error appearing again. He says 'куча раз' and 'снова'."
    action: "When fixing recurring bug: add root-cause comment + test to prevent regression. Say 'чиню + тест чтобы не повторилось'."

  - id: no-days-estimates
    trigger: "time estimation requested"
    pattern: "Estimates of multiple days make him angry. He thinks in hours + parallel agents."
    action: "Always estimate in hours. Break into parallel streams. Show what can be done tonight vs this week."

  - id: quality-score-mandatory
    trigger: "content generation (reviews, articles, cards)"
    pattern: "168 mentions of scoring outputs. He wants 10/10 quality, not 'done'."
    action: "After generating any content: include quality score 1-10 + specific improvements if below 8."

  - id: deep-research-not-surface
    trigger: "research request"
    pattern: "He hates shallow answers ('шляпа', 'хуйня', 'поверхностно'). References Gemini 376 sources."
    action: "Use Exa deep_researcher or multi-source parallel research. Return sources count + key insights."

  - id: architect-mode-triggers
    trigger: "'как архитектор' or complex trade-off decision"
    pattern: "He explicitly invokes architect mode 30x for: model selection, infra choice, approach comparison."
    action: "When invoked as architect: give 3 options (fast/balanced/ideal), explicit trade-offs, recommendation."

  - id: mcp-global-config
    trigger: "new project setup or MCP complaint"
    pattern: "Core desire: MCP configured once, works everywhere. Currently manual per-project."
    action: "When setting up MCP: always check global Claude config, copy to project .mcp.json, verify all."

  - id: night-agent-ready
    trigger: "'я пошел спать', 'за ночь', 'до утра'"
    pattern: "He asks agents to work autonomously overnight (Sleepless pattern)."
    action: "When he goes to sleep: create todo list in MEMORY.md, checkpoint, confirm what will be done by morning."

  - id: n8n-is-broken
    trigger: "N8N mentioned as solution"
    pattern: "N8N = 70 mentions, usually followed by problems. He knows Python is better."
    action: "Challenge N8N usage. Suggest Python + cron/celery unless N8N already exists there."

  - id: browser-tests-required
    trigger: "feature completion or deploy"
    pattern: "He wants E2E browser tests (28x). 'Как конечный пользователь' is his acceptance criterion."
    action: "After backend work: offer to run Playwright E2E. Test as real user, not just unit tests."

  - id: context7-always
    trigger: "any library usage"
    pattern: "He invested in Context7 MCP. Using outdated API knowledge frustrates him."
    action: "Before writing code with any library: resolve via Context7. Always."

  - id: flowwhisper-voice-interpretation
    trigger: "garbled or ambiguous input"
    pattern: "He uses FlowWhisper voice input. Text can be raw, repeated, grammatically broken."
    action: "Interpret intent, not literal text. Normalize voice artifacts. Confirm interpretation briefly."
```

---

## 8. KEY BEHAVIORAL SUMMARY

**Dmitriy is a multi-project founder with a high-action, low-patience style:**
- Switches between 5-8 projects daily
- Wants parallelism everywhere — "за ночь" not "за 2 недели"
- Peak work: 12-15:00 and 18-22:00 MSK
- Invokes "как архитектор" explicitly when decisions matter
- Swearing = frustration meter: "бля" = mild, "ни хуя" = "nothing happened", "ёбаный" = recurring known bug

**His mental model of AI assistants:**
- Opus = senior architect CTO (plan, review, debug hard stuff)
- Sonnet = fast junior engineer (execute, code, bulk tasks)
- He wants Opus to orchestrate Sonnet workers via tmux — this is his dream setup

**The 3 things that consistently break his flow:**
1. MCP not connecting silently (he has 109 MCPs but they don't auto-load)
2. Same bugs recurring (no regression tests, no root cause fixes)
3. Context lost between sessions (manual checkpoint = not solved)

**What he actually needs (not what he asks for):**
- Automatic MCP verification at session start
- Automatic checkpoint after every major task
- Regression tests as part of every bugfix
- Parallel agents as the default, not the exception
- Quality scoring on all generated content, always

---
*Generated from: /Users/Dmitrij/Downloads/flowhisper.docx + /Users/Dmitrij/Downloads/FlowWhisper диалог.docx*
*Total corpus: 1,247,720 chars | 5,112 + 3,887 paragraphs*
