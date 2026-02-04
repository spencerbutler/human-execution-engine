#!/usr/bin/env bash
# last-touch.sh: list files by last git-touch time (approx repo-wide "ls -lt", but meaningful)
# Usage: last-touch.sh [N]
# Prints: "<iso-date> <sha> <path>"

N="${1:-200}"

git ls-files 2>/dev/null \
| while IFS= read -r f; do
    line="$(git log -1 --format='%ci %h' -- "$f" 2>/dev/null || true)"
    [ -n "$line" ] && printf "%s\t%s\n" "$line" "$f"
  done \
| sort -r 2>/dev/null \
| head -"$N" 2>/dev/null
