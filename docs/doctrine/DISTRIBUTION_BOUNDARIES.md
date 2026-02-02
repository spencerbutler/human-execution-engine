# Distribution Boundaries

## Purpose

Define what content is eligible for propagation from the canonical HEE repository into other repositories, and what content is explicitly excluded.

## Eligible for Propagation (Canonical Surface)

- `docs/doctrine/` (normative doctrine)
- `prompts/` (canonical prompts)
- `scripts/` (governance enforcement only, when doctrine-backed)
- Any additional directories explicitly designated as canonical in doctrine

## Explicitly Excluded (Do Not Propagate)

- `docs/history/` (historical notes, post-mortems, session logs)
- `extras/` (optional demos, experiments, client-facing showcases)
- Any “working” directories not designated as canonical by doctrine

## Enforcement

Any sync/push tooling must implement an allowlist based on the "Eligible for Propagation" section, not a blanket copy.
