# CI/CD Governance

## Purpose

This document defines the normative CI/CD governance invariants for Human Execution Engine ecosystems.

It is a **normative definition**, not implementation guidance.

Any CI/CD behavior, tooling, or design decision that violates these invariants is considered incorrect for HEE projects.

---

## Scope and Authority

These invariants apply to:

- CI/CD pipeline design and enforcement
- Automated validation and governance checks
- Repository state verification and conflict detection
- Provenance tracking and audit requirements

These invariants do NOT apply to:

- Specific CI platform implementations (GitHub Actions, etc.)
- Workflow YAML syntax or platform-specific features
- Tool-specific command invocations

---

## Non-Negotiable Invariants

A CI/CD system qualifies for HEE governance **if and only if** it satisfies **all** of the following invariants.

### 1. Real Merge Conflict Detection

Conflict detection MUST attempt a real merge against the target branch.
Diff-based heuristics MUST NOT be used for conflict determination.

### 2. Full History for History-Aware CI Logic

Any CI job that reasons about mergeability, ancestry, or history MUST use full repository history.
Shallow clones MUST NOT be used for history-aware governance operations.

### 3. Structural Separation: YAML vs Execution

Workflow orchestration MUST contain only declarative structure.
Executable logic MUST reside in explicit execution steps or external scripts, not structural definitions.

### 4. Scriptable Truth Over UI/Heuristics

Governance checks MUST rely on machine-verifiable truth, not user interface projections or manual inspection heuristics.

### 5. Provenance Belongs to CI

Model and agent provenance SHOULD be recorded by CI execution context, not enforced through commit message conventions.

---

## Explicit Anti-Patterns

HEE CI/CD governance MUST NOT:

- Treat normal branch differences as merge conflicts
- Use shallow history for ancestry-dependent operations
- Mix executable code with declarative workflow structure
- Require manual inspection for automated validation
- Enforce provenance through commit message patterns

---

## Relationship to History

These invariants were extracted from incident response and hardening efforts.
Historical context and implementation examples are documented at:

`docs/history/state_capsules/2026-01-26/HEE-CI-CD-Greenline-Postmortem.md`
