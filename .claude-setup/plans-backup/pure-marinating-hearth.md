# Фаза 4: Graph Data Modeling — ETL в Neo4j + GraphRAG

## Контекст
Neo4j установлен через brew и запущен (порт 7474/7687). Драйвер `neo4j` v6.1.0 в venv.
Вся инфраструктура кода уже существует (`neo4j_schema_builder.py`, `neo4j_etl_pipeline.py`, `neo4j_schema_init.cypher`), но данные пока только в JSON-фолбеке (`graph_db_mock.json`). Нужно залить в живой Neo4j и создать GraphRAG-запросы.

## Шаг 1: Подключение к Neo4j

**Файлы:** `.env`, `src/config.py`, `src/neo4j_schema_builder.py`

1. Сменить дефолтный пароль Neo4j через `cypher-shell` (neo4j/neo4j → neo4j/password123)
2. Добавить в `.env`:
   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=password123
   ```
3. Добавить в `src/config.py` константы `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
4. Обновить `neo4j_schema_builder.py` — использовать `config.NEO4J_*` вместо `os.getenv()`
5. Проверить: `python3 -m src.neo4j_schema_builder --test`

## Шаг 2: ETL — загрузка данных в Neo4j

### 2a. Базовый импорт (существующий код)
Запуск `python3 -m src.neo4j_schema_builder` — загрузит:
- 142 Ozon товара (CSV)
- 134 Yandex товара (XLSX)
- 59 pipeline results (сегменты + ключи)
- 10K Ozon keywords (XLSX)

### 2b. CGM-данные (новый код в `neo4j_schema_builder.py`)
- **Новая функция `read_cgm_results()`** — читает `output/cgm_matrix/cgm_*.json`
- **Новая функция `upsert_cgm_result()`** — обогащает Segment ноды CGM-свойствами (conversion_chain, pains, fears, seo_title)
- **Новый тип ноды `Block`** — 8 блоков контента на сегмент:
  ```
  (Segment)-[:HAS_BLOCK]->(Block {id, block_number, type, headline, body_text, visual_description})
  ```
- Маппинг CGM файлов на product_id через имя файла (`cgm_omega_90.json` → `omega_90`)
- Добавить constraint и index в `neo4j_schema_init.cypher`

### 2c. WB семантическое ядро (новый код)
- **Новая функция `read_wb_semantic_core()`** — `keywords/bionovacia_semantic_core.json` (1564 ключей с volume/cr_cart/cr_order)
- Создание Keyword нод с `source="WB"`, связь `(Keyword)-[:FOUND_ON]->(Marketplace {name: "WB"})`
- 300K keywords — НЕ грузим все, только фильтрованные по категориям (5-10K)

### 2d. CLI флаги
Добавить `--cgm` и `--wb-keywords` в argparse

## Шаг 3: GraphRAG-модуль

**Новый файл:** `src/graph_rag.py` (~250 строк)

```python
class GraphRAGClient:
    def connect(self) -> bool
    def get_product_context(self, article: str) -> Dict  # полный контекст SKU
    def get_competitor_keywords(self, article: str) -> List[Dict]  # ключи конкурентов
    def get_category_insights(self, category: str) -> Dict  # аналитика категории
    def format_for_llm(self, context: Dict) -> str  # текст для промпта
    def format_for_dify(self, context: Dict) -> Dict[str, str]  # переменные для Dify
```

**Ключевые Cypher-запросы:**
- Product → Segments → Keywords (полный обход)
- Competitor overlap (продукты с общими ключами)
- Category top keywords (по popularity/conversion)

**CLI:** `python3 -m src.graph_rag --article omega_90`

## Шаг 4: Интеграция в pipeline

- `src/cgm_segmentator.py` — опция загрузки товаров из Neo4j вместо JSON
- `src/local_pipeline.py` — опциональное обогащение промпта GraphRAG-контекстом (graceful fallback если Neo4j недоступен)

## Шаг 5: Верификация

1. Cypher-запросы для проверки статистики (nodes/edges counts)
2. `python3 -m src.graph_rag --article omega_90` — полный контекст
3. Тесты: `tests/test_graph_rag.py` (6 кейсов) + `tests/test_neo4j.py` (4 кейса)

## Файлы для изменения

| Файл | Действие | Объём |
|------|----------|-------|
| `.env` | +3 строки | NEO4J config |
| `src/config.py` | +4 строки | NEO4J constants |
| `src/neo4j_schema_builder.py` | +120 строк | CGM/WB readers + upsert + CLI |
| `src/graph_rag.py` | **новый** ~250 строк | GraphRAGClient |
| `deploy/neo4j_schema_init.cypher` | +10 строк | Block constraint/index |
| `tests/test_graph_rag.py` | **новый** ~100 строк | 6 тестов |
