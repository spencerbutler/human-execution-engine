# Agent Prompt 02 — HEER Runtime Implementation

You are implementing the core HEER runtime as the reference implementation for deterministic human work orchestration.

## Objectives
1) Build complete HEER runtime with all required components
2) Ensure deterministic execution under replay conditions
3) Create comprehensive test suites for runtime validation
4) Provide reference implementation for ecosystem compliance

## Constraints
- Follow PROMPTING_RULES.md exactly - security validation mandatory
- Runtime must be deterministic under replay given same event stream
- All HEER contract requirements must be implemented
- Event sourcing must enable full state reconstruction

## Steps

### 1. Core Runtime Implementation (src/heer/runtime.py)
**Objective**: Implement the main HEER runtime orchestrator

**Requirements**:
- Task state machine with complete transition validation
- Event journaling for all state changes
- Deterministic replay capability
- Runtime policy enforcement

**Validation**:
- All legal state transitions enforced
- Events form complete audit trail
- Replay produces identical state sequences
- Policy constraints prevent invalid operations

### 2. Task Graph Manager (src/heer/task_graph.py)
**Objective**: Implement dependency graph management with cycle detection

**Requirements**:
- DAG construction and validation
- Automatic dependency readiness computation
- Cycle detection and rejection
- Downstream propagation of completion/failure

**Validation**:
- Cycles rejected at creation time
- Dependency readiness computed deterministically
- Completion/failure propagates correctly
- Graph operations are thread-safe

### 3. Admission Controller (src/heer/admission.py)
**Objective**: Implement policy-based task admission control

**Requirements**:
- Policy evaluation for runnable task admission
- Runtime constraint validation
- Admission decision recording as events
- Re-evaluation on policy/runtime changes

**Validation**:
- Admission decisions are deterministic
- Policy changes trigger re-evaluation
- Admission events recorded for audit
- Performance constraints respected

### 4. Deterministic Scheduler (src/heer/scheduler.py)
**Objective**: Implement deterministic task scheduling with capacity limits

**Requirements**:
- Single active task enforcement (default concurrency = 1)
- Deterministic tie-breaking rules
- Context switching cost modeling
- Scheduler state preservation in events

**Validation**:
- Maximum one active task when concurrency = 1
- Scheduling decisions reproducible under replay
- Tie-breaking rules prevent non-determinism
- Context switching tracked and auditable

### 5. Event Journal (src/heer/journal.py)
**Objective**: Implement immutable event store with replay capability

**Requirements**:
- Complete event schema implementation
- Event ordering and consistency guarantees
- State reconstruction from event streams
- Query interfaces for event inspection

**Validation**:
- All event types from HEER spec implemented
- Events are immutable once recorded
- State reconstruction is deterministic
- Query performance scales appropriately

### 6. State Machine (src/heer/state_machine.py)
**Objective**: Implement task state machine with transition validation

**Requirements**:
- Complete state definitions (PENDING, RUNNABLE, ACTIVE, BLOCKED, COMPLETED, FAILED, CANCELLED)
- Legal transition enforcement
- Transition event emission
- State query interfaces

**Validation**:
- Illegal transitions rejected with clear errors
- All legal transitions supported
- State changes emit appropriate events
- State queries are consistent with event history

### 7. HEE Validation Layer (src/hee/validation.py)
**Objective**: Implement HEE compliance validation framework

**Requirements**:
- 8 normative property validation functions
- Conceptual model compliance checking
- Validation reporting with actionable feedback
- Integration with runtime monitoring

**Validation**:
- All HEE properties have validation functions
- Validation is deterministic and repeatable
- Reports provide clear compliance status
- Performance overhead is acceptable

### 8. Comprehensive Test Suite (tests/test_heer_*.py)
**Objective**: Create complete test coverage for HEER runtime

**Requirements**:
- Unit tests for all components
- Integration tests for component interaction
- Determinism tests under replay conditions
- Performance and scalability tests

**Validation**:
- All HEER contract requirements tested
- Security validation integrated into tests
- Test coverage meets 95% threshold
- Determinism verified through replay testing

## Success Criteria
- [ ] src/heer/runtime.py implements complete HEER orchestrator
- [ ] src/heer/task_graph.py manages dependencies deterministically
- [ ] src/heer/admission.py enforces policy-based admission
- [ ] src/heer/scheduler.py provides deterministic scheduling
- [ ] src/heer/journal.py enables full event sourcing
- [ ] src/heer/state_machine.py enforces legal transitions
- [ ] src/hee/validation.py validates HEE compliance
- [ ] tests/ provide comprehensive runtime validation
- [ ] Runtime passes all HEER specification requirements
- [ ] Deterministic execution under replay verified
- [ ] All commits include proper model disclosure

## Security Validation
- [ ] All state transitions validated for security compliance
- [ ] Event journaling prevents state manipulation
- [ ] Admission control prevents unauthorized execution
- [ ] Scheduler enforces capacity limits securely
- [ ] State machine prevents invalid transitions
- [ ] Validation framework includes security checks
- [ ] Test suite includes security test vectors
