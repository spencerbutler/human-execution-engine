# HEE CI/CD Greenline — Post‑Mortem / Knowledge Base Entry

**Date:** 2026‑01‑26  
**Context:** human-execution-engine (main)  
**Scope:** CI/CD hardening, governance enforcement, and merge‑readiness validation

---

## Executive Summary

A multi‑day CI/CD hardening effort surfaced several failure modes that were not defects in business logic or governance intent, but in *implementation mechanics*—specifically GitHub Actions YAML structure, shell execution boundaries, and incorrect assumptions about how to detect merge conflicts.

The end state is a **fully green pipeline** with:
- deterministic conflict detection,
- pager‑safe automation,
- reduced governance friction,
- and better operator tooling.

This document captures *what broke, why it broke, how it was fixed,* and *what is now considered canon* so this class of failure does not recur.

---

## Initial Symptoms

- Repeated **Conflict Prevention Validation** failures despite:
  - branch rebased onto `origin/main`
  - GitHub reporting `mergeable = true`
- CI jobs reporting “conflicts” while only showing normal diffs
- Pager‑prevention checks producing false positives
- YAML parser errors pointing to single lines with opaque messages:
  - `could not find expected ':'`
  - `while scanning a simple key`

---

## Root Causes (Ordered by Impact)

### 1. Incorrect Conflict Detection Logic

**What happened**  
The original “conflict prevention” check treated *any diff* between the PR branch and `main` as a conflict.

**Why this is wrong**  
A PR is *expected* to differ from `main`. A conflict only exists if Git cannot perform a merge.

**Fix**  
Replace diff‑based logic with an actual merge attempt:
- `git merge --no-commit --no-ff origin/main`
- Fail only if Git reports conflicts
- Abort the merge *only if a merge state exists*

**Canonical rule**  
> Conflict prevention MUST attempt a real merge. Diffs are not conflicts.

---

### 2. Shallow Checkout Causing False Signals

**What happened**  
CI jobs ran merge logic against incomplete history.

**Fix**  
Explicitly require full history:
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

**Canonical rule**  
> Any job that reasons about history, mergeability, or ancestry must use `fetch-depth: 0`.

---

### 3. Shell Code Leaking Outside `run:` Blocks (YAML Structure Violation)

**What happened**  
Shell lines (`echo`, `git`, `if`) were accidentally placed at the *job level* instead of inside a `steps → run: |` block.

This produced errors like:
- `while scanning a simple key`
- `could not find expected ':'`

These are *YAML errors*, not shell errors.

**Why this is insidious**  
- Editors may not highlight the problem
- The error can be triggered by a single misplaced line
- GitHub Actions error messages are indirect

**Fix**  
- Remove stray shell lines from job scope
- Ensure *all* shell lives under `run: |`

**Canonical rule**  
> YAML job scope may only contain YAML. Shell must never appear outside `run:`.

---

### 4. Pager Prevention False Positives

**What happened**  
Legacy grep‑based checks flagged:
- documentation examples
- comments
- the checker script itself

**Fix**  
- Centralize logic in a dedicated script
- Scope checks to executable contexts only
- Accept environment‑level pager prevention (`GIT_PAGER=cat`)

**Canonical rule**  
> Pager prevention is enforced by execution context, not text search.

---

### 5. Commit‑Message Model Disclosure (Low ROI)

**What happened**  
CI enforced that commit subjects include model disclosure.

**Why it failed**  
- Agents cannot reliably maintain this
- Rebasing to reword commits is pure toil
- Provenance already exists in workflow env

**Fix**  
- Remove commit‑subject enforcement
- Rely on `env: MODEL` in workflows

**Canonical rule**  
> Provenance belongs to CI, not commit prose.

---

## Tooling Improvements Introduced

### `scripts/gh_pr_sanity.sh`

A helper script added to provide fast, local truth:
- branch ↔ PR SHA alignment
- check status snapshot
- merge state

This script dramatically reduced guesswork and UI reliance.

**Canonical rule**  
> Prefer local, scriptable truth over UI inspection.

---

## What Made This Hard

- YAML + shell + CI semantics is a hostile combination
- Single‑character indentation errors can invalidate entire workflows
- Error messages are often symptoms, not causes
- Fatigue amplifies all of the above

**Operational takeaway**  
Shell embedded in YAML is the worst.

---

## Final State

- All CI checks **green**
- Merge state **CLEAN**
- Governance guarantees preserved
- False positives eliminated
- Operator tooling improved

The system is strictly better than before.

---

## Recommendations Going Forward

1. Keep conflict detection merge‑based
2. Treat `fetch-depth: 0` as mandatory for governance jobs
3. Never debug YAML without first validating structure
4. Add helper scripts before adding new CI rules
5. Document failure modes immediately while context is fresh

---

## Placement

Recommended location:
```
docs/history/state_capsules/2026-01-26/HEE-CI-CD-Greenline-Postmortem.md
```

This is archival knowledge, not active doctrine.

---

*There is only one football game left this season. This document exists so that none of this has to happen again.*

