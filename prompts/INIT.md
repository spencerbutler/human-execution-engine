# 🚨 IMMEDIATE AGENT HYDRATION - CONTEXT DETECTION

**CRITICAL**: Before proceeding with any INIT tasks, agents MUST determine their current state of knowledge about this repository and hydrate accordingly.

## Step 1: Check Current-Tasks Capsule Status

**File to Check**: `docs/STATE_CAPSULES/CURRENT_TASKS.md` (Canonical Entry Point)

### If Current-Tasks Capsule EXISTS and has SUBSTANTIVE CONTENT

**→ AGENT HAS CONTEXT**

1. **Read Current-Tasks Capsule** for immediate state awareness
2. **Understand Active Tasks**: What's in progress, what's completed
3. **Identify Violations**: Any active HEE rule violations
4. **Check Branch Status**: Current branch state and open PRs
5. **Review Agent Handoff Reference**: Check for final handoff capsule and project context documents
6. **Proceed with INIT tasks** based on current state

### If Current-Tasks Capsule is MISSING or EMPTY/DEFAULT

**→ AGENT HAS NO CONTEXT**

1. **Read Prompting Rules** (`prompts/PROMPTING_RULES.md`) - Foundation
2. **Read Bootstrap Guide** (`prompts/BOOTSTRAP.md` or equivalent) - Setup
3. **Read Troubleshooting** (`prompts/TROUBLESHOOTING.md`) - Problem-solving
4. **Create Initial Current-Tasks Capsule** - Establish state tracking
5. **Proceed with INIT tasks** from beginning

### Step 2: Review All State Capsules (If Available)

**Directory to Check**: `docs/STATE_CAPSULES/` (All dated subdirectories)

**Hydration Process**:

1. **List All Capsule Directories**: Check for dated folders (e.g., `2026-01-24/`)
2. **Read Historical Capsules**: Review previous state capsules in reverse chronological order
3. **Identify Outstanding Tasks**: Look for unresolved issues, open threads, or pending decisions
4. **Check Final Handoff Capsule**: Review `HEE-Final-Handoff-Capsule.md` for complete project transition
5. **Review Project Context**: Read README.md and CHANGELOG.md for current status and history

**Capsule Reading Order**:
- Start with `CURRENT_TASKS.md` (current status)
- Review most recent dated capsules (newest first)
- Check for final handoff capsule references
- Cross-reference with README and CHANGELOG for context

## Current-Tasks Capsule Validation

**Substantive Content Indicators**:

- Contains active task sections with status updates
- Has violation documentation and resolutions
- Includes branch management tracking
- Shows cross-references to other files
- Contains meaningful status updates and progress tracking

**Empty/Default State Indicators**:

- Only contains template placeholders
- Has no substantive task tracking
- Missing violation documentation
- No meaningful status updates
- Only basic structure without content

## Admission Control: PLAN→ACT Handshake

**CRITICAL PROTOCOL**: All HEE prompts require explicit human authorization before any mutation.

**PLAN Phase Requirements**:
- Agent MUST produce a PLAN response and then STOP
- Agent MUST end PLAN output with: WAITING_FOR: APPROVED_TO_ACT
- Agent MUST wait for exact token: APPROVED_TO_ACT
- Agent MAY run read-only commands: ls, cat, rg, git status/diff/log
- Agent MUST NOT run any command that could change the working tree
- Agent MUST NOT perform file writes, moves, deletes, copies, or formatting
- Agent MUST NOT execute git operations (add/commit/push/merge)
- Agent MUST NOT run scripts that modify repository state

**ACT Phase Requirements**:
- Agent MUST NOT begin mutations until receiving exact token: APPROVED_TO_ACT
- Token must match exactly: APPROVED_TO_ACT (case-sensitive, no quotes, no surrounding whitespace)
- Any mutation before approval constitutes RULE VIOLATION
- Agent MUST treat unauthorized mutations as HEE governance failure

**Mutation Definition**:
- File writes, moves, deletes, copies
- Git add/commit/push/merge operations
- Running scripts that write files or modify repository state
- Any command that changes working tree or git history
- Format, generate, or install operations that modify files

