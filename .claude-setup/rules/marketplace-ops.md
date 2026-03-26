# Marketplace Operations Rules (WB / Ozon / YM)

## API Credentials
- **Ozon**: Client ID 2003894
- **Wildberries**: seller 544455 + OOO 4117589, token active
- **Yandex Market**: App "Арагант"

## MCP Servers (use INSTEAD of raw HTTP)
- `marketplace-api` — unified gateway for WB/Ozon/YM (47+ tools)
- `marketai-db` — PostgreSQL read-only analytics

## Safety Rules
1. NEVER update prices/stocks without explicit confirmation
2. Test on 1-3 products before batch operations
3. Always check rate limits before bulk requests
4. Log every API mutation (price change, stock update, card edit)
5. Backup current state before mass updates

## Card Quality Standards (WB/Ozon)
- Title: основной ключ + бренд + характеристика, 60-120 символов
- Description: 1000-2000 символов, SEO-оптимизирован
- Photos: минимум 5, белый фон, инфографика
- Characteristics: ВСЕ обязательные поля заполнены
- Rich content: A+ контент если доступен

## Monitoring Automation
- Ежедневно: проверка остатков, цен конкурентов
- Еженедельно: отзывы без ответа, вопросы без ответа
- Ежемесячно: unit economics по SKU, неликвиды

## AI Response Generation (MarketAI)
- Provider: Polza.ai (DeepSeek V3.2) — primary
- Fallback: Claude CLI → Anthropic API → static template
- Quality: научные ссылки (PubMed), cross-sell, CTA
- Tone: per-rating (5★=благодарность, 1★=решение проблемы)
- Guardrails: запрещённые фразы, медицинские claims
