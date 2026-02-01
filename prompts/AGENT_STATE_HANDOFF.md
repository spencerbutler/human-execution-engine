# AGENT STATE HANDOFF

## Authority Scope Invariants
- Operate within repository-defined authority and scope.
- Do not exceed declared roles, contracts, or plans.
- Prefer minimal diffs; preserve invariants.

## Scope Invariants
- Keep focus; make it hard to lose and intuitive to regain.
- If uncertain, stop and gather evidence before changing behavior.
- Maintain clean worktree; branch->PR; verify before merge.

## Handoff Format
- Current branch + PR link
- What just changed (1-3 bullets)
- What is failing / passing (CI summary)
- Next exact command to run
- Evidence file pointers (.hee/evidence/...)

## Invariants
- Maintain focus and recoverability.
- Evidence-first, minimal diffs.
