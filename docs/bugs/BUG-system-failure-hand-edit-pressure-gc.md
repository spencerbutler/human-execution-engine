# BUG: System failure pressure — hand-editing risk under CI thrash (gc.sh)

## Severity
P0

## Summary
Operator experienced repeated CI failures in gc-smoke causing pressure to bypass toolchain and hand-edit `scripts/gc.sh`. This is a system failure condition per HEE policy.

## Impact
- Risk of non-auditable changes
- Risk of correctness regression
- Risk of momentum loss due to CI thrash / rework

## Reproduction
1) Open PR checks for the active branch.
2) Observe repeated `gc-smoke` failures with python syntax errors originating from `scripts/gc.sh` heredoc/path quoting.
3) Operator impulse: fix directly in editor due to repeated non-convergent patch attempts.

## Expected
- Deterministic patch workflow converges quickly.
- CI failures are narrow and actionable.
- No need for direct hand editing.

## Actual
- CI failure persisted across multiple patch iterations.
- Evidence/outfile workflow and minimal diffs helped, but GC script brittleness caused repeated thrash.

## Notes / Evidence
- See .hee/evidence/hee-3layer-hardening/ (E20+ evidence shows UI/workflow degradation; latest logs show gc-smoke syntax errors).
