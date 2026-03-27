#!/usr/bin/env bash
# ~/.claude/restore.sh — Restore from backup
# Usage: ~/.claude/restore.sh [backup_file_or_pattern] [component]
# Components: all, settings, rules, gamification, memory, skills

BACKUP_DIR="$HOME/.claude/backups"

if [ -z "${1:-}" ]; then
    echo ""
    echo "Available backups:"
    echo ""
    ls -lt "$BACKUP_DIR"/*.tar.gz 2>/dev/null | awk '{
        n = split($NF, parts, "/")
        fname = parts[n]
        printf "  %s  %s  %s  %s\n", NR".", $6, $7, fname
    }' | head -10
    echo ""
    echo "Usage: ~/.claude/restore.sh <backup.tar.gz|pattern> [component]"
    echo ""
    echo "Components:"
    echo "  settings     — settings.json + settings.local.json + CLAUDE.md"
    echo "  rules        — rules/"
    echo "  gamification — gamification/"
    echo "  memory       — GLOBAL_MEMORY.md + permanent/"
    echo "  skills       — custom skills"
    echo "  all          — full restore (with confirmation)"
    echo ""
    exit 0
fi

BACKUP_FILE="$1"
COMPONENT="${2:-all}"

# Resolve file path
if [ ! -f "$BACKUP_FILE" ]; then
    FOUND=$(ls "$BACKUP_DIR"/*${BACKUP_FILE}*.tar.gz 2>/dev/null | sort -t_ -k1,1 -r | head -1)
    if [ -n "$FOUND" ]; then
        BACKUP_FILE="$FOUND"
        echo "Found: $BACKUP_FILE"
    else
        echo "Backup not found: $1"
        echo "Run ~/.claude/restore.sh without args to list available backups"
        exit 1
    fi
fi

TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "Extracting $BACKUP_FILE..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"
EXTRACTED=$(ls "$TEMP_DIR" | head -1)
SRC="$TEMP_DIR/$EXTRACTED"

echo "Restoring: $COMPONENT"
echo ""

case "$COMPONENT" in
    settings)
        [ -f "$SRC/settings.json" ] && cp "$SRC/settings.json" ~/.claude/ && echo "  ok settings.json"
        [ -f "$SRC/settings.local.json" ] && cp "$SRC/settings.local.json" ~/.claude/ && echo "  ok settings.local.json"
        [ -f "$SRC/CLAUDE.md" ] && cp "$SRC/CLAUDE.md" ~/.claude/ && echo "  ok CLAUDE.md"
        ;;
    rules)
        [ -d "$SRC/rules" ] && cp -r "$SRC/rules" ~/.claude/ && echo "  ok rules/"
        ;;
    gamification)
        [ -d "$SRC/gamification" ] && cp -r "$SRC/gamification" ~/.claude/ && echo "  ok gamification/"
        ;;
    memory)
        [ -f "$SRC/memory/GLOBAL_MEMORY.md" ] && \
            cp "$SRC/memory/GLOBAL_MEMORY.md" ~/.claude/memory/ && echo "  ok GLOBAL_MEMORY.md"
        [ -d "$SRC/memory/permanent" ] && \
            cp -r "$SRC/memory/permanent" ~/.claude/memory/ && echo "  ok memory/permanent/"
        [ -d "$SRC/memory/plans" ] && \
            cp -r "$SRC/memory/plans" ~/.claude/memory/ && echo "  ok memory/plans/"
        [ -d "$SRC/memory/projects" ] && \
            cp -r "$SRC/memory/projects" ~/.claude/memory/ && echo "  ok memory/projects/"
        ;;
    skills)
        if [ -d "$SRC/skills" ]; then
            for skill_dir in "$SRC/skills"/*/; do
                skill_name=$(basename "$skill_dir")
                cp -r "$skill_dir" ~/.claude/skills/ && echo "  ok skill: $skill_name"
            done
        fi
        ;;
    all)
        echo "WARNING: Full restore — existing files will be overwritten"
        printf "Continue? [y/N] "
        read -r confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            # Restore file by file to avoid overwriting unrelated things
            [ -f "$SRC/CLAUDE.md" ] && cp "$SRC/CLAUDE.md" ~/.claude/ && echo "  ok CLAUDE.md"
            [ -f "$SRC/settings.json" ] && cp "$SRC/settings.json" ~/.claude/ && echo "  ok settings.json"
            [ -f "$SRC/settings.local.json" ] && cp "$SRC/settings.local.json" ~/.claude/ && echo "  ok settings.local.json"
            [ -d "$SRC/rules" ] && cp -r "$SRC/rules" ~/.claude/ && echo "  ok rules/"
            [ -d "$SRC/hooks" ] && cp -r "$SRC/hooks" ~/.claude/ && echo "  ok hooks/"
            [ -d "$SRC/gamification" ] && cp -r "$SRC/gamification" ~/.claude/ && echo "  ok gamification/"
            [ -d "$SRC/homunculus" ] && cp -r "$SRC/homunculus" ~/.claude/ && echo "  ok homunculus/"
            [ -d "$SRC/sleepless" ] && cp -r "$SRC/sleepless" ~/.claude/ && echo "  ok sleepless/"
            if [ -f "$SRC/memory/GLOBAL_MEMORY.md" ]; then
                cp "$SRC/memory/GLOBAL_MEMORY.md" ~/.claude/memory/ && echo "  ok GLOBAL_MEMORY.md"
            fi
            [ -d "$SRC/memory/permanent" ] && cp -r "$SRC/memory/permanent" ~/.claude/memory/ && echo "  ok memory/permanent/"
            [ -d "$SRC/memory/plans" ] && cp -r "$SRC/memory/plans" ~/.claude/memory/ 2>/dev/null && echo "  ok memory/plans/"
            [ -d "$SRC/memory/projects" ] && cp -r "$SRC/memory/projects" ~/.claude/memory/ 2>/dev/null && echo "  ok memory/projects/"
            if [ -d "$SRC/skills" ]; then
                for skill_dir in "$SRC/skills"/*/; do
                    skill_name=$(basename "$skill_dir")
                    cp -r "$skill_dir" ~/.claude/skills/ && echo "  ok skill: $skill_name"
                done
            fi
            echo ""
            echo "Full restore complete"
        else
            echo "Cancelled"
        fi
        ;;
    *)
        echo "Unknown component: $COMPONENT"
        echo "Valid: all, settings, rules, gamification, memory, skills"
        exit 1
        ;;
esac

echo ""
echo "Done. Source: $BACKUP_FILE"
echo ""
