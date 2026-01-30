# Blueprints

This directory contains the **authoritative blueprint-related doctrine** for the Human Execution Engine (HEE).

The files here define:
- the world-derived primitives HEE relies on,
- the schema for creating blueprints and plans,
- and the validator contract used to reason about correctness.

Nothing in this directory represents operational work.  
Everything here is **standing doctrine**.

---

## Repository Structure (Conceptual)

This repository separates **doctrine**, **instances**, and **operations**.

- `blueprints/`  
  Authoritative doctrine:
  - core-tools
  - blueprint schema
  - validator contract
  - chat header schema

- `docs/` (if present)  
  Narrative documentation, specs, RFCs, explanations.

- Operational directories (e.g. `ci/`, `ops/`, scripts)  
  Enforcement and automation that *consume* doctrine.

- Project artifacts elsewhere  
  Actual blueprints, plans, tasks, and outputs.

Doctrine defines correctness.  
Operations enforce it.  
Instances execute within it.

---

## RFC Naming (Explicit Reservation)

RFC-style identifiers (e.g. `RFC-0001`) are reserved **exclusively** for narrative documents in:

- `docs/rfc/`

RFC documents **may reference** doctrine identities, but RFC numbering **must not** be used as doctrine identity.

---

## Contents

### `core-tools-doctrine.yml`
Defines the canonical set of **core-tools**.

Core-tools are:
- inherent and world-derived,
- immutable in meaning,
- accepted rather than authored.

They form the foundation for priority, result, evidence, existence, and optional cost.

---

### `blueprints/doctrine/blueprint-doctrine.yaml`
Defines the **schema and rules** for creating blueprints, plans, phases, tasks, and items.

This doctrine:
- depends on core-tools,
- defines structural expectations and constraints,
- establishes conventions for ordering, identity, and provenance,
- treats doctrine as non-terminal (`result: false` always).

Instances inherit meaning from this doctrine and do not redeclare dependencies.

---

### `validator-contract-doctrine.yml`
Defines a **descriptive validator contract**.

It specifies:
- inputs and outputs,
- exit codes,
- violation formats and naming schemes,
- open-world vs strict behavior,
- JSON pointer requirements,
- validation order.

It does not prescribe tooling or implementation.

---

### `chat-header-doctrine.yml`
Defines the **schema and rules** for chat headers:
- `chat-class` and `chat-state`,
- defaults that minimize required fields,
- strict vs tolerant validation behavior,
- reserved keys and `x-*` extensions.

It defines structure only; authorization/policy is defined elsewhere.

---

### `hee-doctrine.yml`
Defines the **HEE doctrine index** for this repository:
- a canonical anchor for doctrine discovery,
- explicit doctrine dependencies,
- non-duplication by design.

---

## Invariants

- Doctrine is alive but non-terminal.
- Doctrine `result` must always remain `false`.
- Only doctrine declares dependencies.
- Determinism is preferred wherever possible.
- Unknown keys are tolerated temporarily and must be resolved.

---

## Scope

This directory intentionally excludes:
- executable plans,
- operational blueprints,
- prompts or agent instructions,
- implementation code.

Those belong elsewhere.
