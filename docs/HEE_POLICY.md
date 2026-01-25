# HEE Policy and Governance

## Overview

This document defines the policies and governance rules for the Human Execution Engine (HEE) ecosystem, ensuring consistent behavior and preventing violations of HEE principles.

## Core HEE Policies

### 1. Output Pager Prevention Policy

**CRITICAL HEE VIOLATION**: Output MUST never invoke shell PAGER

**Rationale**: Pager invocation requires oper intervention, violating HEE autonomy and deterministic execution principles.

**Enforcement**:
- All shell commands must include pager prevention when applicable
- Pager bypass required for ALL interactive commands
- Violation constitutes HEE process failure
- Document pager prevention in all command examples

**Command-Specific Requirements**:
- **Git**: Use `--no-pager` flag or `GIT_PAGER=cat` environment variable
- **Man pages**: Use `-P cat` flag or `MANPAGER=cat` environment variable
- **Less/More**: Use `cat` or redirect to file instead
- **Grep**: Use `--no-pager` where available, otherwise redirect output
- **Find**: Use `-print0` with `xargs -0` or redirect to file
- **System commands**: Use `PAGER=cat` environment variable or output redirection

**Examples**:
```bash
# CORRECT: Pager prevention included
git --no-pager log
GIT_PAGER=cat git status
man -P cat page
PAGER=cat command
command | cat
command > file.txt

# INCORRECT: Pager invocation allowed
git log                    # May invoke pager
man page                   # May invoke pager
command                    # May invoke pager
```

### 2. Branch Management Policy

**Requirement**: ALL changes MUST use feature branches

**Enforcement**:
- Never commit directly to main branch
- Feature branches named: `feature/description-of-work`
- Delete merged branches immediately to prevent confusion
- All changes made on feature branches only

**Workflow**:
```bash
git checkout -b feature/work-description
# Make changes, commit frequently
git push origin feature/work-description
gh pr create --base main --head feature/work-description
# Wait for merge, then cleanup
git checkout main && git pull origin main
git branch -D feature/merged-branch  # Local
git push origin --delete feature/merged-branch  # Remote
```

### 3. State Preservation Policy

**Requirement**: HEE state MUST be preserved across all operations

**Enforcement**:
- Update state capsule after every phase
- Document all state changes
- Maintain state consistency throughout session
- Never leave repository in inconsistent state

**State Capsule Requirements**:
- All required sections present
- HEE YAML format compliance
- HEE naming conventions followed
- HEE date and version references accurate

### 4. Security Validation Policy

**Requirement**: Security validation BEFORE any implementation

**Enforcement**:
- All inputs validated against HEE/HEER security requirements
- No shell commands without security pre-check
- Content sanitization required for all user inputs
- Threat model verification mandatory

**Security Checks**:
- Unicode validation for all text inputs
- Control character blocking
- Zero-width character detection
- Safe character normalization

### 5. Documentation Policy

**Requirement**: Documentation is paramount - no undefined references

**Enforcement**:
- No references to non-existent files/tools
- All README examples must work immediately
- API documentation must reflect actual implementation
- Specs must be canonical and complete

**Documentation Standards**:
- Use relative paths for portability
- Include file references and cross-links for navigation
- Design for smooth handoffs and team onboarding
- Maintain consistency with existing documentation patterns

### 6. Model Disclosure Policy

**Requirement**: ALL commits require model disclosure

**Enforcement**:
- No commits without model identification
- Model name must match actual model used
- Disclosure required in commit subject line
- No exceptions for any commit

**Format**:
```
Pattern: [model: model-name]
Example: [model: claude-3.5-sonnet]
```

### 7. Command Safety Policy

**Requirement**: PRE-VALIDATION required for all commands

**Enforcement**:
- Syntax validation with `bash -n` for all shell commands
- Path verification before file operations
- Git state verification before repository operations
- No execution without explicit validation

**Validation Pattern**:
```bash
# Pattern: Validate then execute
[ -f file.txt ] && echo "File exists" || echo "File missing - plan violation"
```

### 8. Integration Compliance Policy

**Requirement**: HEE/HEER compliance enforced

**Enforcement**:
- All changes validated against HEE conceptual model
- HEER runtime contract compliance required
- Breaking changes require ecosystem coordination
- Integration examples must be executable immediately

## Violation Reporting

### HEE Rule Violation Documentation

**Process**:
1. **Immediate**: Document violation in state capsule
2. **Analysis**: Identify root cause and impact
3. **Resolution**: Record corrective actions taken
4. **Prevention**: Add measures to prevent recurrence

**Violation Categories**:
- **Critical**: Pager invocation, direct main commits, state corruption
- **High**: Security violations, documentation failures
- **Medium**: Command safety issues, integration problems
- **Low**: Minor policy violations, formatting issues

**Example Violation Report**:
```markdown
## 🚨 HEE Rule Violation Documentation

### **Violation**: Direct Main Branch Commit
**Date**: 2026-01-24 at 17:42:52 CST
**Commit**: `7f4bd4f` - "feat: Add human-readable timestamps"
**Issue**: Created files/changes directly on main branch instead of feature branch

### **Root Cause Analysis**:
- Assumed minor formatting changes were acceptable on main
- Failed to follow "ALWAYS create feature branches" rule

### **Impact**:
- ❌ Violates HEE governance and change tracking
- ❌ Breaks established workflow standards

### **Corrective Action Taken**:
- ✅ **Immediate**: Reverted main branch changes (commit `fa16f86`)
- ✅ **Proper Process**: Changes moved to feature branch workflow
- ✅ **Documentation**: Violation recorded in state capsule

### **Status**: RESOLVED ✅
```

## Compliance Monitoring

### Regular Audits
- **Daily**: Review state capsule for violations
- **Weekly**: Audit branch management compliance
- **Monthly**: Review security and documentation standards

### Automated Checks
- Pre-commit hooks for HEE compliance
- State capsule validation in CI/CD
- Pager prevention validation in command examples

### Enforcement Actions
- **First violation**: Warning and documentation
- **Repeated violations**: Process review and training
- **Critical violations**: Immediate corrective action required

## Policy Updates

### Version Control
- All policy changes tracked in git
- Model disclosure required for policy commits
- State capsule updates for policy changes

### Review Process
- Policy reviews every 3 months
- Community feedback incorporated
- HEE principles maintained as core

## References

- [HEE Definition](HEE.md)
- [Prompting Rules](../prompts/PROMPTING_RULES.md)
- [State Capsule Guide](STATE_CAPSULE_GUIDE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

---

**These policies are ENFORCEMENT RULES, not guidelines. Violation constitutes process failure.**