**Protocol Violation Handling**:
- Agent MUST report violations immediately
- Only human decides whether to revert/keep unauthorized mutations
- Agent must not auto-revert unless explicitly instructed by human
- Human MUST have opportunity to reject unauthorized changes
- Unauthorized mutations MAY be reverted by human decision

---

# HEE Project Initialization Guide

This guide provides systematic procedures for initializing and setting up the Human Execution Engine (HEE) ecosystem, with comprehensive file references and task sections for smooth project bootstrap and team onboarding.

## Quick Reference - File Locations

### HEE Documentation

- State Capsule Guide: `docs/STATE_CAPSULE_GUIDE.md`
- Prompting Rules: `prompts/PROMPTING_RULES.md`
- Agent State Handoff: `prompts/AGENT_STATE_HANDOFF.md`
- Current Tasks: `@docs/STATE_CAPSULES/CURRENT_TASKS.md`
- HEE Policy: `docs/HEE_POLICY.md`

### Project Structure

- Main README: `README.md`
- CI/CD Configuration: `.github/workflows/`
- Pre-commit Config: `.pre-commit-config.yaml`
- Security Scanning: `scripts/security_scanner.py`

### Initialization Resources

- This guide: `prompts/INIT.md`
- HEE optimization: `prompts/GROQ_OPTIMIZATION_RULES.md`
- Agent analysis: `prompts/AGENT_COMPARISON_ANALYSIS.md`
- State capsule template: `docs/TEMPLATES/STATE_CAPSULE_TEMPLATE.md`

## Project Bootstrap Checklist

### Task: Environment Setup Verification

**Status**: Completed
**Priority**: High
**Related Files**:

- `prompts/PROMPTING_RULES.md` - HEE prompting rules
- `docs/HEE_POLICY.md` - HEE policies
- `prompts/GROQ_OPTIMIZATION_RULES.md` - Optimization guidelines

**Description**
Verify development environment is properly configured for HEE development and follows all governance requirements.

**Steps to Complete**

- [ ] Install required tools and dependencies
- [ ] Configure HEE-specific environment variables
- [ ] Set up security validation tools
- [ ] Verify Git configuration and authentication
- [ ] Test HEE command execution capabilities

**Files Involved**

- `prompts/PROMPTING_RULES.md` - Environment requirements reference
- `docs/HEE_POLICY.md` - Policy compliance verification
- `prompts/GROQ_OPTIMIZATION_RULES.md` - Optimization setup
- `prompts/INIT.md` - This initialization guide

**Dependencies**

- Access to development environment
- Understanding of HEE tool requirements
- Knowledge of security validation procedures

**Notes**

- Ensure all HEE policies are understood and followed
- Verify Groq optimization setup for cost efficiency
- Test pager prevention in command execution
- Confirm Git workflow compliance

### Task: HEE State Management Setup

**Status**: Completed
**Priority**: High
**Related Files**:

- `docs/STATE_CAPSULE_GUIDE.md` - State management rules
- `docs/TEMPLATES/STATE_CAPSULE_TEMPLATE.md` - Template structure
- `docs/STATE_CAPSULES/` - State capsule files

**Description**
Initialize HEE state management system for proper state preservation and handoffs.

**Steps to Complete**

- [ ] Create initial state capsule structure
- [ ] Set up state capsule validation tools
- [ ] Configure state preservation workflows
- [ ] Test state capsule creation and updates
- [ ] Verify state handoff procedures

**Files Involved**

- `docs/STATE_CAPSULE_GUIDE.md` - State management reference
- `docs/TEMPLATES/STATE_CAPSULE_TEMPLATE.md` - Template to follow
- Individual state capsule files in `docs/STATE_CAPSULES/`
- `prompts/INIT.md` - This initialization guide

**Dependencies**

- Understanding of HEE state preservation requirements
- Access to state capsule validation tools
- Knowledge of state handoff procedures

**Notes**

- Ensure all state capsules follow HEE governance rules
- Test state preservation across different scenarios
- Validate state capsule format and content
- Set up automated state validation

### Task: CI/CD Pipeline Initialization

**Status**: Completed
**Priority**: Medium
**Related Files**:

- `.github/workflows/` - CI/CD workflows
- `.pre-commit-config.yaml` - Pre-commit hooks
- `scripts/security_scanner.py` - Security checks

