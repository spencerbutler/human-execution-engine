# Contracts

Contracts define binding rules for behavior and boundaries across the repo.

## What belongs here

- Governance rules (MUST/SHALL)
- Interface and boundary constraints
- Lane definitions (which contract governs which interaction)

## What does not belong here

- Step-by-step execution procedures (see `plans/`)
- Reusable templates and structural patterns (see `blueprints/`)
- Machine validation schemas (see `schemas/`)

## Lanes

A lane is an interaction governed by a specific contract.
Roles do not change; the active contract determines behavior.

Current lanes:

- Design–Relay lane → governed by DRIC
- GPT–Oper Outfile lane → governed by Outfile Evidence Contract

If work is in a lane’s scope, that lane’s contract is authoritative.

## Core contracts

- DRIC (Design–Relay Interface Contract): governs Design ↔ Relay separation and Agent-facing relay behavior.
- Outfile Evidence Contract: governs GPT ↔ Oper evidence/outfile generation (command emission allowed only here).
- Trilateral Roles Contract: governs GPT ↔ Oper ↔ Agent boundaries and allowed speech/authority.
