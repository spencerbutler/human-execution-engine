# Commit Types and Versioning (HEE Standard)

This document defines (1) commit message conventions and (2) how changes map to Semantic Versioning (SemVer).

## Goals

- Make commit intent obvious during review.
- Keep release versions meaningful (versions track behavior/contract changes, not churn).
- Support conventional-commit tooling without forcing it.

---

## Commit Message Format

Use **Conventional Commits**:

```shell
<type>(<optional-scope>): <imperative summary>
```

Examples:

- docs(history): add CI/CD greenline post-mortem
- fix(ci): correct merge-readiness check abort behavior
- feat(cli): add `hee validate` subcommand
- refactor(scripts): simplify pager-prevention checker

### Types (Allowed)

- **feat**: New user-facing capability (backward compatible)
- **fix**: Bug fix (backward compatible)
- **docs**: Documentation only (no behavior change)
- **test**: Tests only
- **refactor**: Code change with no behavior change
- **perf**: Performance improvement (no contract change)
- **build**: Build system / dependencies
- **ci**: CI configuration and workflows
- **chore**: Maintenance tasks (formatting, cleanup, repo hygiene)
- **revert**: Reverts a prior commit

Scopes are optional but encouraged when they add clarity (e.g., `docs(history`, `ci`, `scripts`, `doctrine`).

---

## SemVer Policy

HEE uses SemVer strictly for **public behavior and public contracts**.

### Version bump rules

- **MAJOR (X.0.0)** when you introduce a **breaking change**
  - Removes/renames public APIs
  - Changes required configuration formats incompatibly
  - Changes documented guarantees/contract in a way that breaks consumers

- **MINOR (0.Y.0)** when you add a **new backward-compatible feature**
  - New commands/flags/endpoints that do not break existing users

- **PATCH (0.0.Z)** for **backward-compatible bug fixes**
  - Fixes incorrect behavior without changing contract

- **NO VERSION BUMP** for changes that do not affect public behavior/contract
  - docs, tests, refactors, CI-only changes, formatting, comments

### Important: docs do not bump versions

Docs-only commits (including runbooks, post-mortems, architecture notes) do **not** change SemVer.
Use `docs:` and do not trigger releases for docs-only changes.

---

## Conventional Commits → Release Automation (Recommended Mapping)

If using semantic-release or similar, use this mapping:

- **feat:** → MINOR
- **fix:** → PATCH
- **BREAKING CHANGE** footer or `!` in type/scope → MAJOR
- **docs/test/refactor/perf/build/ci/chore** → no release (unless paired with breaking footer)

---

## Breaking Changes (How to Declare)

Either:

- `feat!: ...` or `fix!: ...`

Or include a footer:
BREAKING CHANGE: `<what broke and migration notes>`

Example:
feat!(cli): rename `hee run` to `hee exec`

BREAKING CHANGE: `hee run` removed. Use `hee exec`. Update scripts accordingly.

---

## Examples (Common Scenarios)

### Adding a post-mortem / knowledge base entry

Commit:

- docs(history): add CI/CD greenline post-mortem

SemVer:

- No bump

### Fixing a CI merge-readiness validator

Commit:

- ci: fix conflict prevention to detect real merge conflicts

SemVer:

- No bump (unless it changes a public runtime contract; CI-only generally does not)

### Fixing a runtime bug

Commit:

- fix(core): handle empty config without crash

SemVer:

- PATCH

### Adding a new CLI command

Commit:

- feat(cli): add `hee doctor` command

SemVer:

- MINOR

---

## House Rules (HEE-specific)

- Prefer **truthful provenance** in CI (workflow env, run logs) over commit-message ceremony.
- Keep SemVer signals high-quality: versions reflect user-facing behavior/contract, not internal churn.
- When in doubt:
  - If users/scripts would need to change → breaking → MAJOR
  - If users get a new capability without changing anything → MINOR
  - If behavior is corrected without changing contract → PATCH
  - Otherwise → no bump
