# Postmortem: patching sting and terminal reset (2026-02-02)

## Summary

We incurred significant operator cost due to repeated patch application failures, including terminal and UI resets.
The primary problem was patch tooling interface ambiguity and fragile patch transport.

Outcome: hardened patch tooling and established file based patch workflow.

## Impact

- multiple failed patch attempts (corrupt patch)
- terminal reset at least once
- delayed CI stabilization work
- increased cognitive load and drift risk

## What happened

1. Attempted to apply multi file patch payloads.
2. Patch content was occasionally polluted mid line due to paste collisions.
3. A frequent failure mode appeared: error: corrupt patch at line N.
4. One key instance was caused by incorrect hunk header counts.
   - the @@ header claimed more new side lines than were present
   - git rejected the patch as malformed

## Root causes

- Patch transport was not consistently file based.
- Tooling interface was underspecified.
  - apply-var-patch is a wrapper for patch-apply
  - patch-apply performs normalization and validation that differ from naive git apply assumptions
- Lack of standardized branch guard increased wrong branch risk.

## Fixes implemented

- tools/git/patch-apply: allow VAR to reference a patch file path
- branch guard function hee_ensure_branch established for mdshell usage

## Preventive measures

- Mandate file based patches.
  - patches written to /tmp/*.patch
  - apply using VAR=/tmp/foo.patch tools/git/apply-var-patch with optional --check
- Mandate branch guard at top of every mdshell.
- Document diagnosis commands for corrupt patch failures.

## Evidence patterns

- show patch with line numbers
  - nl -ba /tmp/foo.patch | sed -n "1,120p"
- show tool debug
  - python3 tools/git/patch-apply --debug --file /tmp/foo.patch --check
- show target file header for anchor
  - nl -ba .github/workflows/FILE.yaml | sed -n "1,80p"

## What we learned

- corrupt patch usually indicates syntax error, not context mismatch
- small file based patches preserve operator momentum
- wrapper clarity is correctness work
