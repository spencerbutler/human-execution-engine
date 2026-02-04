#!/usr/bin/env bash
# is-repo-clean.sh: oper-level cleanliness check (k:v output)
# Definition (minimal):
# - no staged changes
# - no unstaged tracked changes
# - not ahead of origin/main
# Untracked files are allowed (reported, not failing by default).
#
# Exit codes:
# 0 clean, 1 dirty, 2 usage/error
# -q: quiet (exit code only)

QUIET=0

usage() {
  echo "tool=is-repo-clean status=ERROR error=usage msg='usage: is-repo-clean.sh [-q] [-h]'" >&2
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

# Ensure we have origin refs if possible (non-fatal)
git fetch -p >/dev/null 2>&1 || true

staged="$(git diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')"
unstaged="$(git diff --name-only 2>/dev/null | wc -l | tr -d ' ')"

ahead="0"
if git rev-parse --verify -q origin/main >/dev/null 2>&1; then
  ahead="$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)"
fi
case "$ahead" in (''|*[!0-9]*) ahead=0 ;; esac

untracked="$(git ls-files -o --exclude-standard 2>/dev/null | wc -l | tr -d ' ')"

dirty=0
reasons=""

if [ "$staged" -gt 0 ]; then dirty=1; reasons="${reasons} reason=staged"; fi
if [ "$unstaged" -gt 0 ]; then dirty=1; reasons="${reasons} reason=unstaged"; fi
if [ "$ahead" -gt 0 ]; then dirty=1; reasons="${reasons} reason=ahead_of_origin_main"; fi

if [ "$dirty" -eq 0 ]; then
  [ "$QUIET" -eq 1 ] && exit 0
  echo "tool=is-repo-clean status=OK staged=$staged unstaged=$unstaged ahead_of_origin_main=$ahead untracked=$untracked"
  exit 0
else
  [ "$QUIET" -eq 1 ] && exit 1
  echo "tool=is-repo-clean status=DIRTY staged=$staged unstaged=$unstaged ahead_of_origin_main=$ahead untracked=$untracked${reasons}"
  exit 1
fi
