# План V2: Переработка WB_ConvChains_AutoFill.gs + прямой деплой + тестирование

## Контекст

Скрипт `WB_ConvChains_AutoFill.gs` (2746 строк) задеплоен в таблицу V5, но не работает полноценно:
- Лист "Запросы" пустой — ключевые слова не загружаются автоматически
- Частотность берётся из search.wb.ru/total (число результатов ≠ реальная частотность)
- Рекламная статистика — все метрики 0 (fullstats без дат)
- Джем-аналитика недоступна через API — нужна браузерная автоматизация
- Фото #ERROR! (IMAGE → HYPERLINK уже исправлено)
- Нет версионирования, debug mode, error boundary

**Таблица:** `1rKbV2nGZvnzZZVC6nuGy_h-MRBVyCFPd8ufLNQUMNAc`
**Service account:** `~/Documents/Orchestrator/агенты/wb_content_factory/google_service_account.json`

---

## Компоненты

```
[1] WB_ConvChains_AutoFill.gs  — GAS: меню + API + заполнение (EDIT)
[2] deploy_and_test.py         — Python: деплой .gs + верификация через gspread (CREATE)
[3] wb_jam_parser.py           — Python: парсинг Джема через браузер → gspread (CREATE)
```

---

## Шаг 1: Исправить GAS-скрипт

**Файл:** `scripts/WB_ConvChains_AutoFill.gs`

### 1.1 Уже сделано
- [x] HYPERLINK вместо IMAGE (ccGetPhotoFormula_)
- [x] Gemini URL: v1beta → v1
- [x] ccFetchCardByNm_: загрузка всех карточек + фильтр
- [x] ui.alert → ccLog_ в pipeline
- [x] Camp B rule-based fallback

### 1.2 Автосбор ключевых слов (НОВАЯ функция)

`ccAutoCollectKeywords_(nmId, token)`:
1. Берёт title + subjectName из карточки
2. Разбивает на значимые слова/фразы → базовые запросы
3. WB Suggest API (`search.wb.ru/suggests/`) расширяет каждый запрос
4. WB Search API (`search.wb.ru/exactmatch/`) — результаты для частотности
5. Фильтрация стоп-слов + дедупликация
6. → массив `{keyword, frequency, cluster}` → лист "Запросы"

Результат: ~50-100 фраз с частотностью автоматически.

### 1.3 Фикс рекламной статистики

**Проблема:** `ccFetchAdStats_` не передаёт `dates` → WB возвращает пустые метрики.
**Фикс:** Добавить последние 30 дней в body:
```javascript
ids.push({ 'id': advertId, 'dates': [beginDate, endDate] });
```

### 1.4 Улучшения инфраструктуры
- `CC_VERSION_ = '2.0.0'` + `CC_BUILD_DATE_`
- `ccSafeRun_(fn, moduleName)` — try-catch wrapper
- `CC_DEBUG_` через PropertiesService + пункт меню
- `ccHealthCheck_()` — проверка токенов/Gemini
- Итоговая метрика: `[v2.0.0] Pipeline: 8/8 | API: 14 | Time: 52s`

### 1.5 Переработка pipeline
Текущий: требует ручной ввод nmID + ключевых слов.
Новый: спрашивает только nmID → всё остальное автоматически.

---

## Шаг 2: Python-деплой + тестирование

**Файл:** `scripts/deploy_and_test.py`

1. Читает `scripts/WB_ConvChains_AutoFill.gs`
2. Подключается к таблице через gspread + service account
3. Записывает данные напрямую в листы для тестирования
4. Для деплоя .gs кода — через Apps Script API (если SA имеет доступ) или генерирует ТЗ для Antigravity

---

## Шаг 3: Парсер Джема

**Файл:** `scripts/wb_jam_parser.py`

1. Camoufox/playwright → seller.wildberries.ru
2. Навигация: Аналитика → Джем → артикул → отчёт по фразам
3. Парсинг: фраза, показы, клики, CTR, заказы
4. Push в лист "Джем" через gspread
5. Fallback: принимает CSV/XLSX из ручного экспорта

---

## Параллельная работа (Agent Team)

```
[Agent 1: coder] → GAS-скрипт: keywords + fullstats + pipeline + debug
[Agent 2: coder] → deploy_and_test.py: gspread + service account
[Agent 3: coder] → wb_jam_parser.py: browser automation
[Agent 4: reviewer] → Code review после завершения
```

---

## Критичные файлы

| Файл | Действие |
|---|---|
| `scripts/WB_ConvChains_AutoFill.gs` | EDIT |
| `scripts/deploy_and_test.py` | CREATE |
| `scripts/wb_jam_parser.py` | CREATE |
| `TASK_CONV_CHAINS_V5.md` | EDIT (v2.0) |

---

## Верификация

1. `python3 scripts/deploy_and_test.py` → подключение к таблице OK
2. Обновлённый .gs код загружен в Apps Script
3. Меню "НЭП Авто" → v2.0.0
4. "Health Check" → токены OK, Gemini OK
5. "Заполнить карточку товара" → фото HYPERLINK, данные заполнены
6. "Загрузить ключевые фразы" → автосбор → "Запросы" заполнен (~50+ фраз)
7. "Рекламная статистика" → метрики НЕ нулевые
8. "Полный цикл" → 8/8 шагов OK
9. `wb_jam_parser.py` → лист "Джем" заполнен
