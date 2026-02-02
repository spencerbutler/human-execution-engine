# GOVERNANCE VERSIONING (FROZEN / CANONICAL)

**Status:** Frozen and Canonical (Ratified 2026-01-26)
**Authority:** Single Responsible Operator (SRO): Spencer Butler
**Scope:** CI governance rules only (mechanical, enforceable, testable)

## Immutability Notice

This file is **frozen**. Changes are **invalid** unless:

- A change record is added under `docs/governance/operations/changes/`
- `docs/governance/operations/INTEGRITY_SHA256SUMS` is updated
- The process in `docs/governance/operations/GOVERNANCE_CHANGE_PROCESS.md` is followed

## Versioning Scheme

Governance changes are versioned using **MAJOR.MINOR.PATCH**.

### PATCH

- Bugfixes that do not change pass/fail behavior for compliant repos
- Error message improvements only

### MINOR

- Adds immediately enforced checks
- Backward-compatible tightening (existing compliant repos remain compliant)

### MAJOR

- Breaking enforcement changes (previously compliant repos may fail)
- Renames/moves of canonical governance paths
- Required schema changes that invalidate old state

## Deprecation

No shadow modes.
Any removal/replacement must be explicit via change process + version bump + documented migration.
