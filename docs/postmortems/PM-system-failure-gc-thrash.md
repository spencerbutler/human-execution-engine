# Postmortem: System failure risk — GC CI thrash induced hand-edit pressure

## Incident Class
P0 system failure condition (hand-edit temptation)

## What happened
Repeated gc-smoke CI failures created pressure to bypass the auditable patch workflow and hand-edit `scripts/gc.sh` directly.

## Timeline (fill in)
- T0: PR created; initial CI failures identified (HEE Compliance, governance, gc-smoke, etc.)
- T1: Most checks fixed; remaining failures concentrated in gc-smoke
- T2: Multiple patch iterations attempted; failure signature persisted (python heredoc/path quoting)
- T3: Operator reported imminent hand-edit (system failure condition)

## Root cause
GC script brittleness (stringly-typed quoting + heredocs + mixed shell/python) produced repeated non-convergent fixes and persistent failure signatures.

## Contributing factors
- Workflow/UI degradation around evidence E20s increased cognitive load
- GC is a backstop tool but currently has high maintenance cost
- Lack of a single deterministic “GC repair contract” / tests for quoting invariants

## Detection
- CI logs: python SyntaxError `open(/_scripts_all.txt,...)`
- Operator signal: explicit report of imminent hand-edit

## Resolution (fill in)
- Deterministic fix applied via auditable patch/outfiles
- CI returned to green

## Hardening / Prevent recurrence
- Add a unit/smoke test for gc.sh quoting invariants (fail fast)
- Refactor/replace GC to remove heredoc substitution footguns OR retire GC if CBA negative
- Add policy: if gc-smoke fails >N times in PR, auto-open issue + allow temporary skip with explicit waiver pill
- Evidence naming contract: encode hypothesis/result in outfile names

## What did we learn
- Evidence-first + minimal bets works, but only if the subsystem is structurally testable.
- “System failure” is not a feeling; it is a policy-trigger requiring artifacts and urgency.

