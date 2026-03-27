# План: Лист "Семантика" + умный матчинг ключевых слов к товарам

## Контекст
Текущая функция `enrichNastroykiFromWbFilters()` использует WB Suggest API, который возвращает 10-20 generic подсказок. У пользователя есть семантическое ядро из 10,844 ключей (3,848 релевантных) в `bionovacia_full_semantic_core.json`. Нужно загрузить их в лист "Семантика", привязать к товарам и использовать для обогащения Настроек.

## Архитектура

```
bionovacia_full_semantic_core.json (10,844 ключей)
    ↓ Python: upload_semantics.py
    ↓ Фильтрация по релевантным категориям (3,848)
    ↓ Матчинг к товарам из Артикулов (по title/характеристикам)
    ↓
Лист "Семантика" в Google Sheets
    [Запрос | Частотность | Категория | Релевантные nmID]
    ↓
GS: кнопка "Подобрать из Семантики" в диалоге
    → fetchKeywordsFromSemantics_(nmId)
    → enrichNastroykiFromWbFilters(keywords)
```

---

## Шаг 1: Python скрипт `scripts/upload_semantics.py`

**Задачи:**
1. Загрузить `bionovacia_full_semantic_core.json`
2. Отфильтровать по релевантным категориям (Протеин, БАДы, Креатины, Гейнеры, Аминокислоты, Жиросжигатели, Комплексные пищевые добавки)
3. Прочитать товары из листа "Артикулы" (nmID, vendorCode, brand)
4. Для каждого товара — получить карточку WB (title, subjectName, characteristics) через Content API
5. Матчинг: для каждого ключевого слова проверить, подходит ли оно к товару (substring match по title/characteristics/subjectName)
6. Создать/обновить лист "Семантика" с колонками:
   - A: Запрос
   - B: Частотность
   - C: Категория
   - D: Релевантные nmID (через запятую)
7. Сортировать по частотности (убывание)

**Файлы для чтения:**
- `/Users/Dmitrij/Documents/агенты/wb_content_factory/keywords/bionovacia_full_semantic_core.json`
- Google Sheets API через gspread (лист Артикулы)
- WB Content API для получения title/characteristics

**SA ключ:** `/Users/Dmitrij/Documents/Orchestrator/_archive/агенты/wb_content_factory/google_service_account.json`

---

## Шаг 2: GS функция `getOrCreateSemanticsSheet_(ss)`

В файле `scripts/НЭП_Loader_AppScript.gs`:
- Создать лист "Семантика" если не существует
- Заголовки: `['Запрос', 'Частотность', 'Категория', 'Релевантные nmID']`
- Стиль: синий header `#1a73e8`, frozen row 1
- Ширины колонок: A=300, B=100, C=150, D=300

---

## Шаг 3: GS функция `fetchKeywordsFromSemantics_(nmId)`

- Читает лист "Семантика"
- Фильтрует строки где колонка D содержит указанный nmId
- Возвращает массив ключевых слов (колонка A), отсортированных по частотности (колонка B)
- Если лист пустой или нет матчей — fallback на текущий `fetchTopSearchQueries_(nmId)`

---

## Шаг 4: Обновить диалог `showKeywordFilterDialog()`

Добавить вторую кнопку **"Подобрать из Семантики"** рядом с "Собрать ключевые слова":
- При клике вызывает `fetchKeywordsFromSemantics_(nmId)`
- Заполняет textarea ключевыми словами из листа Семантика
- Показывает количество найденных ключей

Текущая кнопка "Собрать ключевые слова" (WB Suggest) остаётся как fallback.

---

## Шаг 5: Деплой

1. Запустить `python3 scripts/upload_semantics.py` для загрузки семантики
2. `clasp push` обновлённого GS в оригинальный скрипт (ID: `1AHizC7cODRH9if6C-G2oM8qJ0DySA6c2C_J6KJRS2EvIrgbq3IkMCQKS`)

---

## Файлы для изменения
- `scripts/upload_semantics.py` — **НОВЫЙ** (Python, загрузка семантики)
- `scripts/НЭП_Loader_AppScript.gs` — изменить:
  - Добавить `getOrCreateSemanticsSheet_(ss)` (~20 строк)
  - Добавить `fetchKeywordsFromSemantics_(nmId)` (~30 строк)
  - Обновить `showKeywordFilterDialog()` — добавить кнопку "Из Семантики"

## Проверка
1. Запустить `upload_semantics.py` → убедиться что лист "Семантика" создан с 3800+ строками
2. Открыть таблицу → меню "Дополнить Настройки" → выбрать товар → кнопка "Из Семантики" → textarea заполнится ключами
3. Нажать "Получить фильтры" → Настройки дополнятся
