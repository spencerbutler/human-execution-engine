# HEE PR Doctrine

## Authority
This doctrine governs pull-request workflow and review discipline for HEE repositories.
Authority is limited to PR-scoped operational rules and evidence requirements.
No implicit authority is claimed beyond the PR boundary.

## Scope
Applies to:
- Branch → PR creation
- Review intake and response
- CI/run status interpretation and gating
- Merge criteria and post-merge verification

Does not apply to:
- Feature design decisions outside the PR diff
- Human performance management
- External org policy

## Core Invariants
- Pushed branch ≠ PR. A PR exists only after explicit creation.
- PR status must be evidenced by GitHub artifacts (PR number/URL, checks, reviews).
- CI signals are authoritative only as reported by the CI system for that commit/PR.
- Review responses must be scoped to the specific comment; no unsolicited scope expansion.
- No “green” claim without evidence: passing checks (or explicitly waived) for the merge commit.
- Merge must be followed by a post-merge verification of default branch state.

## Operational Gates
- Merge is allowed only when required checks are passing or explicitly waived with rationale.
- Any failing required check blocks merge until resolved or waived.

## Non-Goals
- This doctrine does not guarantee correctness; it guarantees disciplined evidence and gating.
- This doctrine does not define implementation details of CI configuration.
