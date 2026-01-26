# Agent Prompt 01 — Architecture & API Design

You are implementing the architecture and API design for the Human Execution Engine ecosystem.

## Objectives

1) Define reference architecture for HEE/HEER implementations
2) Establish standard API contracts for ecosystem interoperability
3) Create compliance validation framework foundation
4) Provide implementation guidance for ecosystem components

## Constraints

- Follow PROMPTING_RULES.md exactly - security validation mandatory
- All APIs must support both tick-task and MT-logo-render integration
- Architecture must enable deterministic interoperability
- No implementation code - design and contracts only

## Steps

### 1. Create Architecture Document (docs/ARCHITECTURE.md)

**Objective**: Define reference architecture for HEE/HEER systems

**Requirements**:

- Layered architecture: HEE conceptual → HEER operational → Implementation
- Component responsibilities and interfaces
- Data flow patterns for deterministic execution
- Integration points for ecosystem tools

**Validation**:

- Architecture supports both task management and creative work flows
- Clear separation of concerns between layers
- Deterministic execution paths defined
- Security integration points identified

### 2. Define API Contracts (docs/API.md)

**Objective**: Establish standard interfaces for HEE/HEER compliance

**Requirements**:

- Core abstractions: Task, Operator, Runtime Policy, Execution Event
- Command interface (write path) with deterministic semantics
- Query interface (read path) for state inspection
- Event schema for journaling and replay

**Validation**:

- APIs support tick-task task management workflows
- APIs support MT-logo-render creative orchestration
- Deterministic command execution guaranteed
- Event sourcing enables full state reconstruction

### 3. Compliance Framework (docs/COMPLIANCE.md)

**Objective**: Define certification criteria for HEE/HEER implementations

**Requirements**:

- HEE compliance checklist (8 normative properties)
- HEER compliance checklist (runtime contract validation)
- Automated validation procedures
- Certification levels (Basic, Full, Ecosystem)

**Validation**:

- Compliance tests map to specification requirements
- Validation procedures are automatable
- Certification provides ecosystem interoperability guarantee
- Security compliance integrated into certification

### 4. Implementation Guide (docs/IMPLEMENTATION_GUIDE.md)

**Objective**: Provide guidance for building HEE/HEER systems

**Requirements**:

- Step-by-step implementation roadmap
- Common patterns and anti-patterns
- Integration examples for existing tools
- Migration strategies for legacy systems

**Validation**:

- Guide enables independent HEE/HEER implementation
- Examples are executable against specifications
- Migration paths preserve existing functionality
- Security considerations integrated throughout

### 5. Core Abstractions (src/core/abstractions.py)

**Objective**: Define foundational abstractions for the ecosystem

**Requirements**:

- Task abstraction with HEE compliance
- Operator model with capacity constraints
- Runtime policy framework
- Event base classes for journaling

**Validation**:

- Abstractions are implementation-language agnostic
- All HEE/HEER requirements captured
- Security validation interfaces included
- Extensible for ecosystem needs

### 6. Basic Compliance Checking (src/validation/compliance.py)

**Objective**: Create foundation for automated compliance validation

**Requirements**:

- HEE property validation functions
- HEER contract checking interfaces
- Basic validation reporting
- Extensible validation framework

**Validation**:

- Validation functions map to specification requirements
- Security validation integrated
- Reporting provides actionable feedback
- Framework supports ecosystem scaling

## Success Criteria

- [ ] docs/ARCHITECTURE.md defines complete reference architecture
- [ ] docs/API.md specifies standard HEE/HEER interfaces
- [ ] docs/COMPLIANCE.md provides certification framework
- [ ] docs/IMPLEMENTATION_GUIDE.md enables independent implementation
- [ ] src/core/abstractions.py contains foundational abstractions
- [ ] src/validation/compliance.py provides validation foundation
- [ ] All files committed with proper model disclosure
- [ ] Architecture supports ecosystem interoperability

## Security Validation

- [ ] All APIs include security validation interfaces
- [ ] Architecture defines security integration points
- [ ] Compliance framework requires security validation
- [ ] Implementation guide includes security considerations
- [ ] Abstractions support security validation
- [ ] No implementation bypasses security requirements

## Authority
Canonical authority: HEE doctrine and repository governance rules.
This prompt is subordinate to docs/doctrine/ and repository policy enforcement.

## Scope
Defines the operating rules and intended usage for this prompt file only.

## Invariants
- Do not contradict docs/doctrine/.
- Prefer minimal diffs; no opportunistic refactors.
- If requirements conflict, escalate rather than invent policy.