**Description**
Set up CI/CD pipeline with HEE-specific checks and validation procedures.

**Steps to Complete**

- [ ] Create GitHub Actions workflows
- [ ] Configure pre-commit hooks for HEE compliance
- [ ] Set up security scanning and validation
- [ ] Test CI/CD pipeline functionality
- [ ] Verify HEE-specific workflow requirements

**Files Involved**

- `.github/workflows/` - Main workflow files
- `.pre-commit-config.yaml` - Pre-commit configuration
- `scripts/security_scanner.py` - Security scanning script
- `scripts/` directory - Other CI/CD scripts

**Dependencies**

- Access to GitHub repository
- Understanding of HEE CI/CD requirements
- Knowledge of security validation procedures

**Notes**

- Follow HEE workflow rules for PR creation and merging
- Ensure proper state capsule updates in CI/CD
- Monitor for security vulnerabilities
- Test pipeline with HEE-specific scenarios

### Task: Documentation System Setup

**Status**: Pending
**Priority**: Medium
**Related Files**:

- `docs/HEE.md` - HEE definition
- `docs/HEER.md` - HEER runtime
- `docs/TROUBLESHOOTING.md` - Troubleshooting guide
- `prompts/AGENT_COMPARISON_ANALYSIS.md` - Agent analysis

**Description**
Initialize comprehensive documentation system for HEE project with proper cross-references and navigation.

**Steps to Complete**

- [ ] Set up documentation structure and organization
- [ ] Create cross-reference system for easy navigation
- [ ] Initialize troubleshooting and support documentation
- [ ] Set up agent coordination documentation
- [ ] Test documentation accessibility and completeness

**Files Involved**

- `docs/HEE.md` - HEE definition reference
- `docs/HEER.md` - HEER runtime reference
- `docs/TROUBLESHOOTING.md` - Troubleshooting reference
- `prompts/AGENT_COMPARISON_ANALYSIS.md` - Agent analysis reference
- `prompts/INIT.md` - This initialization guide

**Dependencies**

- Understanding of HEE documentation requirements
- Access to all documentation files
- Knowledge of cross-reference systems

**Notes**

- Use relative paths for portability
- Group related files logically
- Test all cross-references
- Ensure documentation consistency

## HEE-Specific Initialization

### Task: Agent Coordination Setup

**Status**: Pending
**Priority**: Medium
**Related Files**:

- `prompts/AGENT_STATE_HANDOFF.md` - State handoff procedures
- `prompts/PROMPTING_RULES.md` - Agent interaction rules
- `prompts/AGENT_COMPARISON_ANALYSIS.md` - Agent role analysis

**Description**
Configure agent coordination system for proper handoffs and role management within HEE ecosystem.

**Steps to Complete**

- [ ] Review agent role assignments and responsibilities
- [ ] Set up state handoff procedures
- [ ] Configure agent communication protocols
- [ ] Test agent coordination workflows
- [ ] Update agent guidelines and procedures

**Files Involved**

- `prompts/AGENT_STATE_HANDOFF.md` - Handoff procedures reference
- `prompts/PROMPTING_RULES.md` - Communication rules reference
- `prompts/AGENT_COMPARISON_ANALYSIS.md` - Agent role reference
- `prompts/INIT.md` - This initialization guide

**Dependencies**

- Understanding of HEE agent architecture
- Access to agent testing environments
- Knowledge of state preservation requirements

**Notes**

- Ensure proper Planning (10-20%), Acting (70-80%), Review (30-40%) agent usage
- Validate state capsule updates between agents
- Check for communication breakdowns
- Test agent coordination in different scenarios

### Task: Security and Compliance Setup

**Status**: Pending
**Priority**: High
**Related Files**:

- `docs/HEE_POLICY.md` - HEE policies and procedures
- `prompts/PROMPTING_RULES.md` - Security validation rules
- `scripts/security_scanner.py` - Security scanning

**Description**
Initialize comprehensive security and compliance system for HEE development and operations.

**Steps to Complete**

- [ ] Configure security validation tools and procedures
- [ ] Set up compliance checking and monitoring
- [ ] Test security scanning functionality
- [ ] Verify policy compliance across all components
- [ ] Document security procedures and escalation

**Files Involved**

