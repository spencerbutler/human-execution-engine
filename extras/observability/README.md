# Observability (Extras)

## Status
OPTIONAL / NON-CANONICAL / LOCAL-ONLY

This directory contains optional demo and observability tooling (e.g., dashboards, visualizations, experimental monitors).

## Rules
- Nothing in `extras/` is required for HEE governance.
- Nothing in `extras/` is used as a control-plane mechanism.
- `extras/` MUST NOT be propagated into other repos by any "push/sync" tooling.
- If any component here becomes core governance enforcement, it must be relocated to canonical locations and documented:
  - Doctrine: `docs/doctrine/`
  - Prompts: `prompts/`
  - Enforcement scripts: `scripts/` (with doctrine references)

## Intent
`extras/` exists to support demos, experimentation, and client-facing artifacts without polluting the canonical HEE distribution surface.
