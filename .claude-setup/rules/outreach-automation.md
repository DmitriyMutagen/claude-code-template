# B2B Outreach Automation Rules

## Scope
Полностью автоматический аутрич для селлеров маркетплейсов.
Масштаб: тысячи номеров, идеальный уровень персонализации.

## Pipeline Architecture
```
Data Collection → Enrichment → Scoring → Personalization → Outreach → Follow-up → CRM
```

### 1. Data Collection
- Парсинг WB/Ozon: продавцы по категориям
- Извлечение контактов: ИНН → ЕГРЮЛ → телефон/email
- Sources: WB API, Ozon API, СПАРК, Rusprofile, 2GIS

### 2. Enrichment
- Размер бизнеса (оборот, кол-во SKU)
- Рейтинг продавца
- Проблемы (плохие отзывы, низкий рейтинг)
- Конкуренты в нише

### 3. Scoring (Lead Quality)
- Revenue estimate (A/B/C)
- Response likelihood (горячий/тёплый/холодный)
- Product-fit score

### 4. Personalization
- AI-генерация сообщения под конкретного продавца
- Упоминание его товаров/проблем/конкурентов
- Несколько каналов: WhatsApp, Telegram, Email, Phone

### 5. Outreach Execution
- Rate limiting: не больше 50 сообщений/час на канал
- Randomized delays (30-120 сек между сообщениями)
- Anti-ban: ротация аккаунтов, прогрев
- A/B тестирование сообщений

### 6. Follow-up Chain
- Day 0: Первый контакт
- Day 2: Follow-up если нет ответа
- Day 5: Другой канал
- Day 10: Финальный follow-up
- Stop: если ответил или отписался

## Technical Requirements
- PostgreSQL: хранение лидов, статусов, истории
- Redis: очереди сообщений, rate limiting
- Celery/ARQ: async task queue для отправки
- Anti-detection: разные прокси, fingerprints
- Compliance: unsubscribe механизм, GDPR-like

## Quality Metrics
- Response rate > 15%
- Meeting booking rate > 5%
- Unsubscribe rate < 2%
- Delivery rate > 95%
