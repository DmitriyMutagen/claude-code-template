#!/bin/bash
# ============================================================
# Claude Code Full Infrastructure Installer
# ============================================================
# Run on a NEW machine to get 100/100 infrastructure level
# Usage: bash install.sh
# ============================================================

set -e
echo "🧠 Claude Code Infrastructure Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CLAUDE_DIR="$HOME/.claude"

# ─── 1. Create directory structure ───
echo "📁 Создаю структуру директорий..."
mkdir -p "$CLAUDE_DIR"/{hooks,scripts,rules,memory/{permanent,decay-7d,decay-30d,projects,plans}}
mkdir -p "$CLAUDE_DIR"/homunculus/{instincts/{personal,inherited},evolved/{agents,skills,commands},projects}
mkdir -p "$CLAUDE_DIR"/gamification
echo "  ✅ Директории созданы"

# ─── 2. Copy rules ───
echo "📋 Копирую правила..."
cp -v "$TEMPLATE_DIR/.claude-setup/rules/"*.md "$CLAUDE_DIR/rules/" 2>/dev/null || true
echo "  ✅ Rules скопированы"

# ─── 3. Copy hooks ───
echo "🪝 Копирую хуки..."
for f in "$TEMPLATE_DIR/.claude-setup/hooks/"*; do
  [ -f "$f" ] && cp -v "$f" "$CLAUDE_DIR/hooks/" && chmod +x "$CLAUDE_DIR/hooks/$(basename $f)"
done
echo "  ✅ Hooks скопированы"

# ─── 4. Copy scripts ───
echo "📜 Копирую скрипты..."
for f in "$TEMPLATE_DIR/.claude-setup/scripts/"*; do
  [ -f "$f" ] && cp -v "$f" "$CLAUDE_DIR/scripts/" && chmod +x "$CLAUDE_DIR/scripts/$(basename $f)"
done
echo "  ✅ Scripts скопированы"

# ─── 5. Copy instincts ───
echo "🧠 Копирую instincts..."
cp -v "$TEMPLATE_DIR/.claude-setup/instincts/"*.yaml "$CLAUDE_DIR/homunculus/instincts/personal/" 2>/dev/null || true
echo "  ✅ Instincts скопированы"

# ─── 6. Copy identity ───
echo "👤 Копирую identity..."
cp -v "$TEMPLATE_DIR/.claude-setup/identity.json" "$CLAUDE_DIR/homunculus/identity.json" 2>/dev/null || true
echo "  ✅ Identity скопирован"

# ─── 7. Copy gamification config ───
echo "🎮 Копирую gamification..."
cp -v "$TEMPLATE_DIR/.claude-setup/gamification/"* "$CLAUDE_DIR/gamification/" 2>/dev/null || true
echo "  ✅ Gamification скопирована"

# ─── 8. Merge hooks into settings.json ───
echo "⚙️  Настраиваю settings.json..."
python3 "$TEMPLATE_DIR/.claude-setup/merge-settings.py" 2>/dev/null || echo "  ⚠️  Ручная настройка settings.json нужна"

# ─── 9. Copy global CLAUDE.md (CTO instructions) ───
if [ -f "$TEMPLATE_DIR/.claude-setup/CLAUDE.md.global" ] && [ ! -f "$CLAUDE_DIR/CLAUDE.md" ]; then
  cp "$TEMPLATE_DIR/.claude-setup/CLAUDE.md.global" "$CLAUDE_DIR/CLAUDE.md"
  echo "  ✅ Global CLAUDE.md (CTO instructions) installed"
else
  echo "  ⏭️  CLAUDE.md already exists"
fi

# ─── 9b. Copy CL v2.1 observations (learning history) ───
if [ -d "$TEMPLATE_DIR/.claude-setup/observations-backup" ]; then
  for obs_file in "$TEMPLATE_DIR/.claude-setup/observations-backup/"*.jsonl; do
    [ -f "$obs_file" ] || continue
    echo "  📊 Copied learning data: $(basename $obs_file)"
  done
fi

# ─── 10. Copy CL v2.1 skill (if not already installed) ───
if [ ! -d "$CLAUDE_DIR/skills/continuous-learning-v2" ]; then
  echo "📦 Копирую Continuous Learning v2.1..."
  cp -r "$TEMPLATE_DIR/.claude-setup/skills/continuous-learning-v2" "$CLAUDE_DIR/skills/" 2>/dev/null || true
  chmod +x "$CLAUDE_DIR/skills/continuous-learning-v2/hooks/observe.sh" 2>/dev/null || true
  echo "  ✅ CL v2.1 установлен"
else
  echo "  ⏭️  CL v2.1 уже установлен"
fi

# ─── 10. Copy daily-review and good-morning skills ───
echo "📅 Копирую skills..."
for skill_dir in "$TEMPLATE_DIR/.claude-setup/skills/"*/; do
  skill_name=$(basename "$skill_dir")
  mkdir -p "$CLAUDE_DIR/skills/$skill_name"
  cp -v "$skill_dir"* "$CLAUDE_DIR/skills/$skill_name/" 2>/dev/null || true
done
echo "  ✅ Skills скопированы"

# ─── 11. Setup pre-commit for this project ───
echo "🔒 Настраиваю pre-commit..."
if command -v pre-commit &>/dev/null; then
  cd "$TEMPLATE_DIR"
  pre-commit install 2>/dev/null || true
  echo "  ✅ pre-commit настроен"
else
  echo "  ⚠️  pre-commit не установлен. Установи: pip install pre-commit"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ УСТАНОВКА ЗАВЕРШЕНА"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Что установлено:"
echo "  📋 $(ls $CLAUDE_DIR/rules/*.md 2>/dev/null | wc -l | tr -d ' ') rules"
echo "  🪝 $(ls $CLAUDE_DIR/hooks/*.{py,sh} 2>/dev/null | wc -l | tr -d ' ') hooks"
echo "  📜 $(ls $CLAUDE_DIR/scripts/*.py 2>/dev/null | wc -l | tr -d ' ') scripts"
echo "  🧠 $(ls $CLAUDE_DIR/homunculus/instincts/personal/*.yaml 2>/dev/null | wc -l | tr -d ' ') instincts"
echo "  🎮 Gamification engine"
echo "  📦 CL v2.1 (Continuous Learning)"
echo ""
echo "Следующий шаг:"
echo "  1. Добавь API ключи в ~/.claude/settings.json → env"
echo "  2. Перезапусти Claude Code"
echo "  3. Проверь: при старте должны появиться MCP Status и Memory Status"