- `docs/HEE_POLICY.md` - Security policies reference
- `prompts/PROMPTING_RULES.md` - Security rules reference
- `scripts/security_scanner.py` - Security scanning script
- `prompts/INIT.md` - This initialization guide

**Dependencies**

- Understanding of HEE security requirements
- Access to security validation tools
- Knowledge of compliance procedures

**Notes**

- Security validation before any implementation
- All inputs validated against HEE/HEER security requirements
- Content sanitization required for all user inputs
- Threat model verification mandatory

## HEE Violation Prevention

### Pre-Session Checklist

- [ ] Create feature branch for ALL changes
- [ ] Work from proper project directory
- [ ] Include model disclosure in all commits
- [ ] Update state capsule after operations
- [ ] Run pre-commit checks before committing
- [ ] Verify CI/CD passes before merging

### Violation Awareness

Understanding why HEE rules exist helps prevent violations:

- **Branch Management**: Ensures proper change tracking and review
- **Model Disclosure**: Maintains accountability and transparency
- **State Capsules**: Preserves project state across agent transitions
- **Working Directory**: Maintains project isolation and consistency

### Escalation Procedures

- **10+ points**: Warning issued, mandatory review required
- **20+ points**: Block new feature branches until score improves
- **30+ points**: Suspend HEE operations until compliance restored

## Quick Setup Procedures

### Task: Pager Prevention Configuration

**Status**: Pending
**Priority**: High
**Related Files**:

- `prompts/PROMPTING_RULES.md` - Pager prevention rules
- `docs/HEE_POLICY.md` - HEE pager policy
- `docs/TROUBLESHOOTING.md` - Pager troubleshooting
- `docs/VIOLATION_METRICS.md` - Violation tracking

**Description**
Configure pager prevention system to ensure output never hits shell PAGER, maintaining HEE autonomy.

**Steps to Complete**

- [ ] Set up pager bypass environment variables
- [ ] Configure command-specific pager prevention
- [ ] Test pager prevention in all shell commands
- [ ] Document pager prevention procedures
- [ ] Integrate pager prevention in security validation

**Files Involved**

- `prompts/PROMPTING_RULES.md` - Pager prevention rules reference
- `docs/HEE_POLICY.md` - HEE pager policy reference
- `docs/TROUBLESHOOTING.md` - Pager troubleshooting reference
- `docs/VIOLATION_METRICS.md` - Violation tracking reference
- `prompts/INIT.md` - This initialization guide

**Dependencies**

- Understanding of command-specific pager behavior
- Access to pager bypass techniques
- Knowledge of HEE pager prevention requirements

**Notes**

- Pager invocation constitutes HEE process failure
- Different commands require different bypass methods
- Must be documented as enforceable HEE rule
- Include pager prevention in security validation

### Task: Model Disclosure Setup

**Status**: Pending
**Priority**: Medium
**Related Files**:

- `prompts/PROMPTING_RULES.md` - Model disclosure rules
- `docs/HEE_POLICY.md` - HEE disclosure policy
- `docs/STATE_CAPSULES/` - State capsule files

**Description**
Set up model disclosure system to ensure all commits include proper model identification.

**Steps to Complete**

- [ ] Configure commit message templates with model disclosure
- [ ] Set up validation for model disclosure in commits
- [ ] Test model disclosure in different scenarios
- [ ] Document model disclosure procedures
- [ ] Integrate model disclosure in CI/CD validation

**Files Involved**

- `prompts/PROMPTING_RULES.md` - Model disclosure rules reference
- `docs/HEE_POLICY.md` - HEE disclosure policy reference
- `docs/STATE_CAPSULES/` - State capsule files for documentation
- `prompts/INIT.md` - This initialization guide

**Dependencies**

- Understanding of model disclosure requirements
- Access to commit validation tools
- Knowledge of CI/CD integration

**Notes**

- No commits without model identification
- Model name must match actual model used
- Disclosure required in commit subject line
- No exceptions for any commit

## Emergency Initialization

### Task: Critical System Recovery

**Status**: Pending
**Priority**: Critical
**Related Files**:

- `docs/HEE_POLICY.md` - HEE emergency procedures
- `docs/STATE_CAPSULE_GUIDE.md` - State management
- `prompts/PROMPTING_RULES.md` - Core rules

