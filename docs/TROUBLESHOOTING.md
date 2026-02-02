# HEE Troubleshooting Guide

## Overview

This guide provides comprehensive troubleshooting procedures for the Human Execution Engine (HEE) ecosystem,
including common issues, resolution steps, and escalation procedures.

## Quick Reference

### Common Issues and Solutions

| Issue | Solution | Reference |
|-------|----------|-----------|
| Pager invocation | Use `--no-pager` or `PAGER=cat` | [Pager Prevention](#pager-prevention-issues) |
| Branch management violations | Create feature branches | [Branch Management](#branch-management-issues) |
| State capsule errors | Validate format and content | [State Capsule](#state-capsule-issues) |
| Security validation failures | Check input sanitization | [Security](#security-issues) |
| CI/CD failures | Review workflow configuration | [CI/CD](#cicd-issues) |

## Pager Prevention Issues

### Problem: Pager Invocation Detected

**Symptoms**:

- Commands hang or require user interaction
- HEE autonomy violation
- Process failure

**Root Causes**:

- Missing pager prevention flags
- Shell environment pager settings
- Command-specific pager behavior

**Solutions**:

#### Git Commands

```bash
# CORRECT: Pager prevention included
git --no-pager log
GIT_PAGER=cat git status
git diff --no-pager

# INCORRECT: Pager invocation allowed
git --no-pager log         # Prevents pager invocation
git status                 # May invoke pager
```

#### Man Pages

```bash
# CORRECT: Pager prevention included
man -P cat page
MANPAGER=cat man page

# INCORRECT: Pager invocation allowed
man page                   # May invoke pager
```

#### System Commands

```bash
# CORRECT: Pager prevention included
PAGER=cat command
command | cat
command > file.txt

# INCORRECT: Pager invocation allowed
command                    # May invoke pager
```

**Environment Variables**:

```bash
# Set pager prevention globally
export GIT_PAGER=cat
export MANPAGER=cat
export PAGER=cat
```

### Problem: Pager Prevention Not Working

**Diagnosis**:

```bash
# Test pager behavior
echo "Testing pager behavior..." && git --no-pager log --oneline -5
```

**Solutions**:

1. Check shell configuration for pager overrides
2. Verify environment variables are set correctly
3. Use command-specific pager prevention flags
4. Redirect output to file if needed

## Branch Management Issues

### Problem: Direct Main Branch Commits

**Symptoms**:

- HEE governance violations
- Process failure
- State corruption

**Root Causes**:

- Committing directly to main/master
- Missing feature branch workflow
- Inadequate branch management

**Solutions**:

#### Create Feature Branch

```bash
# Create feature branch
git checkout -b feature/work-description

# Make changes and commit
git add .
git commit -m "feat: add feature [model: claude-3.5-sonnet]"

# Push to remote
git push origin feature/work-description

# Create PR
gh pr create --base main --head feature/work-description
```

#### Fix Direct Main Commits

```bash
# Revert main branch changes
git checkout main
git reset --hard HEAD~1  # Remove last commit
git push origin main --force

# Create proper feature branch
git checkout -b feature/fix-branch
git add .
git commit -m "feat: add feature [model: claude-3.5-sonnet]"
git push origin feature/fix-branch
```

### Problem: Branch Naming Violations

**Solutions**:

```bash
# Rename branch to follow HEE conventions
git branch -m old-name feature/new-name
git push origin :old-name
git push origin feature/new-name
```

## State Capsule Issues

### Problem: Invalid State Capsule Format

**Symptoms**:

- Validation failures
- State corruption
- Handoff issues

**Root Causes**:

- Missing required sections
- Incorrect YAML format
- Incomplete task tracking

**Solutions**:

#### Validate State Capsule

```bash
# Run validation script
python scripts/validate_hee_capsule.py --input docs/history/state_capsules/current.md
```

#### Fix Format Issues

```yaml
# Required sections
chat: HEE [Project] Session [Date]
purpose: [Session purpose]
context:
  - Project: [Project name]
  - Current Phase: [Phase]
  - HEE State Version: [Version]
  - Branch: [Branch name]
  - Status: [Status]

decisions:
  - Decision: [Decision text]
    Rationale: [Rationale]
    Impact: [Impact]

open_threads:
  - [Open thread description]

next_chat_bootstrap:
  - [Next step description]
```

### Problem: Missing State Capsule Updates

**Solutions**:

```bash
# Update task status immediately
sed -i 's/- \[ \] Task description/- [x] Task description/' docs/history/state_capsules/current.md

# Add new tasks
echo "- [ ] New task description" >> docs/history/state_capsules/current.md
```

## Security Issues

### Problem: Security Validation Failures

**Symptoms**:

- Pre-commit hook failures
- Security scanner violations
- Input validation errors

**Root Causes**:

- Unsafe code patterns
- Missing input validation
- Hardcoded secrets

**Solutions**:

#### Run Security Scanner

```bash
# Scan for security issues
python scripts/security_scanner.py --format json
```

#### Fix Common Issues

```python
# CORRECT: Safe input validation
def process_input(user_input):
    if not isinstance(user_input, str):
        raise ValueError("Input must be string")
    sanitized = user_input.strip()
    if not sanitized:
        raise ValueError("Input cannot be empty")
    return sanitized

# INCORRECT: Unsafe input handling
def process_input(user_input):
    return eval(user_input)  # DANGEROUS
```

#### Remove Hardcoded Secrets

```python
# CORRECT: Environment variables
import os
password = os.environ.get('DB_PASSWORD')

# INCORRECT: Hardcoded secrets
password = "my-secret-password"  # DANGEROUS
```

### Problem: Unicode/Character Issues

**Solutions**:

```python
# Sanitize input
def sanitize_input(text):
    # Remove control characters
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
    # Normalize Unicode
    import unicodedata
    return unicodedata.normalize('NFKC', sanitized)
```

## CI/CD Issues

### Problem: CI Pipeline Failures

**Symptoms**:

- Build failures
- Test failures
- Deployment issues

**Root Causes**:

- Missing dependencies
- Configuration errors
- Code quality issues

**Solutions**:

#### Check CI Configuration

```yaml
# .github/workflows/ci.yml
name: HEE CI Pipeline
on:
  pull_request:
    branches: [ main, master ]
  push:
    branches: [ main, master ]

jobs:
  hee-compliance-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Check for pager invocation prevention
      run: |
        echo "🔍 Validating pager prevention in shell commands..."
        if grep -r "git log" --include="*.md" --include="*.sh" . | grep -v "git --no-pager"; then
          echo "❌ Found git log without pager prevention"
          exit 1
        fi
```

#### Fix Pre-commit Issues

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: hee-pager-prevention-check
        name: HEE Pager Prevention Check
        entry: bash -c 'echo "🔍 Checking for pager prevention..." && (grep -r "git log" . | grep -v "git --no-pager" | head -1 && exit 1 || echo "✅ Pager prevention check passed")'
        language: system
        files: '.*\.(md|sh)$'
```

### Problem: Pre-commit Hook Failures

**Solutions**:

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit manually
pre-commit run --all-files

# Skip pre-commit (emergency only)
git commit --no-verify -m "Emergency commit [model: claude-3.5-sonnet]"
```

## Agent Coordination Issues

### Problem: State Handoff Failures

**Symptoms**:

- Agent transitions fail
- State corruption
- Context loss

**Root Causes**:

- Incomplete state capsules
- Missing decision documentation
- Format violations

**Solutions**:

#### Validate Handoff Capsule

```bash
# Run handoff validation
python scripts/validate_hee_handoff.py --input HEE-Handoff-[ID].md
```

#### Fix Handoff Issues

```yaml
# Required handoff format
chat: HEE [Project] Agent Handoff [Originator]→[Recipient]
purpose: Preserve HEE state and context for agent transition
context:
  - Project: [HEE Project Name]
  - Current Phase: [Phase/Milestone]
  - HEE State Version: [Version]
  - Originator Agent: [Agent ID]
  - Recipient Agent: [Agent ID]
  - Handoff Timestamp: [ISO 8601]
  - HEE Governance Compliance: [Status]

decisions:
  - Decision: [Decision Text]
    Rationale: [HEE Alignment Explanation]
    Impact: [HEE System Impact]
    Follow-up: [Next Steps]
    HEE Compliance: [Governance Reference]

open_threads:
  - [Unresolved issues requiring recipient attention]
  - [HEE-specific pending tasks]
  - [Dependencies and blockers]

next_chat_bootstrap:
  - [Immediate next steps for recipient]
  - [HEE execution continuation instructions]
  - [Priority-ordered task list]
```

### Problem: Agent Communication Breakdown

**Solutions**:

```bash
# Check agent coordination
python scripts/check_agent_coordination.py --status

# Force agent synchronization
python scripts/sync_agent_state.py --force
```

## Performance Issues

### Problem: Slow HEE Operations

**Symptoms**:

- Long execution times
- Resource exhaustion
- Timeout errors

**Root Causes**:

- Inefficient code patterns
- Missing optimizations
- Resource constraints

**Solutions**:

#### Optimize Code

```python
# CORRECT: Efficient patterns
def process_large_dataset(data):
    # Use generators for memory efficiency
    for item in data:
        yield process_item(item)

# INCORRECT: Memory-intensive patterns
def process_large_dataset(data):
    results = []
    for item in data:
        results.append(process_item(item))
    return results
```

#### Monitor Resource Usage

```bash
# Check system resources
top
htop
free -h
df -h
```

## Escalation Procedures

### When to Escalate

Escalate immediately if:

- Critical security vulnerabilities found
- State corruption detected
- Multiple HEE violations occur
- System instability persists

### Escalation Process

1. **Document Issue**

   ```markdown
   ## 🚨 Critical HEE Issue

   **Date**: [YYYY-MM-DD]
   **Issue**: [Description]
   **Impact**: [Severity assessment]
   **Steps to Reproduce**: [Detailed steps]
   ```

2. **Update State Capsule**

   ```bash
   echo "🚨 CRITICAL: [Issue description]" >> docs/history/state_capsules/current.md
   ```

3. **Notify Team**
   - Update team channels
   - Create incident report
   - Document resolution steps

4. **Implement Fix**
   - Apply emergency procedures
   - Test resolution
   - Validate system stability

### Emergency Procedures

#### Emergency State Recovery

```bash
# Create emergency backup
python scripts/create_emergency_backup.py --output emergency_backup.json

# Restore from backup
python scripts/restore_from_backup.py --backup emergency_backup.json
```

#### Emergency Branch Recovery

```bash
# Reset to known good state
git checkout main
git reset --hard origin/main
git clean -fd
```

## Prevention Strategies

### Regular Maintenance

#### Daily Checks

```bash
# Validate state capsules
python scripts/validate_hee_capsule.py --all

# Check for violations
python scripts/check_violations.py --daily
```

#### Weekly Reviews

```bash
# Review security posture
python scripts/security_audit.py --weekly

# Update documentation
python scripts/update_documentation.py --weekly
```

#### Monthly Audits

```bash
# Comprehensive system audit
python scripts/comprehensive_audit.py --monthly

# Performance review
python scripts/performance_review.py --monthly
```

### Best Practices

1. **Always use feature branches**
2. **Update state capsules immediately**
3. **Validate all changes**
4. **Test thoroughly before deployment**
5. **Document all decisions**
6. **Monitor system health**
7. **Escalate early when issues arise**

## Support Resources

### Documentation

- [HEE Policy](HEE_POLICY.md)
- [State Capsule Guide](STATE_CAPSULE_GUIDE.md)
- [Prompting Rules](../prompts/PROMPTING_RULES.md)
- [Agent Handoff Guide](../prompts/AGENT_STATE_HANDOFF.md)

### Tools

- `scripts/security_scanner.py` - Security validation
- `scripts/validate_hee_capsule.py` - State capsule validation
- `scripts/violation_checker.sh` - Violation detection
- `scripts/validate_hee_handoff.py` - Handoff validation

### Emergency Contacts

- HEE Monitor: [monitor@hee.example.com]
- Security Team: [security@hee.example.com]
- DevOps Team: [devops@hee.example.com]

---

**Remember**: When in doubt, escalate early and document thoroughly. HEE system integrity is paramount.
