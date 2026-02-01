# INIT

Repository initialization prompt.

(Stub to satisfy CI required-docs invariant.)

## Authority Scope Invariants

- Operate within repository-defined authority and scope.
- Do not exceed declared roles, contracts, or plans.
- Prefer minimal diffs; preserve invariants.

## Scope Invariants
- Keep focus; make it hard to lose and intuitive to regain.
- Evidence-first; verify before fix; minimal diffs.

Reference: scripts/hee_git_ops.sh

## Invariants
- Maintain focus and recoverability.
- Evidence-first, minimal diffs.

 scripts/hee_git_ops.sh
BLOCKER: Do not proceed on invariant violations.
