# Phase 3: 3D Labels + Data Connectors + Document Engine

## Context
Phase 2 завершён: 4,930 ингредиентов, 10 страниц, JWT auth, role dashboards, interactive graph, 139 тестов. Дмитрий хочет: (1) генерацию этикеток + 3D рендер на банках, (2) ВСЕ возможные источники данных подключены, (3) генерацию ВСЕЙ документации — от ТУ до патентов и отчётов Сколково. Всё на русском, по ГОСТам.

## Plan: 3 параллельных workstream'а

---

### WS1: 3D Label Rendering + Product Studio (~6 дней)

**1.1** Конвертация OBJ → GLB (0.5 дня)
- `scripts/convert_obj_to_glb.sh` — obj2gltf + Draco compression
- Вход: `~/Yandex.Disk.../Банки/3D/Протеин 2.7/SoulWayProtein2.7.obj` (99MB)
- Выход: `frontend/public/models/jar-2700ml.glb` (<10MB)

**1.2** Процедурные банки 6 размеров (1 день)
- `frontend/components/3d/JarGeometry.tsx` — параметрический цилиндр + крышка
- `frontend/components/3d/jarConfigs.ts` — 7 конфигов (0.1L–5L)
- `frontend/components/3d/ProductViewer.tsx` — OrbitControls, освещение, Environment map

**1.3** Label Generator (бэкенд) (2 дня)
- `src/services/label_generator.py` — Pillow: бренд, название, nutrition facts, состав, предупреждения, штрихкод
- `src/services/nutrition_facts_renderer.py` — таблица по ТР ТС 022/2011
- `src/api/routes/label_studio.py` — `POST /api/v1/labels/generate`, `GET /api/v1/labels/{id}/preview`
- Шрифты: PT Sans/PT Serif (русская типографика)
- Выход: PNG 300dpi (печать) + 72dpi (3D текстура)

**1.4** Текстура на 3D банку (1 день)
- `frontend/components/3d/LabelTexture.tsx` — загрузка PNG, UV mapping на цилиндр
- `frontend/app/(dashboard)/product-studio/page.tsx` — 3 панели: рецептура | 3D | свойства

**1.5** Reverse Engineering (2 дня)
- `src/services/label_ocr_service.py` — Tesseract OCR (RU+EN)
- `src/services/recipe_extractor.py` — NLP парсинг состава → matching с базой 4930 ингр
- `src/api/routes/reverse_engineering.py` — `POST /api/v1/reverse/label` (фото → рецептура → анализ → улучшения)

---

### WS2: Все Data Connectors (~10 дней)

**2.1** Base Scraper (1 день)
- `src/connectors/base_scraper.py` — httpx + rotating headers + rate limit + proxy (SOCKS5)

**2.2** iHerb Scraper (2 дня)
- `src/connectors/iherb_scraper.py` — парсинг 50K+ продуктов, Supplement Facts
- `scripts/harvest/harvest_iherb.py`

**2.3** ГРЛС Минздрав (1.5 дня)
- `src/connectors/grls_client.py` — реестр зарегистрированных БАД РФ
- `scripts/harvest/harvest_grls.py`

**2.4** Examine.com (1.5 дня)
- `src/connectors/examine_scraper.py` — 400+ добавок с research grades A-F
- `scripts/harvest/harvest_examine.py`

**2.5** EFSA API (1 день)
- `src/connectors/efsa_client.py` — EU health claims, novel food, safe intake levels

**2.6** WB/Ozon supplements (1 день)
- `src/connectors/marketplace_supplements.py` — парсинг составов из карточек товаров
- Использует marketplace-api MCP (WB seller 544455, Ozon Client 2003894)

**2.7** EU Novel Food + ConsumerLab (1 день)
- `src/connectors/eu_novel_food_client.py`
- `src/connectors/consumerlab_scraper.py`

**2.8** Connector Registry + API (1 день)
- `src/services/connector_registry.py` — статус, last sync, data counts
- `src/api/routes/connectors.py` — `GET /api/v1/connectors/status`, `POST /api/v1/connectors/{name}/sync`

---

### WS3: Document Generation Engine (~12 дней) ← КРИТИЧНЫЙ

