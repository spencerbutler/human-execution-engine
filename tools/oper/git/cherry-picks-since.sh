#!/usr/bin/env bash
# cherry-picks-since.sh: list commits that look like cherry-picks since a base ref/sha
# Matches the standard -x trailer: "cherry picked from commit ..."

if [ "${1:-}" = "" ]; then
  echo "usage: $0 <base-ref-or-sha> [<range-tip>]" >&2
  exit 2
fi

BASE="$1"
TIP="${2:-HEAD}"

git log --grep='cherry picked from commit' \
  --format='%h %ci %an %s' \
  "${BASE}..${TIP}" 2>/dev/null || true
