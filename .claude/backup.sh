#!/usr/bin/env bash
# ~/.claude/backup.sh — Smart backup of critical Claude Code files
# Usage: ~/.claude/backup.sh [label]
# Example: ~/.claude/backup.sh "before-major-refactor"

set -euo pipefail

BACKUP_DIR="$HOME/.claude/backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LABEL="${1:-manual}"
BACKUP_NAME="claude-backup-${TIMESTAMP}-${LABEL}"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

mkdir -p "$BACKUP_PATH"

log() { echo "  $1"; }

echo ""
echo "═══════════════════════════════════════"
echo "  Claude Code — Smart Backup"
echo "  Label: $LABEL"
echo "  Path: $BACKUP_PATH"
echo "═══════════════════════════════════════"

# Critical single files
log "Backing up critical files..."
for f in "$HOME/.claude/CLAUDE.md" "$HOME/.claude/settings.json" "$HOME/.claude/settings.local.json"; do
    [ -f "$f" ] && cp "$f" "$BACKUP_PATH/" && log "  ok $(basename $f)"
done

# Critical directories (smart: only .claude config dirs, not plugins/cache)
log "Backing up config directories..."
DIRS=(
    "$HOME/.claude/rules"
    "$HOME/.claude/hooks"
    "$HOME/.claude/gamification"
    "$HOME/.claude/homunculus"
    "$HOME/.claude/sleepless"
)
for d in "${DIRS[@]}"; do
    if [ -d "$d" ]; then
        name=$(basename "$d")
        # Gamification: skip db and cache, keep scripts/configs
        if [ "$name" = "gamification" ]; then
            mkdir -p "$BACKUP_PATH/gamification"
            find "$d" -maxdepth 2 \( -name "*.py" -o -name "*.json" -o -name "*.md" \) \
                ! -name "gamify.db" | while read -r file; do
                rel="${file#$d/}"
                mkdir -p "$BACKUP_PATH/gamification/$(dirname "$rel")"
                cp "$file" "$BACKUP_PATH/gamification/$rel"
            done
            log "  ok gamification (scripts+configs only)"
        else
            cp -r "$d" "$BACKUP_PATH/" 2>/dev/null || true
            log "  ok $name"
        fi
    fi
done

# Memory (only key files, not all decay sessions)
log "Backing up memory..."
mkdir -p "$BACKUP_PATH/memory/permanent" "$BACKUP_PATH/memory/plans" "$BACKUP_PATH/memory/projects"
[ -f "$HOME/.claude/memory/GLOBAL_MEMORY.md" ] && \
    cp "$HOME/.claude/memory/GLOBAL_MEMORY.md" "$BACKUP_PATH/memory/"
[ -d "$HOME/.claude/memory/permanent" ] && \
    cp -r "$HOME/.claude/memory/permanent" "$BACKUP_PATH/memory/"
[ -d "$HOME/.claude/memory/plans" ] && \
    cp -r "$HOME/.claude/memory/plans" "$BACKUP_PATH/memory/" 2>/dev/null || true
[ -d "$HOME/.claude/memory/projects" ] && \
    cp -r "$HOME/.claude/memory/projects" "$BACKUP_PATH/memory/" 2>/dev/null || true
log "  ok memory (GLOBAL + permanent + plans)"

# Custom skills only (not 315MB of all skills)
log "Backing up custom skills..."
mkdir -p "$BACKUP_PATH/skills"
CUSTOM_SKILLS=(
    "growth-coach"
    "org-structure"
    "improver"
    "do-router"
    "daily-review"
    "good-morning"
    "continuous-learning-v2"
    "rfc"
    "tech-radar"
    "mega-research"
    "qa-verifier"
)
for skill in "${CUSTOM_SKILLS[@]}"; do
    skill_path="$HOME/.claude/skills/$skill"
    if [ -d "$skill_path" ]; then
        cp -r "$skill_path" "$BACKUP_PATH/skills/"
        log "  ok skill: $skill"
    fi
done

# Template project
if [ -d "$HOME/Documents/template-project/.claude" ]; then
    log "Backing up template-project..."
    mkdir -p "$BACKUP_PATH/template-project"
    cp -r "$HOME/Documents/template-project/.claude" "$BACKUP_PATH/template-project/"
    [ -f "$HOME/Documents/template-project/CLAUDE.md" ] && \
        cp "$HOME/Documents/template-project/CLAUDE.md" "$BACKUP_PATH/template-project/"
    log "  ok template-project/.claude"
fi

# Create manifest
SIZE_BEFORE_COMPRESS=$(du -sh "$BACKUP_PATH" 2>/dev/null | cut -f1)
cat > "$BACKUP_PATH/MANIFEST.md" << EOF
# Backup Manifest
- **Created**: $TIMESTAMP
- **Label**: $LABEL
- **Size (uncompressed)**: $SIZE_BEFORE_COMPRESS

## Contents
- CLAUDE.md, settings.json, settings.local.json
- rules/
- hooks/
- gamification/ (scripts+configs, no gamify.db)
- memory/ (GLOBAL_MEMORY.md + permanent/ + plans/ + projects/)
- skills/ (custom only)
- template-project/.claude/

## Restore commands
\`\`\`bash
# List backups
~/.claude/restore.sh

# Restore settings only
~/.claude/restore.sh "${BACKUP_NAME}.tar.gz" settings

# Restore GLOBAL_MEMORY only
~/.claude/restore.sh "${BACKUP_NAME}.tar.gz" memory

# Full restore (with confirmation prompt)
~/.claude/restore.sh "${BACKUP_NAME}.tar.gz" all
\`\`\`
EOF

# Compress
log "Compressing..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME" 2>/dev/null
rm -rf "$BACKUP_PATH"  # remove uncompressed

FINAL_SIZE=$(du -sh "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" | cut -f1)

# Keep only last 10 backups
BACKUP_COUNT=$(ls "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 10 ]; then
    ls -t "$BACKUP_DIR"/*.tar.gz | tail -n +11 | xargs rm -f
    log "Cleaned old backups (kept last 10)"
fi

echo ""
echo "BACKUP COMPLETE"
echo "   File: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "   Size: $FINAL_SIZE"
echo "   Keep: last 10 backups max"
echo "═══════════════════════════════════════"
echo ""
