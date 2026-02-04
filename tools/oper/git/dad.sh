#!/usr/bin/env bash
# dad.sh: detect branches that look like automation churn (heuristic)
# Oper-iteration safe: no errexit/pipefail; tolerate partial failures.

THRESH="${THRESH:-10}"
PAT="${PAT:-'(regen|generated|format|lint|pre-commit|autofix|chore|workflow|manifest|integrity|lock|deps|bump|vendor|sync)'}"
MAX_BRANCHES="${MAX_BRANCHES:-25}"

git fetch -p >/dev/null 2>&1 || true

git for-each-ref --format='%(refname:short)' refs/heads 2>/dev/null \
| rg -v '^main$' 2>/dev/null \
| while IFS= read -r b; do
    ahead="$(git rev-list --count "main..$b" 2>/dev/null || echo 0)"
    case "$ahead" in (''|*[!0-9]*) ahead=0 ;; esac
    [ "$ahead" -le "$THRESH" ] && continue

    sus="$(git log --format='%s' -n 30 "$b" 2>/dev/null | rg -ic "$PAT" 2>/dev/null || echo 0)"
    case "$sus" in (''|*[!0-9]*) sus=0 ;; esac

    if [ "$sus" -ge 15 ]; then
      printf "%-40s ahead=%4s suspicious=%2s/30\n" "$b" "$ahead" "$sus"
    fi
  done 2>/dev/null \
| sort -k2,2nr 2>/dev/null \
| head -"$MAX_BRANCHES" 2>/dev/null