**3.1** Рефакторинг core (1 день)
- `src/services/document_generator.py` — strategy pattern
- `src/services/generators/base.py` — `BaseDocumentGenerator`: collect_data → render_html → convert_to_format → validate

**3.2** Format Converters (1 день)
- `src/services/format_converters.py`:
  - `HTMLToPDFConverter` — WeasyPrint, русская типографика, A4
  - `HTMLToDOCXConverter` — python-docx
  - `DataToXLSXConverter` — openpyxl

**3.3** ГОСТ стили (0.5 дня)
- `src/services/gost_styles.py` — Times New Roman 14pt, поля 20/10/20/10мм, ГОСТ Р 7.0.97-2016
- `templates/styles/gost_base.css`

**3.4** Нормативные документы (4 дня)
- `src/services/generators/tu_generator.py` — ТУ (улучшение существующего)
- `src/services/generators/ti_generator.py` + `templates/ti_template.html` — ТИ
- `src/services/generators/label_generator.py` — Этикетка документ (не PNG)
- `src/services/generators/haccp_generator.py` + `templates/haccp_template.html` — ХАССП
- `src/services/generators/sgr_generator.py` + `templates/sgr_template.html` — СГР заявление
- `src/services/generators/test_protocol_generator.py` — Протокол испытаний
- `src/services/generators/raw_material_spec_generator.py` — Спецификация на сырьё

**3.5** Патентная документация (2 дня)
- `src/services/generators/patent_generator.py` — формат ФИПС
- `templates/patent/` — заявка, описание, формула, реферат, поиск prior art
- Интеграция с science-api MCP для поиска аналогов в PubMed/OpenAlex

**3.6** Отчётность Сколково (1.5 дня)
- `src/services/generators/skolkovo_tech_generator.py` — техническое описание
- `src/services/generators/niokr_generator.py` — отчёт НИОКР
- `src/services/generators/financial_model_generator.py` — unit economics XLSX + roadmap

**3.7** Batch generation + version control (1 день)
- `POST /api/v1/documents/generate-package` — все документы за 1 вызов → ZIP
- Версионирование: parent_document_id, auto-increment version

**3.8** Frontend документы (1 день)
- `frontend/app/(dashboard)/documents/[id]/page.tsx` — preview HTML, download PDF/DOCX
- Кнопки генерации по типам, выбор формата

---

### Новые зависимости

**Backend (pyproject.toml):**
```
weasyprint>=60.0    # HTML→PDF русская типографика
Pillow>=10.0.0      # Label image generation
pytesseract>=0.3.10 # OCR reverse engineering
```

**Frontend (package.json):**
Уже установлены: @react-three/fiber, drei, postprocessing, three

---

### Порядок выполнения (параллельные агенты)

**Волна 1** (дни 1-3): WS3.1-3.3 (doc foundation) ‖ WS2.1 (base scraper) ‖ WS1.1-1.2 (3D jars)
**Волна 2** (дни 4-8): WS3.4 (7 doc generators) ‖ WS2.2-2.5 (connectors) ‖ WS1.3 (label engine)
**Волна 3** (дни 9-12): WS3.5-3.6 (patents+skolkovo) ‖ WS2.6-2.8 (remaining) ‖ WS1.4-1.5 (3D+reverse)
**Волна 4** (дни 13-14): WS3.7-3.8 (batch+frontend) ‖ тесты

---

### Критические файлы для модификации
- `src/api/routes/documents.py` — рефакторинг в service layer (600+ строк)
- `src/services/template_service.py` — расширение конвертерами
- `src/connectors/dsld_client.py` — паттерн для новых коннекторов
- `frontend/components/3d/MoleculeScene.tsx` — паттерн R3F
- `src/models/document.py` — новые DocumentType для патентов/Сколково

### Верификация
1. `pytest tests/ -v` — все существующие + новые тесты
2. `cd frontend && npx next build` — билд фронта с новыми 3D/document pages
3. E2E: Playwright тест полного цикла рецептура → label → 3D → документы
4. Smoke: `POST /api/v1/documents/generate-package` → скачать ZIP с 7+ документами
5. Reverse: загрузить фото этикетки → получить распознанную рецептуру
