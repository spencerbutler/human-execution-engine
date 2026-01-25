# Agent Prompt 06 — Ecosystem Launch & Adoption

You are launching the HEE/HEER ecosystem and driving adoption across implementations.

## Objectives

1) Coordinate HEE/HEER adoption across tick-task and MT-logo-render
2) Establish ecosystem governance and certification processes
3) Create migration support for existing implementations
4) Launch community participation and growth initiatives

## Constraints

- Follow PROMPTING_RULES.md exactly - security validation mandatory
- Ecosystem launch must maintain backward compatibility
- Certification process must be transparent and enforceable
- Community growth must preserve security and quality standards

## Steps

### 1. Ecosystem Governance (docs/GOVERNANCE.md)

**Objective**: Establish governance model for ecosystem evolution

**Requirements**:

- Decision-making processes for specification changes
- Ecosystem maintainer responsibilities
- Conflict resolution mechanisms
- Sustainability and funding models

**Validation**:

- Governance enables ecosystem growth
- Processes are transparent and fair
- Security requirements protected
- Community participation supported

### 2. Compliance Certification (docs/CERTIFICATION.md)

**Objective**: Define certification process for HEE/HEER implementations

**Requirements**:

- Certification levels (Basic, Full, Ecosystem)
- Automated certification procedures
- Badge and verification systems
- Recertification requirements

**Validation**:

- Certification provides interoperability guarantees
- Process is transparent and repeatable
- Security compliance mandatory
- Certification scales with ecosystem growth

### 3. Migration Guides (docs/MIGRATION_GUIDES.md)

**Objective**: Provide comprehensive migration support

**Requirements**:

- tick-task HEER integration migration guide
- MT-logo-render HEE compliance migration guide
- Legacy system migration patterns
- Rollback and recovery procedures

**Validation**:

- Guides preserve existing functionality
- Migration processes are safe and reversible
- Performance characteristics maintained
- Security properties enhanced or preserved

### 4. Ecosystem Compliance Validator (tools/ecosystem_validator.py)

**Objective**: Build cross-ecosystem compliance checking

**Requirements**:

- Multi-implementation compliance validation
- Ecosystem-wide interoperability testing
- Automated certification generation
- Performance and security benchmarking

**Validation**:

- Validator works across all ecosystem implementations
- Results provide clear interoperability status
- Performance benchmarks are meaningful
- Security validation is comprehensive

### 5. Adoption Tracker (tools/adoption_tracker.py)

**Objective**: Monitor and report ecosystem adoption metrics

**Requirements**:

- Implementation adoption tracking
- Compliance level monitoring
- Ecosystem health metrics
- Growth and participation analytics

**Validation**:

- Metrics provide actionable insights
- Tracking is privacy-preserving
- Data supports ecosystem decision-making
- Security metrics integrated

### 6. Issue Templates (.github/ISSUE_TEMPLATE/)

**Objective**: Create structured contribution templates

**Requirements**:

- Compliance report template
- Ecosystem integration template
- Security vulnerability template
- Feature request template

**Validation**:

- Templates collect required information
- Process enables efficient triaging
- Security reports have proper handling
- Community contributions properly routed

### 7. PR Template (.github/PULL_REQUEST_TEMPLATE.md)

**Objective**: Establish PR standards for ecosystem contributions

**Requirements**:

- Comprehensive PR description requirements
- Security and compliance checklist
- Testing and validation requirements
- Ecosystem impact assessment

**Validation**:

- Template ensures quality PR submissions
- Requirements align with PROMPTING_RULES.md
- Process enables efficient review
- Ecosystem coordination supported

## Success Criteria

- [ ] docs/GOVERNANCE.md establishes ecosystem governance
- [ ] docs/CERTIFICATION.md defines compliance process
- [ ] docs/MIGRATION_GUIDES.md supports safe migrations
- [ ] tools/ecosystem_validator.py enables cross-ecosystem validation
- [ ] tools/adoption_tracker.py provides ecosystem metrics
- [ ] .github/ISSUE_TEMPLATE/ enables structured contributions
- [ ] .github/PULL_REQUEST_TEMPLATE.md establishes PR standards
- [ ] Ecosystem governance supports sustainable growth
- [ ] Certification process enables interoperability
- [ ] Migration guides preserve existing functionality
- [ ] All commits include proper model disclosure

## Security Validation

- [ ] Governance model protects security requirements
- [ ] Certification mandates security compliance
- [ ] Migration guides maintain security properties
- [ ] Ecosystem validator includes security checks
- [ ] Issue templates properly handle security reports
- [ ] PR template requires security validation
- [ ] Adoption tracking preserves privacy and security
