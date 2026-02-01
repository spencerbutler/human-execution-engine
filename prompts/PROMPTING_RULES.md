# Prompting Rules

## Pager Prevention

All commands must disable pagers (GIT_PAGER=cat, --no-pager) to avoid blocking automation.

This documents pager prevention as required by CI.

## Authority Scope Invariants

- Operate within repository-defined authority and scope.
- Do not exceed declared roles, contracts, or plans.
- Prefer minimal diffs; preserve invariants.

## Scope Invariants
- Keep focus; make it hard to lose and intuitive to regain.
- Evidence-first; verify before fix; minimal diffs.

## Invariants
- Maintain focus and recoverability.
- Evidence-first, minimal diffs.

scripts/hee_git_ops.sh
BLOCKER: Stop on invariant violations.
