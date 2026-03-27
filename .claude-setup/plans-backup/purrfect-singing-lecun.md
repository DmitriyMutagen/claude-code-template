# План: Модуль генерации ТЗ для инфографики WB + MCP серверы

## Контекст

Проект WB Content Factory уже генерирует названия, описания и характеристики товаров через enrichment pipeline + QA scoring (9.9/10). Теперь нужен **модуль генерации ТЗ для инфографики**, который:
1. Берёт данные из существующего пайплайна (enriched product data, НЭП-профили, сегменты)
2. Применяет методологию из обучения (конверсионные цепочки, намерения/мотивы) и шаблона "тз дизайнеру.docx" + "промпт.docx"
3. Генерирует структурированное ТЗ для каждого слайда инфографики
4. Прогоняет через систему скоринга (аналог wb_qa_multilevel.py)
5. Выход пригоден для генерации через Nano Banana Pro API (kie.ai)

## Что уже есть (НЕ переписываем, переиспользуем)

| Модуль | Путь | Что даёт |
|--------|------|----------|
| `infographic_cgm.py` | `src/infographic/` | Генерация раскадровки 8-12 слайдов по НЭП-профилю |
| `infographic_brief_scorer.py` | `src/infographic/` | Базовый скоринг ТЗ слайда (5 критериев, max 10) |
| `infographic_prompt_builder.py` | `src/infographic/` | Билдер промптов для Nano Banana Pro |
| `infographic_orchestrator.py` | `src/infographic/` | Оркестратор: scorer → prompt → генерация |
| `nano_banana_api.py` | `src/` | API клиент nanobanana.com |
| `nano_banana_generator.py` | `src/` | KIE.ai клиент (nano-banana-2) |
| `nep_analysis/` | `output/` | НЭП-профили по 91 товару + storyboards_all.json |
| `infographic_knowledge_base.md` | `output/nep_analysis/` | База знаний для ТЗ инфографики |
| `тз дизайнеру.docx` | корень | 8-блочный шаблон ТЗ (намерения, мотивы, боли, визуал) |
| `промпт.docx` | корень | Промпт анализа фото: определение намерений и мотивов |

## Что нужно сделать

### Фаза 1: Рефакторинг и усиление ТЗ генератора

**Файл:** `src/infographic/infographic_tz_generator.py` (НОВЫЙ — главный модуль)

Объединяет логику из `тз дизайнеру.docx` (8 секций) + `промпт.docx` (намерения/мотивы) + НЭП-профиль + данные enriched product:

**Структура выходного ТЗ (JSON):**
```
{
  "product_id": "226825123",
  "product_name": "L-глутамин 250г",
  "tz_version": "v1",

  // Блок 1: Контекст (из тз дизайнеру.docx секция 1)
  "context": {
    "category": "Аминокислоты",
    "content_type": "инфографика",
    "intent_chain": "исследовательское → целевое → ситуативное → экономическое",
    "key_phrases": ["BCAA", "восстановление", "синтез белка"],
    "competitor_refs": []
  },

  // Блок 2: Главная логика восприятия (секция 2)
  "perception": {
    "primary_intent": "целевое",
    "primary_motive": "Функциональный",
    "key_emotion": "уверенность",
    "funnel_stage": "уточнение"
  },

  // Блок 3: Вторичные намерения и мотивы (секция 3)
  "secondary": {
    "secondary_intents": ["исследовательское", "ситуативное"],
    "secondary_motives": ["Социальный"],
    "integration_method": "через детализацию состава и факты о применении"
  },

  // Блок 4: Потребности из отзывов (секция 4)
  "review_insights": {
    "positive": ["Хорошо растворяется", "Без побочек"],
    "doubts": ["Малая дозировка", "Не указан полный состав"],
    "content_solution": "Показать крупно дозировку и состав на слайде 2"
  },

  // Блок 5: Боли и барьеры из вопросов (секция 5)
  "pain_points": {
    "typical_questions": ["Какой вкус?", "Сколько порций?"],
    "barrier_type": "непонимание",
    "visual_solution": "Иконка 'Без вкуса', пиктограмма '50 порций'"
  },

  // Блок 6: Семантические акценты (секция 6)
  "semantic_accents": {
    "function_focus": "состав, дозировка, чистый продукт",
    "context_focus": "спорт, восстановление после тренировки",
    "emotion_focus": "уверенность, результат",
    "trust_focus": "GMP, сертификат, сделано в РФ"
  },

  // Блок 7: Визуальные параметры (секция 7)
  "visual_params": {
    "photo_type": "предметная",
    "composition": "центр + выноски",
    "background": "нейтральный",
    "color_scheme": "холодная",
    "additional_elements": ["пиктограммы", "бейджи", "логотип"]
  },

  // Блок 8: Обоснование (секция 8)
  "rationale": {
    "intent_rationale": "...",
    "traffic_correlation": "...",
    "pain_resolution": "...",
    "visual_decisions": "..."
  },

  // СЛАЙДЫ (из CGM + enrichment)
  "slides": [
    {
      "slide_num": 1,
      "type": "hero",
      "intent_served": "исследовательское",
      "motive_served": "Эмоциональный",
      "text_focus": "...",
      "suggested_text": "...",
      "visual_strategy": "...",
      "wb_constraints": {
        "min_font_px": 16,
        "safe_zones": ["left_top", "right_top", "bottom"],
        "max_text_elements": 5
      },
      "nano_banana_hints": {
        "aspect_ratio": "3:4",
        "resolution": "2K",
        "style": "infographic",
        "key_objects": ["банка протеина", "иконки"]
      }
    }
    // ... 8-12 слайдов
  ]
}
```

