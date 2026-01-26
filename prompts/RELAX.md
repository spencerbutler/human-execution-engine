# RELAX Prompt

## Authority

Canonical authority: HEE doctrine and repository governance rules.

## Scope

This prompt governs behavior **only when RELAX is explicitly invoked**.

## Invariants

When RELAX is invoked:
- Do not ask clarifying questions unless absolutely blocking.
- Produce concrete, pasteable shell heredocs/scripts that write artifacts to disk.
- Keep changes minimal and reversible.
- Report only disk-evidence facts (files written, paths, sizes, git status).
- Stop after delivering the requested artifacts.
