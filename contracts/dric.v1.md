# DRIC v1 (Design–Relay Interface Contract)

## Purpose

Separates design output from relay execution.

## Rules (normative)

- Design produces one pasteable block (header + pill + prompt), no execution steps.
- Relay executes and reports evidence, does not redesign.
- Referee posture: mark 🟥/🟨/🟩, halt on 🟥 until resolved.
- Output should be terminal-readable and evidence should be file-backed.
