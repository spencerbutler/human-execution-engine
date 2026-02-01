# var/oper

This directory holds operator-facing workflow notes and logs.

## SQZ roll (hee-sqz-roll-v1)
A SQZ roll is a ≤5-line summary that converts one UNKNOWN axis into one KNOWN signal using exactly one source artifact.

Artifacts:
- contract: `contracts/hee-sqz-roll-v1.md`
- schema: `schemas/hee/v1/sqz_roll_log.schema.json`
- template: `tools/sqz/sqz-roll.template.txt`

Rule: unknown ≠ negative. If the source is unreachable/unreadable, remain UNKNOWN.
