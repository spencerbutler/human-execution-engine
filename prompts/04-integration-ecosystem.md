# Agent Prompt 04 — Integration Examples & Ecosystem

You are implementing integration examples and ecosystem coordination for the HEE/HEER standards.

## Objectives

1) Create concrete integration examples for tick-task and MT-logo-render
2) Build compliance validation tools for the ecosystem
3) Establish ecosystem coordination mechanisms
4) Provide reference implementations for common integration patterns

## Constraints

- Follow PROMPTING_RULES.md exactly - security validation mandatory
- Integration examples must be immediately executable
- Compliance tools must work across the ecosystem
- Ecosystem patterns must enable independent implementation

## Steps

### 1. tick-task Integration Example (examples/tick_task_integration/)

**Objective**: Demonstrate HEER integration for task management

**Requirements**:

- HEER runtime adapter for tick-task workflows
- Task state synchronization with HEER state machine
- Dependency graph integration with tick-task tasks
- Deterministic scheduling demonstration

**Validation**:

- Integration preserves existing tick-task functionality
- HEER compliance verified through validation tools
- Example is executable and demonstrates benefits
- Security validation integrated into integration

### 2. MT-logo-render Integration Example (examples/logo_render_integration/)

**Objective**: Demonstrate HEE integration for creative workflows

**Requirements**:

- HEE semantic mapping for logo generation workflows
- Deterministic execution of creative processes
- Integration with existing MT-logo-render security model
- Compliance validation for creative work orchestration

**Validation**:

- Integration maintains MT-logo-render's security properties
- HEE compliance demonstrated through validation
- Creative workflow determinism preserved
- Example executable with real logo generation

### 3. HEER Reference Application (examples/heer_reference_app/)

**Objective**: Provide minimal HEER runtime demonstration

**Requirements**:

- Complete but minimal HEER implementation
- Command-line interface for runtime operations
- Deterministic execution demonstration
- State reconstruction from event replay

**Validation**:

- Application demonstrates all HEER requirements
- Deterministic behavior under replay verified
- Security validation integrated
- Performance suitable for demonstration

### 4. Compliance Validation CLI (tools/compliance_validator.py)

**Objective**: Create ecosystem-wide compliance checking tool

**Requirements**:

- HEE compliance validation for implementations
- HEER runtime contract validation
- Automated certification generation
- Integration with CI/CD pipelines

**Validation**:

- Tool works with tick-task, MT-logo-render, and new implementations
- Validation results are deterministic and repeatable
- Certification provides interoperability guarantee
- Performance supports continuous validation

### 5. Specification Validator (tools/spec_validator.py)

**Objective**: Build tool for validating against HEE/HEER specifications

**Requirements**:

- Specification compliance checking
- Implementation validation against canonical specs
- Automated test generation from specifications
- Integration with development workflows

**Validation**:

- Validator uses canonical HEE/HEER specs as source of truth
- Validation is comprehensive and accurate
- Tool integrates with existing development processes
- Results provide clear remediation guidance

### 6. Ecosystem Coordination Documentation (docs/ECOSYSTEM.md)

**Objective**: Document ecosystem integration patterns and governance

**Requirements**:

- Integration patterns for common use cases
- Governance model for ecosystem evolution
- Certification process for implementations
- Migration guides for existing systems

**Validation**:

- Documentation enables ecosystem participation
- Governance model supports sustainable growth
- Certification process is transparent and fair
- Migration guides preserve existing functionality

### 7. Integration Patterns Guide (docs/INTEGRATION_PATTERNS.md)

**Objective**: Provide detailed integration patterns and anti-patterns

**Requirements**:

- Common integration scenarios with examples
- Anti-patterns to avoid in HEE/HEER implementations
- Performance optimization patterns
- Security integration patterns

**Validation**:

- Patterns are validated against real implementations
- Anti-patterns include real-world examples
- Performance patterns provide measurable benefits
- Security patterns maintain ecosystem security properties

## Success Criteria

- [ ] examples/tick_task_integration/ demonstrates HEER compliance
- [ ] examples/logo_render_integration/ shows HEE integration
- [ ] examples/heer_reference_app/ provides executable HEER demo
- [ ] tools/compliance_validator.py enables ecosystem validation
- [ ] tools/spec_validator.py validates against canonical specs
- [ ] docs/ECOSYSTEM.md provides governance framework
- [ ] docs/INTEGRATION_PATTERNS.md guides implementations
- [ ] All integration examples are immediately executable
- [ ] Compliance tools work across ecosystem implementations
- [ ] All commits include proper model disclosure

## Security Validation

- [ ] Integration examples maintain security properties
- [ ] Compliance validator includes security checks
- [ ] Specification validator enforces security requirements
- [ ] Ecosystem documentation includes security considerations
- [ ] Integration patterns preserve security guarantees
- [ ] Reference application demonstrates secure HEER runtime

## Authority
Canonical authority: HEE doctrine and repository governance rules.
This prompt is subordinate to docs/doctrine/ and repository policy enforcement.

## Scope
Defines the operating rules and intended usage for this prompt file only.

## Invariants
- Do not contradict docs/doctrine/.
- Prefer minimal diffs; no opportunistic refactors.
- If requirements conflict, escalate rather than invent policy.
