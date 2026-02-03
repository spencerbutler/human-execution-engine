# Plans

Plans are executable sequences used to produce disk evidence.

## Goals

- Convert intent into auditable steps
- Produce evidence on disk (source of truth)
- Remain small, phase-scoped, and reviewable

## What belongs here

- Plan YAML files (`*.plan.yaml`)
- Plan-supporting notes that are non-binding and execution-scoped
- Archived plans for provenance

## What does not belong here

- Binding rules (see `contracts/`)
- Reusable templates (see `blueprints/`)
- Machine validation schemas (see `schemas/`)

## Doctrine candidates

`doctrine_candidates/` contains non-binding candidate doctrine.

- Candidate doctrine is experimental and plan-scoped.
- It exists to be tested via execution and evidence.
- It MUST NOT be treated as binding.
- Promotion path: candidate doctrine graduates only when backed by evidence and enforced by contract and/or validated by schema.

## Directory layout

- `active/` — currently executing plans
- `archive/` — closed plans retained for provenance
- `doctrine_candidates/` — non-binding candidates being tested
