#!/usr/bin/env bash
set -euo pipefail

echo "== local branch =="
git rev-parse --abbrev-ref HEAD
git --no-pager log -1 --oneline --decorate

echo
echo "== PR checks (current branch PR) =="
gh pr view --json mergeStateStatus,statusCheckRollup,headRefName,headRefOid --jq '
{
  branch: .headRefName,
  head: .headRefOid,
  merge_state: .mergeStateStatus,
  checks: (.statusCheckRollup | map({name: .name, status: .status, conclusion: .conclusion}))
}
'
