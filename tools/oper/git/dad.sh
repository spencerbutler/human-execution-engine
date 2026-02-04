#!/usr/bin/env bash
# dad.sh: heuristic detector for automation-churn branches
# Oper-safe: no set -e / pipefail. Default output is k:v. -q is exit-code only.

THRESH="${THRESH:-10}"
PAT="${PAT:-'(regen|generated|format|lint|pre-commit|autofix|chore|workflow|manifest|integrity|lock|deps|bump|vendor|sync)'}"
MAX_BRANCHES="${MAX_BRANCHES:-25}"
QUIET=0

usage() {
  echo "tool=dad status=ERROR error=usage msg='usage: dad.sh [-q] [-h]'" >&2
  return 2
}

while [ $# -gt 0 ]; do
  case "$1" in
    -q) QUIET=1 ;;
    -h|--help) usage; exit $? ;;
    *) usage; exit $? ;;
  esac
  shift
done

git fetch -p >/dev/null 2>&1 || true

# Collect suspicious lines into a temp var (avoid term-killer behavior)
out="$(
  git for-each-ref --format='%(refname:short)' refs/heads 2>/dev/null \
  | rg -v '^main$' 2>/dev/null \
  | while IFS= read -r b; do
      ahead="$(git rev-list --count "main..$b" 2>/dev/null || echo 0)"
      case "$ahead" in (''|*[!0-9]*) ahead=0 ;; esac
      [ "$ahead" -le "$THRESH" ] && continue

      sus="$(git log --format='%s' -n 30 "$b" 2>/dev/null | rg -ic "$PAT" 2>/dev/null || echo 0)"
      case "$sus" in (''|*[!0-9]*) sus=0 ;; esac

      if [ "$sus" -ge 15 ]; then
        printf "tool=dad status=SUSPECT branch=%s ahead=%s suspicious=%s/30\n" "$b" "$ahead" "$sus"
      fi
    done 2>/dev/null \
  | sort -k0,0 2>/dev/null \
  | head -"$MAX_BRANCHES" 2>/dev/null
)"

if [ -n "$out" ]; then
  [ "$QUIET" -eq 1 ] && exit 1
  # Emit summary header + findings
  echo "tool=dad status=SUSPECT findings=1 threshold=$THRESH max_branches=$MAX_BRANCHES"
  echo "$out"
  exit 1
else
  [ "$QUIET" -eq 1 ] && exit 0
  echo "tool=dad status=OK findings=0 threshold=$THRESH max_branches=$MAX_BRANCHES"
  exit 0
fi
