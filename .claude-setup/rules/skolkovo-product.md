# Skolkovo IT Product Rules

## Context
Резидентство в Сколково. Нужен IT-продукт уровня Сколково:
- Инновационность (AI/ML обязательно)
- Масштабируемость (SaaS модель)
- Документация на уровне (техническая + бизнес)
- Патентоспособность (если применимо)

## Skolkovo Requirements
- Продукт должен решать реальную проблему рынка
- Научно-техническая новизна
- Экономическая модель (unit economics, TAM/SAM/SOM)
- Roadmap на 3 года
- MVP → пилот → масштабирование

## Documentation Standards (for Skolkovo reports)
- Техническое описание продукта
- Архитектура (C4 диаграммы)
- Описание AI/ML компонентов
- Метрики эффективности
- Конкурентный анализ
- Финансовая модель

## Tech Stack Recommendations
- Backend: FastAPI + PostgreSQL + Redis (наш стандарт)
- AI: собственные модели или fine-tuned (не просто API wrapper)
- Infrastructure: Docker + CI/CD + monitoring
- Documentation: автогенерация из кода + Mermaid диаграммы
