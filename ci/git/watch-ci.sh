#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

PROG="${0##*/}"

usage() {
  cat <<USAGE
$PROG — tail -f latest GitHub Actions run for a branch

Usage:
  ci/git/watch-ci.sh
  ci/git/watch-ci.sh --branch <name>

Behavior:
  - Defaults to current branch.
  - Watches the most recent run on that branch.
  - Fails with corrective advice if prerequisites are missing.
USAGE
}

branch=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch) branch="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "FAIL: unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

command -v gh >/dev/null 2>&1 || { echo "FAIL: missing 'gh' (GitHub CLI)
FIX: install gh and authenticate (gh auth login)" >&2; exit 2; }

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "FAIL: not inside a git repository
FIX: cd into the repo root" >&2; exit 2; }

if [[ -z "$branch" ]]; then
  branch="$(git symbolic-ref --quiet --short HEAD 2>/dev/null || true)"
  [[ -n "$branch" ]] || { echo "FAIL: detached HEAD state
FIX: git checkout <branch> OR pass --branch <name>" >&2; exit 2; }
fi

run_id="$(gh run list --branch "$branch" --limit 1 --json databaseId --jq '.[0].databaseId')"
if [[ -z "$run_id" || "$run_id" == "null" ]]; then
  echo "FAIL: no workflow runs found for branch: $branch" >&2
  echo "FIX:" >&2
  echo "  - push a commit to trigger CI, or" >&2
  echo "  - check workflows are enabled for this repo" >&2
  exit 2
fi

echo "Watching latest run for branch: $branch (run_id=$run_id)"
gh run watch "$run_id"
