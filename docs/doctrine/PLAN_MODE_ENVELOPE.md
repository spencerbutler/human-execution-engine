## PLAN MODE ENVELOPE Doctrine

### Purpose

PLAN MODE ENVELOPE is the control-plane doctrine governing agent behavior during PLAN phase in all HEE workflows. It enforces disciplined planning, explicit authority transitions, and first-class no-op outcomes to prevent accidental mutation and ensure deterministic execution.

### Non-Negotiable Invariants

1. **Authority Separation**: PLAN authority and ACT authority are mutually exclusive domains with explicit transition protocol.

2. **Mutation Prohibition**: No repository mutations permitted in PLAN phase. Read-only operations only.

3. **Transition Atomicity**: PLAN → ACT transition requires exact token match. No partial transitions.

4. **No-Op Validity**: No-op outcomes are first-class results, not failures.

### PLAN Output Contract

**Required Structure**:
- Complete analysis and planning artifacts
- Clear, testable compliance criteria
- Brief rationale for each planned section/component

**Prohibited**:
- Partial plans requiring follow-up questions
- Implementation details without analysis
- Ambiguous success criteria

### No-Op as a First-Class Outcome

**Definition**: No-op is a valid PLAN conclusion when analysis determines no action required.

**Requirements**:
- No-op conclusions must be explicitly stated and justified
- No-op rationale must address original task scope
- No-op outcomes do not require ACT authorization
- No-op documentation must be preserved for audit

**Enforcement**: No-op outcomes are celebrated as efficient resource allocation, not process failure.

### PLAN → ACT Transition (AUTHZ)

**Canonical Sentinel**:
```
AUTHZ: APPROVED_TO_ACT
```

**Authorization Protocol**:
- ACT begins only on exact sentinel: `AUTHZ: APPROVED_TO_ACT`
- Sentinel must be exact match, case-sensitive, no surrounding whitespace

**Allowed Extensions**:
- Additional fields permitted: `scope=...`, `authority=...`
- Example: `AUTHZ: APPROVED_TO_ACT — scope=PLAN MODE ENVELOPE doctrine only — authority=this chat`

**Proposal Requirements**:
- If changes proposed, present exact AUTHZ line for operator response
- If no changes required, explicitly declare no-op outcome

**Explicitly Forbidden**:
- Inference of authorization from similar tokens
- Near-matches or partial matches
- Agent-issued AUTHZ tokens
- Implied or assumed authorization

### Agent Obligations

**During PLAN**:
- Complete information gathering before planning
- Produce reviewable artifacts only
- Accept no-op as valid outcome

**Transition Discipline**:
- Wait for explicit human authorization
- Do not interpret similar tokens as authorization
- Report attempted violations immediately

### Human Obligations

**Review Requirements**:
- Evaluate PLAN artifacts for completeness
- Assess no-op conclusions for validity
- Provide explicit authorization or rejection
- Specify rejection scope if partial

**Authorization Scope**:
- Must include specific scope: `scope=ARTIFACT_NAME`
- May include additional constraints
- Cannot be inferred or assumed

### Failure Conditions

**Critical Failures**:
- Mutation in PLAN phase
- Invalid token acceptance
- Undocumented no-op conclusions

**Recovery Protocol**:
- Critical failures require immediate human intervention
- Unauthorized mutations may be reverted by human decision
- Agent must not auto-revert without explicit instruction

### Relationship to INIT.md and Repo Policy

**INIT.md Integration**:
- INIT.md references this doctrine for PLAN phase governance
- This doctrine provides enforceable structure for INIT.md PLAN requirements
- INIT.md may specify workflow-specific PLAN patterns within this envelope

**Repo Policy Integration**:
- Repo policy enforces doctrine compliance through structure
- Doctrine violations are repo policy violations
- Doctrine updates require repo policy coordination

---

**This doctrine is enforceable by structure alone. Agents must self-check compliance before transition.**

### Rationale

Each section exists because:

- **Purpose**: Defines the doctrine's scope and prevents misinterpretation as style guide
- **Non-Negotiable Invariants**: Creates structural enforcement without requiring tool-specific knowledge
- **PLAN Output Contract**: Ensures planning artifacts are complete and reviewable, preventing partial handoffs
- **No-Op as First-Class Outcome**: Removes stigma from efficient analysis that concludes no action needed
- **PLAN → ACT Transition**: Provides atomic, explicit authority boundary preventing accidental mutations
- **Agent Obligations**: Defines enforceable agent behavior patterns
- **Human Obligations**: Clarifies human responsibilities in the protocol
- **Failure Conditions**: Enables violation detection and recovery
- **Relationship to INIT.md and Repo Policy**: Positions doctrine as canonical reference, not duplicative content

The doctrine enables tool-agnostic enforcement through structural constraints, ensuring consistent PLAN behavior across all HEE workflows while preventing the accidental mutations that have historically caused process failures.
