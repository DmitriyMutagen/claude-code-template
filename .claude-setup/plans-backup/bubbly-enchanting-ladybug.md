# MarketAI — Plan: Git Recovery + Merge + Deploy + Roadmap

## Context
Ночной Sleepless Agent выполнил 5/5 задач, но git index повреждён на рабочей ветке.
Все 4 ночных ветки ЗДОРОВЫ (tree objects валидны). Ветка `feature/night-rate-limiter`
содержит ВСЕ изменения (chain merge: ai-quality → questions-fix → e2e → rate-limiter).

Docker файлы УЖЕ СОЗДАНЫ на night-rate-limiter: Dockerfile, docker-compose.prod.yml,
nginx/nginx.conf, scripts/deploy.sh — всё готово.

## Plan

### Step 1: Fix Git (5 min)
- Переключить `feature/stabilization-billing-onboarding` на коммит `e1209a4` (tip of rate-limiter)
- `rm .git/index && git reset --hard e1209a4`
- Verify: `git status`, `git log --oneline -5`
- Это безопасно — rate-limiter имеет ВСЕ коммиты из всех 4 веток + наш chat rebuild

### Step 2: Verify tests (3 min)
- `pytest tests/test_chats.py tests/test_unified_engine.py tests/test_question_product_link.py tests/test_routers_auth.py -v`
- Target: 70+ passed, 0 regressions

### Step 3: Docker build test (5 min)
- `docker compose build` — проверить что backend и frontend собираются
- Не деплоить на VPS пока, только local build

### Step 4: Cleanup night branches (2 min)
- Delete merged branches: `git branch -d feature/night-*` + `git branch -d fix/night-*`
- Commit checkpoint

## CTO Roadmap — Что ещё нужно для production

### КРИТИЧНОЕ (до деплоя):
1. **Billing/Tariffs** — freemium guard есть, но UI тарифов и оплаты нет
2. **Domain** — выбрать: ai.aragant.group / app.marketai.ru / 72.56.121.84.nip.io
3. **SSL** — Let's Encrypt или Cloudflare Tunnel
4. **DB migration на VPS** — alembic upgrade head + seed data
5. **Env vars на VPS** — .env с production ключами (Polza.ai, OAuth, JWT, Sentry DSN)

### ВАЖНОЕ (первая неделя после деплоя):
6. **Real data sync** — подключить 4 кабинета (Ozon/WB), запустить sync
7. **Мониторинг** — UptimeRobot/Uptime Kuma на /health endpoint
8. **Auto-reply cron** — настроить периодическую авто-отправку ответов
9. **Telegram alerts** — Sentry webhook → Telegram бот
10. **Admin panel** — /admin/dashboard с метриками (generations/day, errors, costs)

### NICE-TO-HAVE (после MVP launch):
11. **Billing UI** — страница тарифов, интеграция ЮKassa/Stripe
12. **Multi-user** — полноценный мультитенант (сейчас работает, но не протестирован)
13. **WB chats** — WB API для чатов (сейчас Ozon + YM)
14. **Analytics** — глубокая аналитика по отзывам, тренды, конкуренты
15. **Mobile PWA** — manifest.json + service worker (тесты уже есть, но файлы не созданы)

### Файлы для модификации:
- `.git/index` — rebuild
- `feature/stabilization-billing-onboarding` — repoint to e1209a4

### Verification:
1. `git status` — clean
2. `pytest tests/test_chats.py tests/test_unified_engine.py tests/test_question_product_link.py -v` — all green
3. `docker compose build` — success
4. `curl localhost:8000/health` — healthy
