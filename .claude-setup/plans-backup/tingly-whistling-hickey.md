# Plan: Первая задача для Agent Team — Battle Test P0

## Context
Проект MarketAI v1.6.0. Все ключевые фичи до freemium реализованы.
Система готова к production, но BATTLE_TEST_PLAN.md (120+ тестов) — полностью не выполнен (все ⬜).
Sprint 6 тест-стабы уже созданы (test_sprint6_*.py), но тесты внутри, вероятно, пустые/pending.
Следующий приоритет из MEMORY: Chrome Extension → WB product linking → Mailings.

**Цель плана:** Определить первую конкретную задачу для делегирования команде агентов (showrunner + qa-tester).

---

## Рекомендуемая первая задача: Battle Test P0 Execution

### Почему именно P0?
- P0 = Critical: инфраструктура + auth + product linking (~15 тестов)
- Пока система не проверена — небезопасно брать Sprint 6
- qa-tester идеально подходит: запускает pytest + curl + psql проверки
- Результат: baseline-отчёт о состоянии системы перед Sprint 6

### Что входит в P0 (из BATTLE_TEST_PLAN.md)
1. **§1 Инфраструктура** — PostgreSQL доступен, все таблицы есть, Redis PING, FastAPI /health
2. **§2 Auth** — регистрация, логин, JWT, API Key fallback, expired token
3. **§5 Product Linking** — internal_sku populated, product_id linked в reviews

---

## Делегирование агентам

### Агент 1: showrunner (оркестратор)
**Задача:** Прочитать BATTLE_TEST_PLAN.md §1, §2, §5. Декомпозировать на тест-шаги.
Написать bash-скрипт `artifacts/battle_test_p0.sh` с curl + psql командами.
Запустить qa-tester на выполнение.

### Агент 2: qa-tester (исполнитель)
**Задача:**
1. Запустить `pytest tests/ -v -k "not ozon_chat"` (исключить 63 падающих event loop тестов)
2. Выполнить curl smoke-тесты из BATTLE_TEST_PLAN.md §1.3, §2.1
3. Выполнить SQL-проверки §1.1, §3.1, §5.1 через psql
4. Сформировать отчёт: какие тесты прошли / упали / заблокированы

---

## Файлы для работы агентов

- `marketai/BATTLE_TEST_PLAN.md` — тест-план (источник задач)
- `marketai/tests/` — все pytest файлы
- `marketai/tests/test_freemium_guard.py` — последний написанный тест (6 PASS — эталон)
- `marketai/src/api/main.py` — entry point
- `.env` — конфигурация (JWT_SECRET_KEY, DB URL)

---

## Как запустить агентов

```
showrunner: "Прочитай BATTLE_TEST_PLAN.md §1 §2 §5, разбей на тест-кейсы,
             делегируй qa-tester для выполнения P0 smoke-тестов"

qa-tester: "Выполни P0 тесты из BATTLE_TEST_PLAN.md: pytest + curl + psql.
            Отчёт в artifacts/battle_test_p0_report.md"
```

---

## Verification
По итогу первой задачи у нас будет:
- `artifacts/battle_test_p0_report.md` — отчёт P0 статуса
- Список broken/blocked тестов
- Baseline для принятия решения о старте Sprint 6
