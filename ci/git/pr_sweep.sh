#!/usr/bin/env bash
set -euo pipefail

# Create PRs for pushed branches (OPER-friendly).
#
# Defaults:
# - base: main
# - prefixes: feature fix rescue docs
#
# Requires:
# - gh CLI installed and authenticated
# - origin remote
#
# Usage:
#   ci/git/pr_sweep.sh                # list only
#   ci/git/pr_sweep.sh --create       # create PRs
#   ci/git/pr_sweep.sh --base main --create
#

BASE="main"
CREATE="0"
PREFIXES=("feature/" "fix/" "rescue/" "docs/")

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base) BASE="$2"; shift 2 ;;
    --create) CREATE="1"; shift ;;
    --prefix)
      # allow repeated --prefix flags
      PREFIXES+=("$2")
      shift 2
      ;;
    -h|--help)
      sed -n '1,50p' "$0"
      exit 0
      ;;
    *)
      echo "ERROR: unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not found" >&2
  exit 2
fi

gh auth status >/dev/null 2>&1 || {
  echo "ERROR: gh is not authenticated (run: gh auth login)" >&2
  exit 2
}

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "ERROR: not in a git repo" >&2
  exit 2
}

git fetch origin --prune >/dev/null 2>&1 || true

matches_prefix() {
  local b="$1"
  for p in "${PREFIXES[@]}"; do
    [[ "$b" == "$p"* ]] && return 0
  done
  return 1
}

ahead_of_base() {
  local b="$1"
  # returns count of commits ahead of base
  git rev-list --count "origin/${BASE}..origin/${b}" 2>/dev/null || echo "0"
}

has_open_pr() {
  local b="$1"
  # 0 if none, >0 if exists
  gh pr list --head "$b" --state open --json number --jq 'length' 2>/dev/null || echo "0"
}

title_for_branch() {
  local b="$1"
  # light normalization: prefix: rest
  if [[ "$b" == *"/"* ]]; then
    local pre="${b%%/*}"
    local rest="${b#*/}"
    echo "${pre}: ${rest}"
  else
    echo "PR: ${b}"
  fi
}

body_for_branch() {
  local b="$1"
  cat <<BODY
Auto-created PR for branch: \`${b}\`

- Base: \`${BASE}\`
- Class: $( [[ "$b" == rescue/* ]] && echo "rescue" || echo "normal" )

Notes:
- Please edit title/body as needed.
BODY
}

REMOTE_BRANCHES="$(git for-each-ref --format='%(refname:short)' refs/remotes/origin/ | sed 's%^origin/%%')"

NEEDS=()
while IFS= read -r b; do
  [[ -z "$b" ]] && continue
  [[ "$b" == "$BASE" ]] && continue
  matches_prefix "$b" || continue

  ahead="$(ahead_of_base "$b")"
  [[ "$ahead" -gt 0 ]] || continue

  prcount="$(has_open_pr "$b")"
  [[ "$prcount" -eq 0 ]] || continue

  NEEDS+=("$b")
done <<< "$REMOTE_BRANCHES"

if [[ "${#NEEDS[@]}" -eq 0 ]]; then
  echo "No branches found needing PRs (base=${BASE})."
  exit 0
fi

echo "Branches needing PRs (base=${BASE}):"
for b in "${NEEDS[@]}"; do
  echo " - $b (ahead=$(ahead_of_base "$b"))"
done

if [[ "$CREATE" != "1" ]]; then
  echo
  echo "Dry-run only. Re-run with: ci/git/pr_sweep.sh --create"
  exit 0
fi

echo
for b in "${NEEDS[@]}"; do
  t="$(title_for_branch "$b")"
  echo "Creating PR: $b"
  gh pr create \
    --head "$b" \
    --base "$BASE" \
      --title "$t" \
      --body "$(body_for_branch "$b")"
  done

  echo
  echo "Done."
  exit 0
