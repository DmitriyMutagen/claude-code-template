# SEO Automation Rules

## Scope
Автоматизация SEO для 3-4 сайтов: bio-stm.ru (WordPress), SoulWay (Tilda), самописные.

## SEO Stack
- **Yandex.Webmaster API** — индексация, позиции, ошибки
- **Yandex.Wordstat** — ключевые слова, частотность
- **Google Search Console API** — позиции, клики, CTR
- **Google Analytics 4** — трафик, конверсии
- **Ahrefs/Serpstat API** — бэклинки, конкуренты (если подключены)

## Automation Pipeline
1. **Keyword Research**: Wordstat API → извлечь частотность → кластеризация → приоритизация
2. **Content Generation**: ключевые слова → Content Factory → статьи с научным RAG
3. **Publishing**: WordPress REST API → публикация → schema markup → internal linking
4. **Indexing**: Yandex.Webmaster IndexNow → Google Indexing API → проверка через день
5. **Monitoring**: позиции по ключевикам weekly → отчёт в Telegram
6. **Optimization**: страницы с CTR < 3% → переписать meta title/description

## WordPress Integration
- WP REST API для публикации контента
- Yoast SEO API для meta tags
- Rank Math API (альтернатива Yoast)
- WP-CLI для batch-операций

## Quality Standards
- Каждая статья: минимум 1500 слов
- H1 содержит основной ключ
- Meta description 150-160 символов
- Alt-теги на всех изображениях
- Schema markup (Article, FAQ, HowTo)
- Internal links: минимум 3 на статью

## Monitoring Alerts (Telegram)
- Позиция упала > 10 мест → alert
- Новая ошибка в Webmaster → alert
- Страница деиндексирована → alert
- Трафик упал > 20% week-over-week → alert
