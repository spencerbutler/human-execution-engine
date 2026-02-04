# tools/oper

Operator-only tools.

Rules:
- Intended for manual, interactive use.
- Must be safe in iteration (avoid pipefail by default; tolerate partial failures).
- Must not modify repo state unless explicitly named/flagged to do so.
