# Agent Prompt 00 — HEE/HEER Specifications Foundation

You are implementing the foundational specifications for the Human Execution Engine (HEE) and Runtime (HEER) standards.

## Objectives
1) Create canonical HEE and HEER specifications as normative documents
2) Establish the conceptual and operational contracts for the ecosystem
3) Ensure specifications are complete, unambiguous, and enforceable

## Constraints
- Follow PROMPTING_RULES.md exactly - security first, no assumptions
- Specifications must be normative (if/and/only if conditions)
- No implementation code - specifications only
- Commit frequently with model disclosure

## Steps

### 1. Create HEE Specification (docs/HEE.md)
**Objective**: Define the conceptual model of human work orchestration

**Requirements**:
- Formal definition with normative properties
- 8 normative properties that qualify a system as HEE
- Clear litmus test for HEE compliance
- Relationship to tick-task and HEER

**Validation**:
- All properties use "MUST", "SHALL", or "if and only if"
- No implementation details
- Complete exclusion list for non-properties

### 2. Create HEER Specification (docs/HEER.md)
**Objective**: Define the operational runtime contract

**Requirements**:
- Formal definition of deterministic execution runtime
- Complete task state machine with legal transitions
- Runtime components: admission, scheduler, journal, adapters
- Determinism and replay requirements

**Validation**:
- State machine transitions are exhaustive
- Event types fully enumerated
- Failure semantics clearly defined
- Compliance test provided

### 3. Cross-Reference Validation
**Objective**: Ensure HEE and HEER specifications are consistent

**Requirements**:
- HEE defines "what", HEER defines "how"
- Clear relationship between conceptual and operational layers
- No contradictions between specifications

**Validation**:
- HEER implements HEE requirements
- Specifications reference each other appropriately
- Compliance tests align

### 4. Commit Specifications
**Objective**: Preserve canonical specifications in git

**Requirements**:
- Separate commits for HEE and HEER
- Model disclosure in all commits
- Clear commit messages indicating canonical status

**Validation**:
- Both files committed to feature branch
- Commit messages follow PROMPTING_RULES.md
- Files are ready for PR review

## Success Criteria
- [ ] docs/HEE.md contains complete normative specification
- [ ] docs/HEER.md contains complete runtime contract
- [ ] Specifications are cross-referenced and consistent
- [ ] All commits include proper model disclosure
- [ ] Files are committed and ready for PR

## Security Validation
- [ ] No shell commands executed
- [ ] No dynamic content generation
- [ ] Specifications contain no implementation code
- [ ] All content validated for security compliance