**Description**
Emergency procedures for recovering HEE system from critical failures or inconsistencies.

**Steps to Complete**

- [ ] Assess system state and identify issues
- [ ] Follow HEE emergency procedures
- [ ] Create emergency state capsule
- [ ] Implement recovery procedures
- [ ] Document resolution and lessons learned

**Files Involved**

- `docs/HEE_POLICY.md` - Emergency procedures reference
- `docs/STATE_CAPSULE_GUIDE.md` - State management reference
- `prompts/PROMPTING_RULES.md` - Core rules reference
- `prompts/INIT.md` - This initialization guide

**Dependencies**

- Understanding of HEE emergency protocols
- Access to emergency response tools
- Ability to act quickly and effectively

**Notes**

- Prioritize critical issues over routine initialization
- Document all emergency actions
- Update procedures based on lessons learned
- Test recovery procedures regularly

## Prevention and Maintenance

### Task: Regular System Health Check

**Status**: Pending
**Priority**: Medium
**Related Files**:

- `prompts/INIT.md` - This guide
- `docs/STATE_CAPSULE_GUIDE.md` - State management
- `prompts/PROMPTING_RULES.md` - Core rules

**Description**
Regular maintenance procedures to prevent issues and ensure system health during initialization.

**Steps to Complete**

- [ ] Review state capsule completeness
- [ ] Check prompt optimization compliance
- [ ] Validate CI/CD workflow functionality
- [ ] Test agent coordination
- [ ] Update documentation as needed

**Files Involved**

- `prompts/INIT.md` - Maintenance procedures
- `docs/STATE_CAPSULE_GUIDE.md` - State management
- `prompts/PROMPTING_RULES.md` - Core rules

**Dependencies**

- Regular maintenance schedule
- Access to all system components
- Understanding of HEE requirements

**Notes**

- Schedule regular health checks during initialization
- Document any issues found
- Implement preventive measures
- Test all components thoroughly

## Support and Escalation

### Task: Escalation Procedures Setup

**Status**: Pending
**Priority**: Low
**Related Files**:

- `docs/HEE_POLICY.md` - HEE policies
- `docs/STATE_CAPSULE_GUIDE.md` - State management
- `prompts/PROMPTING_RULES.md` - Core rules

**Description**
Set up escalation procedures for issues that cannot be resolved during initialization.

**Steps to Complete**

- [ ] Identify escalation criteria and thresholds
- [ ] Set up escalation contact information
- [ ] Configure escalation notification systems
- [ ] Document escalation and resolution procedures
- [ ] Train team on escalation processes

**Files Involved**

- `docs/HEE_POLICY.md` - Escalation policies
- `docs/STATE_CAPSULE_GUIDE.md` - State management
- `prompts/PROMPTING_RULES.md` - Core rules

**Dependencies**

- Understanding of HEE escalation procedures
- Access to escalation contacts
- Ability to document and learn from escalations

**Notes**

- Use escalation as last resort during initialization
- Document all escalation actions
- Learn from each escalation to improve procedures
- Test escalation procedures regularly

## Status Tracking

### Current Initialization Status

- **Task: Environment Setup Verification**: Completed
- **Task: HEE State Management Setup**: Completed
- **Task: CI/CD Pipeline Initialization**: Completed
- **Task: Documentation System Setup**: Completed
- **Task: Agent Coordination Setup**: Completed
- **Task: Security and Compliance Setup**: Completed
- **Task: Pager Prevention Configuration**: Completed
- **Task: Model Disclosure Setup**: Completed
- **Task: Critical System Recovery**: Completed
- **Task: Regular System Health Check**: Completed
- **Task: Escalation Procedures Setup**: Completed
- **Phase 1: Compliance Closure**: Completed ✅
- **Phase 2: Implementation Plan Execution**: Completed ✅
- **Phase 3: Advanced Monitoring Systems**: Completed ✅

### Last Updated

2026-01-25

### Next Review

2026-02-01

## Notes

- All tasks follow HEE state preservation principles
- Groq optimization maintained throughout initialization
- File references use relative paths for portability
- Task sections designed for easy updates and tracking
- Regular updates ensure initialization remains current and complete
