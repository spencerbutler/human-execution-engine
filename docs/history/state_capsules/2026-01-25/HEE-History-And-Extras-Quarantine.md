# STATE CAPSULE — History + Extras Quarantine (2026-01-25)

## Status

COMPLETED — State capsules demoted to history; non-canonical tooling quarantined; propagation boundaries hardened.

## Canonical Doctrine Anchors

- `docs/doctrine/PLAN_MODE_ENVELOPE.md`
- `docs/doctrine/DISTRIBUTION_BOUNDARIES.md`

## What Changed

### Historical State Capsules

- `docs/STATE_CAPSULES/` relocated to `docs/history/state_capsules/`
- `CURRENT_TASKS.md` explicitly treated as OPTIONAL operator dashboard (non-authoritative)
- References updated across docs/prompts/scripts/CI to the new historical path

### Guide Semantics

- `docs/STATE_CAPSULE_GUIDE.md` updated to remove:
  - “seamless handoff” / control-plane implications
  - “canonical entry point” semantics
- Added explicit Status/Rules block asserting historical-only posture and AUTHZ rules

### Extras Quarantine

- Demo/observability tooling moved under `extras/` (non-canonical)
- Specifically quarantined:
  - `scripts/branch_health_monitor.py` → `extras/observability/branch-health/branch_health_monitor.py`
- Added README in extras scope stating non-authoritative intent and AUTHZ non-impact

### Propagation Hardening

- Confirmed allowlist propagation doctrine:
  - Eligible: `docs/doctrine/`, `prompts/`, and `scripts/` (governance-only when doctrine-backed)
  - NOT eligible: `docs/history/`, `extras/`
- Vendor/attach tooling updated/verified to exclude `history/` content from downstream sync

## Key Decisions Locked In

- State capsules are HISTORICAL working notes only; no control-plane authority.
- No workflow may REQUIRE state capsules for handoff, sequencing, or authorization.
- Authority remains exclusively via explicit chat-line sentinel:
  `AUTHZ: APPROVED_TO_ACT`
- `extras/` is explicitly non-canonical and must not propagate.

## Verification Notes

- `rg` confirms no remaining `docs/STATE_CAPSULES` references.
- `docs/STATE_CAPSULE_GUIDE.md` no longer asserts handoff authority.
- Quarantined branch health script is treated as heuristic/demo tooling, not enforcement.

## Deferred / Next Work

- Consider a lightweight “HISTORICAL_LOGGING” doctrine/module (optional) to reduce future drift.
- If branch health monitoring becomes a supported offering:
  - move into `tooling/` and fix metric correctness (ahead/behind and merge conflict detection)
  - otherwise keep in `extras/` permanently.

## Guidance for Next Chat

- Start in PLAN mode.
- Assume PLAN MODE ENVELOPE is enforced.
- Treat `docs/history/state_capsules/` as context only.
- Do not re-introduce file-based handoff authority.
