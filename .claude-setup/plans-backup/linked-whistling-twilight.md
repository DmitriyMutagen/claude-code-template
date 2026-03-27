# Plan: OTVETO Deep Reverse Engineering — Chats, Broadcasts & Missing Blocks

## Context
OTVETO токен протух (403). Нужен повторный RE для извлечения:
- Chat module architecture (messages, hints, AI generation)
- Broadcast system (mass messaging)
- Все недостающие блоки которых нет в MarketAI

Предыдущий RE (2026-03-24) дал 257 GraphQL ops, 47 fragments. Но детали чатов, рассылок и edge cases не были извлечены полностью.

## Phase 1: Re-authenticate (нужны credentials)
1. Playwright: открыть `https://app.otveto.ru/login`
2. Ввести email + password
3. Перехватить `Authorization: Bearer <token>` из network
4. Сохранить token в `.env` как `OTVETO_TOKEN`

## Phase 2: GraphQL Deep Extraction
Используя новый токен, запросить:

### Chats (ГЛАВНОЕ)
```graphql
# Список чатов
GetCommonChatCursor { chats { uuid, buyerName, marketplace, lastMessage, unreadCount } }
# Сообщения чата
GetChatMessages(chatUuid) { messages { id, text, isFromSeller, createdAt } }
GetOzonChatMessages(chatUuid) { messages { ... } }
# AI подсказки
GetOzonChatHints(chatUuid) { hints { uuid, text, regenerateCount, messageIds } }
# Генерация AI hint
GenerateOzonChatHint(chatUuid, messageId) → response structure
# Отправка
SendOzonMessageV2(chatUuid, text) → response
SendWbMessage(chatUuid, text) → response
SendYandexMessageV2(chatUuid, text) → response
```

### Broadcasts (рассылки)
```graphql
GetCommonChatBroadcasts { broadcasts { id, type, marketplace, status, sentCount } }
CreateOzonChatBroadcast(input) → structure
CreateWbChatBroadcast(input) → structure
```

### Settings & Config
```graphql
# Chat auto-answer settings
chatAutoAnswer { enabled, mode, confirmMessageSending, confirmHintInserting }
# Treat types (как обрабатываются разные типы)
treatType, answerContainType
```

### Missing blocks to check
- Analytics dashboard data models
- Coworker/team management
- Billing/subscription details
- Feature flags
- A/B test configuration

## Phase 3: Frontend JS Analysis
1. Проверить source maps (`*.js.map`)
2. webcrack на main bundle → модульная структура
3. LinkFinder → скрытые endpoints
4. React DevTools → component tree + state

## Phase 4: AI Prompt Extraction
1. Подать 10 тестовых отзывов через OTVETO
2. Записать AI ответы
3. Систематический анализ паттернов
4. Сравнить с MarketAI промптами

## Phase 5: Documentation
1. Обновить `docs/otveto_full_data_models.md`
2. Создать `docs/otveto_chat_architecture.md`
3. Создать `docs/otveto_broadcast_architecture.md`
4. Обновить feature comparison matrix

## Files to create/modify
- `docs/otveto_chat_architecture.md` — NEW
- `docs/otveto_broadcast_architecture.md` — NEW
- `docs/otveto_full_data_models.md` — UPDATE with chat/broadcast models
- `.env` — ADD `OTVETO_TOKEN`

## Verification
- Все GraphQL операции протестированы и задокументированы
- Chat data models полностью извлечены
- Broadcast flow понятен
- Сравнение MarketAI vs OTVETO обновлено

## BLOCKER: Need OTVETO email + password to re-authenticate
