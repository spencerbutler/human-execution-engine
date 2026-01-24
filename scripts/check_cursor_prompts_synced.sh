#!/usr/bin/env bash
set -euo pipefail

./scripts/sync_cursor_prompts.sh

# Fail if sync changed anything
if ! git diff --quiet -- .cursor/prompts; then
  echo "ERROR: .cursor/prompts is out of sync with prompts/hee"
  echo "Run: ./scripts/sync_cursor_prompts.sh and commit the result."
  git diff -- .cursor/prompts | sed -n '1,200p'
  exit 1
fi

echo "OK: .cursor/prompts is in sync"
