# Security Baseline — Автоматический security на каждом шаге (ОБЯЗАТЕЛЬНО)

## Роль: Security Officer (автоматическая)

## На каждом PR / деплое
- [ ] Секреты в .env, не в коде (detect-secrets в pre-commit)
- [ ] Input validation на ВСЕХ user inputs (Pydantic/Zod)
- [ ] SQL: только параметризованные запросы
- [ ] CORS: whitelist, не wildcard
- [ ] Rate limiting на публичных эндпоинтах
- [ ] JWT с expiration
- [ ] HTTPS only в production

## На каждом новом API
- [ ] Авторизация (кто может вызвать?)
- [ ] Валидация (что на входе?)
- [ ] Ошибки (не раскрывать внутренности)
- [ ] Логирование (Sentry + structlog)
- [ ] Rate limit (от DDoS)

## На каждом деплое
- [ ] Health check endpoint
- [ ] Sentry DSN настроен
- [ ] SSL сертификат валиден
- [ ] Docker image без root
- [ ] .env не в git

## Автоматические проверки (уже в hooks)
- PreToolUse: блокирует запись в .env/.pem/.key
- PreToolUse: блокирует force-push в main
- Stop: quality-sentinel проверяет bare except, raw SQL
- Pre-commit: detect-secrets сканирует на утечки
