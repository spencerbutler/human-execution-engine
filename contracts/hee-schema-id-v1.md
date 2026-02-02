# hee-schema-id-v1

## Problem

Branch-churn and domain drift in schema `$id`/`$ref` reduces portability and makes evidence trails brittle.

## Non-goal

- No "vars" inside JSON Schema (`$id` / `$ref` do not support env expansion).

## Rule set (source-of-truth on disk)

1) **Canonical `$id` never encodes branch state.**
2) Prefer **relative `$ref`** within `schemas/` whenever possible.
3) If a locator is needed, publishing tooling may generate **pinned locators** (tag/SHA), without changing canonical source.

## Canonical vs locator

- Canonical ID: stable name (doctrine identity)
- Locator: where to fetch (distribution detail)

## Allowed locator patterns (publish-time only)

- `https://raw.githubusercontent.com/<org>/<repo>/<SHA>/schemas/...`
- `https://raw.githubusercontent.com/<org>/<repo>/refs/tags/<tag>/schemas/...`

## Evidence / guardrails

- No mass rewrite without:
  - scan outfile (file -> $id/$ref)
  - patch emitter output
  - verification run evidence
