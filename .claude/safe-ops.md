# Safe Operations — Backup Before Critical Changes (ОБЯЗАТЕЛЬНО)

## Правило
Перед ЛЮБЫМ из следующих действий — СНАЧАЛА бэкап:
- Переписывание CLAUDE.md (>50% изменений)
- Изменение settings.json (хуки, MCP, permissions)
- Массовое обновление rules/ (>3 файлов)
- Переписывание engine.py или config.json геймификации
- Обновление growth-coach SKILL.md
- Любая операция с флагом --force или деструктивная

## Команда бэкапа
```bash
~/.claude/backup.sh "описание-что-меняем"
```

## Примеры
```bash
~/.claude/backup.sh "before-settings-change"
~/.claude/backup.sh "before-growth-coach-rewrite"
~/.claude/backup.sh "before-gamification-update"
~/.claude/backup.sh "before-rules-overhaul"
```

## Восстановление
```bash
~/.claude/restore.sh                              # список доступных бэкапов
~/.claude/restore.sh "2026-03-27" settings        # восстановить только settings
~/.claude/restore.sh "2026-03-27" memory          # только GLOBAL_MEMORY
~/.claude/restore.sh "2026-03-27" all             # полное восстановление (с подтверждением)
```

## Хранение
- Последние 10 бэкапов (авто-ротация)
- Папка: ~/.claude/backups/
- Формат: claude-backup-YYYY-MM-DD_HH-MM-SS-label.tar.gz
