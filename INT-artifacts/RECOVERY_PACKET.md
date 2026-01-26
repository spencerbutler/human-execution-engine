# RECOVERY_PACKET — INT-CORE-recover (2026-01-26)

## Authority
Operator-owned recovery packet. Disk is truth.

## Purpose
Recover from corrupt status across chats and narrative claims. Consolidate to disk with verifiable evidence.

## Truth Order
1. disk
2. git
3. chat_claims

## Current Ground Truth
### Present
- docs/history/state_capsules/2026-01-26/INT-CORE-recover.md

### Absent (verified missing at time of recovery)
- docs/doctrine/HEE_SVL.md
- docs/specs/HEE_SIGNAL_TAXONOMY.md
- docs/specs/HEE_SIGNAL_GLYPH_RINGS.md
- rfcs/RFC-0001-HEE-SVL.md

## Required Outputs (this packet tracks them)
- INT-artifacts/RECOVERY_PACKET.md (this file)
- INT-artifacts/RECOVERY_STATE_CAPSULE.md
- INT-artifacts/OPERATOR_CHECKLIST.md
- INT-artifacts/LOOP_AUTOPSY.md

## Operational Gates
- No claim of execution without disk evidence.
- No phase advancement without verified file existence/content checks.
- AGENT does not execute; operator executes and presents evidence.

## Next Actions (Minimal / Correct)
1. Run OPERATOR_CHECKLIST and paste output into the canonical chat log.
2. Commit the capsule + these INT-artifacts outputs as a single recovery commit.
3. Only then: create/repair doctrine/spec/RFC files that are currently absent.
