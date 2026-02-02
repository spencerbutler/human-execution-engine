# HEE Session Entry Invariant

## Authority

HEE doctrine. Non-negotiable.

## Scope

This doctrine governs the start of every work session in this repository.

## Invariants

1) Session entry MUST be correct

- ci/git/hee-preflight.sh returns exit code 0
- CI is passing

1) Broken state blocks all work
Broken state is not "background noise."
Broken state is the task.
1) No progress under broken state
If the repo is incorrect, remediation is the only permitted action.

## Mechanism

- Local hard gate: ci/git/hee-preflight.sh
- CI hard gate: workflow runs ci/git/hee-preflight.sh

## Motto

If it ain't correct, it ain't HEE.
The system eats its own failure modes.
