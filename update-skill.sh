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
cp "$SCRIPT_DIR/references/"*.md                 "$DEST/references/"

echo "Skill updated: $DEST"
echo "New session required for changes to take effect."
