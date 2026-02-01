# Prompting Rules

## Pager Prevention

All commands must disable pagers (GIT_PAGER=cat, --no-pager) to avoid blocking automation.

This documents pager prevention as required by CI.

## Authority Scope Invariants

- Operate within repository-defined authority and scope.
- Do not exceed declared roles, contracts, or plans.
- Prefer minimal diffs; preserve invariants.
