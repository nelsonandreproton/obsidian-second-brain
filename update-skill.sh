#!/usr/bin/env bash
# update-skill.sh
# Syncs the skill to the Claude Code skills folder after git pull.
# Usage: ./update-skill.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/.claude/skills/obsidian-second-brain"

mkdir -p "$DEST/assets/templates"
mkdir -p "$DEST/references"

cp "$SCRIPT_DIR/SKILL.md"                        "$DEST/SKILL.md"
cp "$SCRIPT_DIR/assets/templates/"*.md           "$DEST/assets/templates/"
cp "$SCRIPT_DIR/assets/settings.json.example"    "$DEST/assets/settings.json.example"
cp "$SCRIPT_DIR/references/"*.md                 "$DEST/references/"

echo "Skill updated: $DEST"
echo ""
echo "Hooks (optional):"
echo "  Global:  cp $DEST/assets/settings.json.example ~/.claude/settings.json"
echo "  Project: cp $DEST/assets/settings.json.example /path/to/project/.claude/settings.json"
echo ""
echo "New session required for changes to take effect."
