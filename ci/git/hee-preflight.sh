#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

PROG="${0##*/}"

fail() {
  echo "FAIL: $*" >&2
  exit 2
}

note() { echo "$*"; }

require_cmd() {
  local c="$1"
  command -v "$c" >/dev/null 2>&1 || missing+=("$c")
}

print_dirty_detail() {
  local st
  st="$(git status --porcelain)"
  [[ -z "$st" ]] && return 0

  note "DETAIL:"
  # modified / staged / etc.
  local modified untracked
  modified="$(printf '%s\n' "$st" | awk 'substr($0,1,2) !~ /^\?\?/ {print substr($0,4)}' | sed '/^$/d' | sort -u || true)"
  untracked="$(printf '%s\n' "$st" | awk 'substr($0,1,2) == "??" {print substr($0,4)}' | sed '/^$/d' | sort -u || true)"

  if [[ -n "$modified" ]]; then
    note "  modified:"
    printf '%s\n' "$modified" | sed 's/^/    - /'
  fi
  if [[ -n "$untracked" ]]; then
    note "  untracked:"
    printf '%s\n' "$untracked" | sed 's/^/    - /'
  fi
}

usage() {
  cat <<USAGE
$PROG — HEE repo preflight (hard gate)

Usage:
  ci/git/hee-preflight.sh

Contract:
  - Exit 0 if repo is correct enough to begin work.
  - Exit 2 otherwise, with corrective advice.
USAGE
}

CI_MODE=0
case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
  --ci)
    CI_MODE=1
    ;;
  "")
    ;;
  *)
    fail "unknown argument: ${1}
FIX: run: $PROG --help"
    ;;
esac


# 1) must be inside a git repo
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail "not inside a git repository
FIX: cd into the repo root"

# 2) must not be detached HEAD (except in explicit CI mode)
branch="$(git symbolic-ref --quiet --short HEAD 2>/dev/null || true)"
if [[ -z "$branch" ]]; then
  if [[ "$CI_MODE" -eq 1 ]]; then
    [[ "${GITHUB_ACTIONS:-}" == "true" ]] || fail "detached HEAD is only permitted in CI mode under GitHub Actions
FIX:
  - run without --ci in local development"
    branch="(detached-ci)"
  else
    fail "detached HEAD state
FIX: git checkout <branch>"
  fi
fi

# 3) required tools must exist
missing=()
require_cmd git
require_cmd gh
require_cmd rg
require_cmd python3
if [[ "${#missing[@]}" -ne 0 ]]; then
  fail "missing required tools: ${missing[*]}
FIX: install missing tools and re-run $PROG"
fi

# 4) worktree must be clean
if [[ -n "$(git status --porcelain)" ]]; then
  note "FAIL: dirty worktree"
  print_dirty_detail
  note "FIX:"
  note "  - commit intended changes, or"
  note "  - git restore / git clean to discard"
  exit 2
fi

# 5) main must be correct relative to origin/main (fast-forward only)
git remote get-url origin >/dev/null 2>&1 || fail "missing 'origin' remote
FIX: git remote add origin <url>"

# Fetch origin so comparisons are meaningful
git fetch --prune origin >/dev/null 2>&1 || fail "unable to fetch from origin
FIX: check network/auth and run: git fetch origin"

git show-ref --verify --quiet refs/remotes/origin/main || fail "origin/main not found
FIX: ensure the default branch is 'main' on origin, or update preflight to match your default branch"

git show-ref --verify --quiet refs/heads/main || fail "local 'main' branch not found
FIX:
  git checkout -b main origin/main"

main_sha="$(git rev-parse main)"
origin_main_sha="$(git rev-parse origin/main)"
mb="$(git merge-base main origin/main)"

if [[ "$main_sha" == "$origin_main_sha" ]]; then
  :
elif [[ "$mb" == "$main_sha" ]]; then
  fail "main is behind origin/main
FIX:
  git checkout main
  git pull --ff-only
  git checkout $branch"
elif [[ "$mb" == "$origin_main_sha" ]]; then
  fail "main is ahead of origin/main
FIX:
  - if this is expected, push main: git push origin main
  - otherwise, reset main to origin/main (danger): git checkout main && git reset --hard origin/main"
else
  fail "main and origin/main have diverged
FIX:
  git checkout main
  git pull --ff-only  # if this fails, resolve divergence explicitly"
fi

note "OK: HEE preflight passed — repo is correct"
exit 0
