# Contributing

This repository is the canonical source of **HEE doctrine**. Contributions must preserve correctness, determinism, and auditability.

## Source of Truth

- Repo rules and conceptual structure: see `README.md`
- Authoritative doctrine: `blueprints/`
- Narrative/rationale only: `docs/` (RFCs live in `docs/rfc/`)

## Non-Negotiables

- **Doctrine MUST validate in strict mode.**
- Doctrine remains **non-terminal** (`result: false`).
- Doctrine identity is deterministic (`seed` + derived `id`, with derivation input recorded).
- **No hand-editing YAML** once tooling exists; prefer patch-based changes and formatted replacements.
- **No shell scripts embedded in YAML.** Put executable logic in repo scripts, not YAML blocks.

## Change Expectations

- Keep diffs minimal and intentional.
- Increment `schema-version` only when meaning changes.
- If you introduce or rename a concept, make the name correct or don’t ship it.
- If strict validation would reject the change, the change is not acceptable.

## PR Shape

A good PR includes:

- the doctrinal change (in `blueprints/`), formatted canonically
- validation evidence (CI output or equivalent)
- narrative justification only if needed (in `docs/` or an RFC)

That’s it.
