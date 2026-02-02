# STATE-CAPSULE: INT-CORE-recover @ 2026-01-26 (America/Chicago)

chat: INT-CORE-recover
purpose: Recover from corrupt status; identify artifacts/PLANs/STASH; consolidate to disk as truth.
artifacts_chat: INT-artifacts

truth_order:

- disk
- git
- chat_claims

known_disk_targets:

- ./docs/doctrine/HEE_SVL.md
- ./docs/specs/HEE_SIGNAL_TAXONOMY.md
- ./docs/specs/HEE_SIGNAL_GLYPH_RINGS.md
- ./rfcs/RFC-0001-HEE-SVL.md

recovery_outputs_required:

- INT-artifacts/RECOVERY_PACKET.md
- INT-artifacts/RECOVERY_STATE_CAPSULE.md
- INT-artifacts/OPERATOR_CHECKLIST.md
- INT-artifacts/LOOP_AUTOPSY.md

stashes_to_carry:

- "SVL silence is operational; not global absence."
- "Naming hardline: incorrect name must not ship (consider INT-Naming -> HEE-Naming)."
- "Doctrine editing rule: if it doesn't do concrete work, cut."
- "Disavow implicit mode/authority language."
- "Contain OPER spew via explicit COG routing contract."
- "Noise-for-signal caution; enemy is gibberish/NaN; eliminate first."
- "AGENT is teacher-student, non-graded; AGENT receives only operationally correct bits."

gates:

- "No claim of execution without disk evidence."
- "No phase advancement without verified file existence/content checks."
- "AGENT does not execute; OPER executes and presents evidence."

---

## VERIFIED DISK INVENTORY (2026-01-26)

### Present

- docs/history/state_capsules/2026-01-26/INT-CORE-recover.md (this file)

### Absent (verified missing at time of recovery)

- docs/doctrine/HEE_SVL.md
- docs/specs/HEE_SIGNAL_TAXONOMY.md
- docs/specs/HEE_SIGNAL_GLYPH_RINGS.md
- rfcs/RFC-0001-HEE-SVL.md

### Notes

- Absence is recorded state, not a failure.
- No doctrine/spec/RFC claims are valid until these paths exist on disk.
