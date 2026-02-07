# GCIC v1 (General Contract Interface Contract)

## Purpose

Defines how contracts are authored, stored, and referenced.

## Rules (normative)

- Contracts MUST live in-repo.
- Contract changes MUST ship via PR.
- Evidence-first: every behavioral claim should have a reproducer + captured output.
- No-clobber is A1 when writing files (default refuse overwrite).

## Interface

- Higher-level contracts inherit GCIC unless explicitly exempted.
