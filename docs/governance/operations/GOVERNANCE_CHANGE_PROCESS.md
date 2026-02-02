# GOVERNANCE CHANGE PROCESS (FROZEN / CANONICAL)

**Status:** Frozen and Canonical (Ratified 2026-01-26)
**Authority:** Single Responsible Operator (SRO): Spencer Butler
**Scope:** CI governance rules only (mechanical, enforceable, testable)

## Immutability Notice

This file is **frozen**. Changes are **invalid** unless:

- A change record is added under `docs/governance/operations/changes/`
- `docs/governance/operations/INTEGRITY_SHA256SUMS` is updated
- SRO approval is recorded in the change record

## Evidence-Gated Workflow (Binary)

### 1) Trigger (Concrete Event)

Example triggers:

- CI false positive/negative
- rule bypass discovered
- missing enforcement for a real violation class

### 2) Change Record (Required)

Create: `docs/governance/operations/changes/YYYY-MM-DD_<slug>.md`

It MUST include:

- Trigger
- Evidence
- Proposed change
- Enforcement impact (what now fails/passes)
- Version bump (PATCH/MINOR/MAJOR)
- `Approved-by: Spencer Butler`

### 3) Validation

- Add/adjust tests or fixtures proving the trigger and the fix
- Demonstrate deterministic outcomes

### 4) Enforcement

- Merge only when enforcement is live and binary
- Update integrity hashes

## Emergency Rollback

- Revert to last known-good commit
- File a change record describing trigger + evidence
- Re-apply via standard workflow