**Источники данных:**
- `enriched product` из `Processed_01.03.2026` (название, описание, характеристики)
- `nep_analysis/nep_*.json` (НЭП-профили: intent, motive, funnel_stage, gaps)
- `storyboards_all.json` (текущие раскадровки от CGM)
- `docs/knowledge/` (правила WB)
- `docs/lsi_keywords_per_category.json` (LSI для семантических акцентов)
- OpenRouter LLM для заполнения секций 4-5, 8 (отзывы, боли, обоснования)

### Фаза 2: Продвинутый скоринг ТЗ инфографики

**Файл:** `src/infographic/infographic_qa_scorer.py` (НОВЫЙ — замена простого brief_scorer)

10-балльная система по аналогии с `wb_qa_multilevel.py`:

| # | Критерий | Макс | Проверка |
|---|----------|------|----------|
| 1 | Intent Alignment | 1.5 | primary_intent соответствует визуальной стратегии слайдов |
| 2 | Motive Coverage | 1.0 | Все 4 мотива покрыты хотя бы 1 слайдом |
| 3 | Funnel Completeness | 1.5 | Слайды покрывают все этапы воронки (интерес→решение→импульс) |
| 4 | Pain Point Resolution | 1.0 | Боли из отзывов закрыты визуальными решениями |
| 5 | WB Technical Compliance | 1.0 | Формат 3:4, шрифт ≥16px, safe zones, RGB, ≤10MB |
| 6 | Text Quality | 1.0 | Нет оценочных характеристик, нет цен, нет CAPSLOCK, ≤5-7 элементов |
| 7 | Semantic Richness | 1.0 | LSI-ключи встроены в тексты слайдов |
| 8 | Nano Banana Readiness | 0.5 | Промпт-хинты заполнены, aspect_ratio/resolution/style указаны |
| 9 | Slide Diversity | 0.5 | Нет дублирования типов слайдов, ≥6 разных типов |
| 10 | Конверсионная цепочка | 1.0 | Логичная последовательность: hero→details→usage→trust→offer→cta |

**Порог:** 8.5/10 для прохождения.
**AutoFixer:** автоматическая доработка слабых слайдов через LLM (аналог AutoFixer в wb_qa_multilevel.py).

### Фаза 3: Интеграция в пайплайн

**Файл:** `src/infographic/infographic_pipeline.py` (НОВЫЙ — CLI оркестратор)

```
python3 -m src.infographic.infographic_pipeline --all          # все товары
python3 -m src.infographic.infographic_pipeline --product 226825123  # один товар
python3 -m src.infographic.infographic_pipeline --dry-run      # только ТЗ без генерации
```

Пайплайн:
1. Загрузка enriched данных из `output/Processed_*`
2. Загрузка НЭП-профилей из `output/nep_analysis/`
3. Генерация ТЗ через `infographic_tz_generator.py`
4. Скоринг через `infographic_qa_scorer.py` (цикл: score → fix → rescore, max 3 попытки)
5. Экспорт: JSON + XLSX (для ревью) + промпты для Nano Banana

### Фаза 4: Настройка MCP серверов

1. **Context7** — уже подключен как plugin, проверить работоспособность
2. **Serena** — `claude mcp add --transport http serena https://mcp.serena.dev/sse`
3. **Sentry** — `claude mcp add --transport http sentry https://mcp.sentry.dev/sse`

Для Serena и Sentry потребуется OAuth-аутентификация через `/mcp` после добавления.

### Фаза 5: API ключи

- `KIE_API_KEY=50efea7b964e193a6fd115ef01c3d62a` → добавить в `.env`
- Добавить `KIE_API_KEY = os.getenv("KIE_API_KEY", "")` в `config.py`

## Файлы для создания/модификации

| Файл | Действие |
|------|----------|
| `src/infographic/infographic_tz_generator.py` | СОЗДАТЬ — главный генератор ТЗ |
| `src/infographic/infographic_qa_scorer.py` | СОЗДАТЬ — продвинутый скоринг |
| `src/infographic/infographic_pipeline.py` | СОЗДАТЬ — CLI оркестратор |
| `src/infographic/__init__.py` | СОЗДАТЬ — пакет |
| `src/infographic/infographic_cgm.py` | МОДИФИЦИРОВАТЬ — добавить поля из тз дизайнеру.docx |
| `src/infographic/infographic_prompt_builder.py` | МОДИФИЦИРОВАТЬ — улучшить под новую структуру ТЗ |
| `src/config.py` | МОДИФИЦИРОВАТЬ — добавить KIE_API_KEY, NANO_BANANA_API_KEY |
| `.env` | МОДИФИЦИРОВАТЬ — добавить ключи (попросить у пользователя) |

## Переиспользуемые компоненты

- `enrichment_pipeline.py::FileRAG` — для поиска по docs/knowledge/
- `enrichment_pipeline.py::_call_openrouter()` — для LLM-вызовов
- `enrichment_pipeline.py::_extract_json()` — для парсинга JSON из LLM
- `wb_qa_multilevel.py::AutoFixer` — паттерн автофикса
- `config.py` — все API ключи и пути
- `output/nep_analysis/storyboards_all.json` — готовые раскадровки
- `output/nep_analysis/nep_*.json` — НЭП-профили

## Верификация

1. `python3 -m src.infographic.infographic_pipeline --product 226825123 --dry-run` — генерация ТЗ для L-глутамина
2. Проверить JSON-выход: все 8 секций заполнены, слайды ≥8
3. Скоринг ≥8.5/10 для каждого товара
4. Промпты для Nano Banana сформированы и содержат aspect_ratio, resolution, style
5. XLSX-отчёт сохранён в `output/infographics/`
6. Запуск на всех 91 товарах: `--all`
