# Failure Playbook

Strict failure response procedures for HEE operations.

## Failure Flow

### 1. STOP

- Immediately halt all operations
- Preserve current state
- Do not make additional changes
- Document current status

### 2. CAPTURE

- Collect all relevant logs and artifacts
- Take git status snapshots
- Capture error messages and stack traces
- Document timeline of events

### 3. CLASSIFY

- Identify failure mode from classification table
- Determine severity level
- Assess impact scope
- Assign investigation priority

### 4. CORRECT

- Apply minimal corrective action
- Follow containment procedures
- Restore to known good state
- Verify fix effectiveness

### 5. VERIFY

- Run validation checks
- Confirm no additional issues
- Test related functionality
- Document resolution

### 6. REPORT

- Generate failure report
- Document lessons learned
- Update procedures if needed
- Escalate if unresolved

## Failure Classification

| Failure Mode | Description | Immediate Action | Severity |
|--------------|-------------|------------------|----------|
| Dirty Main | Main branch has untracked changes | STOP, do not proceed | CRITICAL |
| Wrong Branch | Not on expected branch | STOP, switch to correct branch | HIGH |
| Outside Write | Writing files outside `doc/oper/**` | STOP, revert changes | CRITICAL |
| Missing Paths | Required files/directories missing | STOP, investigate | MEDIUM |
| Merge Conflicts | Git conflicts during operation | STOP, resolve conflicts | HIGH |
| Failing Checks | Validation or CI checks fail | STOP, investigate root cause | MEDIUM |
| Hallucinated Files | Referencing non-existent files | STOP, verify file existence | HIGH |
| Command Failures | Critical commands return non-zero | STOP, analyze error | HIGH |
| Permission Denied | Access denied to required resources | STOP, check permissions | MEDIUM |
| Network Issues | Connectivity problems during operation | STOP, verify network | MEDIUM |

## Recovery Procedures

### Dirty Main Branch

1. **STOP** - Do not proceed with operation
2. **CAPTURE** - Document current git status
3. **CORRECT** - Stash or commit changes to main
4. **VERIFY** - Confirm clean main branch
5. **REPORT** - Document cause of dirty state

### Wrong Branch

1. **STOP** - Halt all operations immediately
2. **CAPTURE** - Document current branch and changes
3. **CORRECT** - Switch to correct branch
4. **VERIFY** - Confirm correct branch is active
5. **REPORT** - Document branch confusion

### Outside Write Detection

1. **STOP** - Immediately cease file operations
2. **CAPTURE** - Document all files written outside scope
3. **CORRECT** - Remove or move files to correct location
4. **VERIFY** - Confirm only `doc/oper/**` files remain changed
5. **REPORT** - Document scope violation

### Missing Paths

1. **STOP** - Halt operations requiring missing paths
2. **CAPTURE** - Document missing files/directories
3. **CORRECT** - Create missing paths or adjust operation
4. **VERIFY** - Confirm all required paths exist
5. **REPORT** - Document path issues

## Never Do List

**DO NOT:**

- Force push to main branch
- Edit YAML by hand for quick fixes
- Introduce new scripts/tools as a "quick fix"
- Continue after a hard gate fails
- Ignore error messages or warnings
- Skip validation steps
- Make assumptions about file existence
- Modify files outside scope without approval

**ALWAYS:**

- Stop immediately on hard gate failures
- Capture evidence before making changes
- Follow established procedures
- Document all actions taken
- Escalate unresolved issues
- Verify fixes before proceeding

## Escalation Criteria

Escalate to senior operator when:

- Multiple hard gates fail
- Root cause cannot be identified
- Fix requires scope changes
- Security concerns are present
- Timeline exceeds 30 minutes
- Pattern of similar failures observed

## Post-Failure Actions

1. **Root Cause Analysis**
   - Identify underlying cause
   - Document contributing factors
   - Assess preventability

2. **Procedure Updates**
   - Update failure playbook if needed
   - Improve detection mechanisms
   - Enhance prevention measures

3. **Knowledge Sharing**
   - Share lessons learned
   - Update team documentation
   - Conduct post-mortem if critical

4. **Prevention Measures**
   - Implement additional safeguards
   - Improve monitoring
   - Enhance training materials
