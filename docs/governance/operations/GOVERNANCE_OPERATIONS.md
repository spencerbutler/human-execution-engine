# GOVERNANCE OPERATIONS (FROZEN / CANONICAL)

**Status:** Frozen and Canonical (Ratified 2026-01-26)
**Authority:** Single Responsible Operator (SRO): Spencer Butler
**Scope:** CI governance rules only (mechanical, enforceable, testable)

## Immutability Notice

This file is **frozen**. Changes are **invalid** unless:

- A change record is added under `docs/governance/operations/changes/`
- `docs/governance/operations/INTEGRITY_SHA256SUMS` is updated
- The process in `docs/governance/operations/GOVERNANCE_CHANGE_PROCESS.md` is followed

## Purpose

Established normative framework for ongoing operation, evolution, and versioning of CI governance rules.
Defines mechanical processes for governance rule lifecycle management while maintaining strict scope boundaries.

## Authority Model

- **Single Responsible Operator (SRO):** Spencer Butler
- **Model:** Explicit operator sovereignty (no committees / multi-party approval)
- **Scope:** CI governance rules only (mechanical, enforceable, testable)

## Scope Boundaries

Included:

- CI governance rule lifecycle, versioning, enforcement mechanics
- `ci/governance/*` components and CI pipeline integration

Explicitly excluded:

- HEE doctrine evolution, human compliance processes
- Social/organizational governance, violation tracking systems
- Compliance monitoring beyond CI enforcement

## Core Invariants

1. **No Aspirational Governance** — rules cannot require non-existent approval bodies.
2. **Enforcement Binary** — rules either enforce immediately or do not exist.
3. **Reactive Evolution Only** — changes only in response to concrete triggers, never hypothetical.
