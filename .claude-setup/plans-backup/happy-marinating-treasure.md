# План: Автоматические ключевые слова WB для Настроек

## БЛОКЕР: сначала фикс фото (IMAGE/HYPERLINK)

## Контекст
Функция "Дополнить Настройки по ключевым словам WB" требует ручного ввода ключей.
Нужно: автоматически тянуть топ-запросы с WB API и фильтры по ним.

## Текущий код (строки 922-1083)
- `showKeywordFilterDialog()` — диалог с textarea (8 захардкоженных слов)
- `enrichNastroykiFromWbFilters(keywords[])` — для каждого слова fetchWbFilters_
- `fetchWbFilters_(kw)` — GET search.wb.ru?resultset=filters&query=kw
- WB Suggest API НЕ используется

## План реализации
1. Добавить функцию `fetchWbSuggestions_(baseQuery)` — WB Suggest API
2. Добавить функцию `fetchTopSearchQueries_(nmID)` — получить топ-запросы по товару
3. Переделать диалог: автозаполнение textarea из WB API по выбранному товару
4. Цепочка: товар → ключи → фильтры → Настройки (без ручного ввода)
