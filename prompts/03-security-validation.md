# Agent Prompt 03 — Security & Validation Framework

You are implementing the comprehensive security and validation framework for the HEE/HEER ecosystem.

## Objectives

1) Build security validation infrastructure for all HEE/HEER implementations
2) Create automated compliance scanning and validation tools
3) Establish HEE/HEER-specific security constraints and monitoring
4) Provide security test vectors and validation procedures

## Constraints

- Follow PROMPTING_RULES.md exactly - security is highest priority
- All validation must be deterministic and repeatable
- Security scanning must prevent known vulnerability patterns
- HEE/HEER security requirements must be enforceable

## Steps

### 1. Security Validation Core (src/security/validator.py)

**Objective**: Implement comprehensive input validation for HEE/HEER systems

**Requirements**:

- Unicode validation and normalization
- Control character blocking and detection
- Zero-width character removal
- Input sanitization with HEE/HEER context awareness

**Validation**:

- All validation functions are deterministic
- Security test vectors pass validation
- Performance overhead is acceptable
- False positives minimized

### 2. Content Sanitization (src/security/sanitizer.py)

**Objective**: Provide content sanitization for human work orchestration

**Requirements**:

- Task description sanitization
- Operator input cleaning
- Event data sanitization
- Policy content validation

**Validation**:

- Sanitization preserves semantic meaning
- Security threats neutralized
- HEE/HEER workflows remain functional
- Audit trail maintained

### 3. Security Audit Framework (src/security/audit.py)

**Objective**: Implement security monitoring and audit capabilities

**Requirements**:

- Security event logging and monitoring
- Compliance violation detection
- Audit trail generation for security events
- Integration with runtime event journaling

**Validation**:

- Security events are tamper-evident
- Audit trails support forensic analysis
- Performance monitoring doesn't impact runtime
- Compliance violations trigger appropriate alerts

### 4. Automated Security Scanner (scripts/security_scanner.py)

**Objective**: Create CLI tool for automated security scanning

**Requirements**:

- File system security scanning
- HEE/HEER-specific security checks
- Vulnerability pattern detection
- Compliance reporting and recommendations

**Validation**:

- Scanner runs without runtime dependencies
- False positive rate below 5%
- Performance suitable for CI/CD integration
- Reports provide actionable remediation steps

### 5. Security Validation CLI (scripts/security_validator.py)

**Objective**: Build CLI tool for HEE/HEER security validation

**Requirements**:

- Runtime security policy validation
- Input validation testing
- Security compliance certification
- Integration with automated testing

**Validation**:

- CLI integrates with existing security workflows
- Validation results are machine-readable
- Performance supports continuous validation
- Security requirements are comprehensively checked

### 6. Security Documentation (docs/SECURITY.md)

**Objective**: Document security requirements and implementation

**Requirements**:

- Threat model for HEE/HEER systems
- Security requirements and constraints
- Implementation guidance for secure HEE/HEER systems
- Security testing and validation procedures

**Validation**:

- Documentation covers all security requirements
- Implementation examples are secure by default
- Testing procedures are comprehensive
- Security considerations integrated throughout

### 7. Security Test Suite (tests/security/)

**Objective**: Create comprehensive security test coverage

**Requirements**:

- Input validation test vectors
- Sanitization effectiveness tests
- Security scanner validation tests
- Integration security tests

**Validation**:

- All security requirements have test coverage
- Tests include known attack vectors
- Security regressions prevented
- Test performance supports CI/CD

## Success Criteria

- [ ] src/security/validator.py provides comprehensive validation
- [ ] src/security/sanitizer.py ensures content safety
- [ ] src/security/audit.py enables security monitoring
- [ ] scripts/security_scanner.py provides automated scanning
- [ ] scripts/security_validator.py enables validation CLI
- [ ] docs/SECURITY.md documents security requirements
- [ ] tests/security/ provides complete security test coverage
- [ ] All HEE/HEER security constraints implemented
- [ ] Security validation integrated into all workflows
- [ ] All commits include proper model disclosure

## Security Validation

- [ ] Security validation functions prevent known attacks
- [ ] Sanitization neutralizes malicious content
- [ ] Audit framework provides tamper-evident logging
- [ ] Security scanner detects vulnerability patterns
- [ ] Security tests cover comprehensive threat model
- [ ] Documentation enables secure HEE/HEER implementation
- [ ] No security bypasses or backdoors implemented

## Authority
Canonical authority: HEE doctrine and repository governance rules.
This prompt is subordinate to docs/doctrine/ and repository policy enforcement.

## Scope
Defines the operating rules and intended usage for this prompt file only.

## Invariants
- Do not contradict docs/doctrine/.
- Prefer minimal diffs; no opportunistic refactors.
- If requirements conflict, escalate rather than invent policy.
