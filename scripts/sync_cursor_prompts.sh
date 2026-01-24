#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="prompts/hee"
DST_DIR=".cursor/prompts"

if [ ! -d "$SRC_DIR" ]; then
  echo "ERROR: missing $SRC_DIR (vendored HEE prompts). Run vendoring first."
  exit 1
fi

mkdir -p "$DST_DIR"

# Mirror vendored HEE prompts into Cursor convenience location.
# Exclude docs and any nested .cursor content (should not exist, but belt+suspenders).
rsync -a --delete \
  --exclude "docs/" \
  --exclude ".cursor/" \
  "$SRC_DIR/" "$DST_DIR/"

echo "Synced $SRC_DIR -> $DST_DIR"
