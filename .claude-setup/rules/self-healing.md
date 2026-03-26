# Self-Healing Infrastructure Rules

## Health Monitoring (ALL production services)
Every deployed service MUST have:
1. `/health` endpoint returning JSON: `{"status": "ok", "db": true, "redis": true, "uptime": 12345}`
2. Docker HEALTHCHECK in Dockerfile/compose
3. External monitoring (Uptime Kuma or similar)
4. Telegram alert on failure

## Docker Compose Health Checks
```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
```

## Auto-Recovery Pattern
```python
# health_monitor.py — run as cron every 5 min
# 1. Check each service health endpoint
# 2. If down 2x in a row → restart container
# 3. If down 3x → alert Telegram with logs
# 4. If down 5x → escalate (call/SMS)
```

## Sentry → GitHub Issue Automation
- New Sentry error with >10 events → auto-create GitHub Issue
- Tag with severity (critical/high/medium/low)
- Assign to project based on Sentry project
- Link back to Sentry issue in GitHub Issue body

## Deploy Rollback
- Every deploy creates a tagged Docker image
- If health check fails after deploy → auto-rollback to previous tag
- Notify Telegram: "Deploy rolled back: [reason]"
- Never deploy on Friday evening

## Backup Strategy
- PostgreSQL: pg_dump daily → S3/local
- Redis: RDB snapshot every 6 hours
- Code: GitHub (already version controlled)
- Secrets: encrypted backup of .env files
- Test restore quarterly
