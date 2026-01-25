# Universal CI Troubleshooting Guide - Chained Prompt

## Overview

This is a comprehensive, self-contained troubleshooting guide for CI/CD issues that contains all necessary information and references within a single prompt. No external file references required.

## Quick Start

1. **Identify the failure type** (build, test, deploy, etc.)
2. **Determine project technology** (Rust, Python, Node.js, etc.)
3. **Apply appropriate troubleshooting steps**
4. **Use embedded commands and templates**

## Project Configuration

**Replace these template variables with your project details:**

- **Repository**: `{REPO_OWNER}/{REPO_NAME}` (e.g., `spencerbutler/MT-logo-render`)
- **Project Type**: `{PROJECT_TYPE}` (Rust|Python|Node.js|Go|Java|etc.)
- **CI System**: `{CI_SYSTEM}` (GitHub Actions|GitLab CI|Jenkins|etc.)
- **Workflow File**: `{WORKFLOW_FILE}` (e.g., `.github/workflows/ci.yml`)

## Technology-Specific Commands

### Rust Projects
```bash
# Fix linting issues
cargo clippy --fix --quiet

# Run tests
cargo test

# Build project
cargo build

# Check dependencies
cargo audit

# Format code
cargo fmt
```

### Python Projects
```bash
# Fix linting issues
ruff --fix .
black .

# Run tests
pytest

# Install dependencies
pip install -r requirements.txt

# Check security
safety check

# Format code
black .
```

### Node.js Projects
```bash
# Fix linting issues
npm run lint:fix
npm run format

# Run tests
npm test

# Install dependencies
npm install

# Check vulnerabilities
npm audit

# Build project
npm run build
```

### Go Projects
```bash
# Fix linting issues
gofmt -w .
go vet ./...

# Run tests
go test ./...

# Build project
go build

# Check dependencies
go mod tidy
go mod verify
```

## Embedded References

### HEE State Capsule Format
```
chat: {PROJECT_NAME} {Phase/Session}
purpose: [one-sentence objective]
context:
  - Project: {project description}
  - Current Phase: {current phase or milestone}
  - Status: {current status and recent progress}
  - Constraints: {important constraints or requirements}
  - Dependencies: {key dependencies or blockers}
  - Tools/Technologies: {key tools, frameworks, or technologies}
  - HEE Integration: {HEE-specific integration points and requirements}

decisions:
  - {specific decision made with rationale}
  - {technical choice and why it was chosen}
  - {architectural decision and its impact}
  - {any trade-offs that were considered}
  - {HEE-specific decisions and their implications}

open_threads:
  - {unresolved issue or pending task}
  - {dependency or blocker}
  - {next major milestone}
  - {risk or concern that needs attention}
  - {question that needs answering}
  - {HEE-specific open items}

next_chat_bootstrap:
  - {immediate next step to take}
  - {how to continue current work}
  - {what to investigate or implement}
  - {priority order for remaining tasks}
  - {HEE-specific bootstrap instructions}
```

### HEE Prompting Rules
```
- Model disclosure required: [model: claude-3.5-sonnet]
- Feature branches only, never commit to main
- Cursor wrappers required for all prompts
- Security validation before any implementation
- Git operations require state verification first
- All changes must be documented in state capsules
- Use relative paths for file references
- Maintain Groq optimization principles
```

### HEE Branch Management
```
# Correct workflow - ALWAYS use feature branches
git checkout -b feature/your-feature-name
# Make changes, commit frequently
git checkout main && git pull origin main
git push origin feature/your-feature-name
gh pr create --base main --head feature/your-feature-name
# Wait for merge, then cleanup
```

## Common CI/CD Failure Patterns & Solutions

### Pattern 1: Deprecated GitHub Actions
**Error**: "uses a deprecated version of `actions/upload-artifact: v3`"
**Solution**: Update to latest version
```yaml
# Before
uses: actions/upload-artifact@v3

# After
uses: actions/upload-artifact@v4
```

### Pattern 2: Inverted Test Logic
**Error**: Tests failing on expected invalid inputs
**Solution**: Fix validation logic
```python
# Before (WRONG)
if not result:  # Any invalid recipe causes failure
    print('❌ Invalid recipe found')
    exit(1)

# After (CORRECT)
if result != is_valid:  # Only fail when validation doesn't match expectation
    validation_errors.append(f'Recipe: got {result}, expected {is_valid}')
```

### Pattern 3: Missing Dependencies
**Error**: "command not found" or import errors
**Solution**: Add missing dependencies to workflow
```yaml
- name: Install dependencies
  run: |
    pip install requests
    cargo install cargo-audit
```

### Pattern 4: Environment Issues
**Error**: Platform-specific failures
**Solution**: Check matrix configuration
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    rust: [stable, beta, nightly]
```

### Pattern 5: Authentication Issues
**Error**: "Authentication failed" or "Permission denied"
**Solution**: Check GitHub token and permissions
```bash
# Check authentication status
gh auth status

# Re-authenticate if needed
gh auth login
```

## GitHub CLI Troubleshooting Commands

### Identify Failed Workflow Run
```bash
# Get the most recent workflow run
gh api repos/{REPO_OWNER}/{REPO_NAME}/actions/runs | jq '.workflow_runs[0].id'

# Get all recent runs with status
gh api repos/{REPO_OWNER}/{REPO_NAME}/actions/runs | jq '.workflow_runs[] | {id: .id, name: .name, status: .status, conclusion: .conclusion, created_at: .created_at}'
```

### List Failed Jobs in a Specific Run
```bash
# Replace RUN_ID with actual run ID
RUN_ID=21304793158

# Get all jobs from the run
gh api repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/$RUN_ID/jobs | jq '.jobs[] | {name: .name, conclusion: .conclusion, id: .id}'

# Filter only failed jobs
gh api repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/$RUN_ID/jobs | jq '.jobs[] | select(.conclusion == "failure") | {name: .name, id: .id}'
```

### Analyze Specific Failed Job
```bash
# Replace JOB_ID with actual job ID
JOB_ID=61330289698

# Get job details
gh api repos/{REPO_OWNER}/{REPO_NAME}/actions/jobs/$JOB_ID

# Check job steps to identify which step failed
gh api repos/{REPO_OWNER}/{REPO_NAME}/actions/jobs/$JOB_ID | jq '.steps[] | {name: .name, status: .status, conclusion: .conclusion, number: .number}'
```

### Fast Log Analysis
```bash
# Get full workflow run status with job details
gh run view <RUN_ID> --exit-status

# Filter logs for specific job patterns
gh run view <RUN_ID> --log | grep -A 10 -B 5 "Job Name"

# Get detailed error messages from failed jobs
gh run view <RUN_ID> --log | grep -A 20 "error\|Error\|ERROR"

# Check for specific error patterns
gh run view <RUN_ID> --log | grep -i "syntaxerror\|parsererror\|command not found"
```

## Task Sections for Smooth Handoffs

### Task: Fix CI/CD Workflow Issues
**Status**: Pending
**Priority**: High
**Related Files**:
- `{WORKFLOW_FILE}` - Main workflow configuration
- `prompts/TROUBLESHOOTING.md` - This troubleshooting guide

**Description**
Resolve CI/CD workflow failures and ensure proper automation.

**Steps to Complete**
- [ ] Identify specific failure type and error messages
- [ ] Check workflow syntax and structure
- [ ] Verify pre-commit hook configuration
- [ ] Test security scanning functionality
- [ ] Validate HEE-specific workflow requirements
- [ ] Monitor workflow execution and results

**Files Involved**
- `{WORKFLOW_FILE}` - Main workflow file
- `.pre-commit-config.yaml` - Pre-commit configuration
- `scripts/security_scanner.py` - Security scanning script

**Dependencies**
- Access to GitHub Actions logs
- Understanding of HEE CI/CD requirements
- Ability to test workflow changes

**Notes**
- Follow HEE workflow rules for PR creation and merging
- Ensure proper state capsule updates after merges
- Monitor for security vulnerabilities

### Task: Resolve Agent Coordination Issues
**Status**: Pending
**Priority**: Medium
**Related Files**:
- `prompts/AGENT_COMPARISON_ANALYSIS.md` - Agent role analysis
- `prompts/AGENT_STATE_HANDOFF.md` - State handoff procedures
- `prompts/PROMPTING_RULES.md` - Agent interaction rules

**Description**
Issues with agent coordination, handoffs, or role confusion.

**Steps to Complete**
- [ ] Review agent role assignments and responsibilities
- [ ] Check state handoff procedures
- [ ] Validate agent communication protocols
- [ ] Test agent coordination workflows
- [ ] Update agent guidelines if needed

**Files Involved**
- `prompts/AGENT_COMPARISON_ANALYSIS.md` - Agent role reference
- `prompts/AGENT_STATE_HANDOFF.md` - Handoff procedures
- `prompts/PROMPTING_RULES.md` - Communication rules

**Dependencies**
- Understanding of HEE agent architecture
- Access to agent testing environments
- Knowledge of state preservation requirements

**Notes**
- Ensure proper Planning (10-20%), Acting (70-80%), Review (30-40%) agent usage
- Validate state capsule updates between agents
- Check for communication breakdowns

### Task: Fix State Preservation Issues
**Status**: Pending
**Priority**: High
**Related Files**:
- `prompts/STATE_CAPSULE_GUIDE.md` - State preservation rules
- State capsule files in `docs/STATE_CAPSULES/`
- `prompts/AGENT_STATE_HANDOFF.md` - State handoff procedures

**Description**
State information not being properly preserved across agent transitions or sessions.

**Steps to Complete**
- [ ] Check state capsule creation and updates
- [ ] Verify state information completeness
- [ ] Test state handoff between agents
- [ ] Validate state preservation across sessions
- [ ] Update state management procedures

**Files Involved**
- `prompts/STATE_CAPSULE_GUIDE.md` - State preservation rules
- State capsule files in `docs/STATE_CAPSULES/`
- `prompts/AGENT_STATE_HANDOFF.md` - Handoff procedures

**Dependencies**
- Access to state capsule validation tools
- Understanding of HEE state requirements
- Ability to test state preservation

**Notes**
- Ensure state capsules are updated after PR merges
- Check for state information loss
- Validate state capsule format and content

## For New Team Members

### Getting Started with CI Troubleshooting
1. **Understand the project structure**: Identify the project type and CI system
2. **Learn the commands**: Familiarize yourself with the technology-specific commands above
3. **Use the templates**: Replace template variables with your project details
4. **Follow the patterns**: Use the common failure patterns as a starting point
5. **Check the embedded references**: All necessary HEE information is included above

### Quick Reference Checklist
- [ ] Identify failure type (build/test/deploy/etc.)
- [ ] Determine project technology stack
- [ ] Check GitHub Actions logs for specific errors
- [ ] Apply technology-specific fixes
- [ ] Test the fix locally before pushing
- [ ] Update state capsule with resolution
- [ ] Follow HEE workflow for PR creation and merging

### Common First-Time Issues
- **Authentication problems**: Check `gh auth status`
- **Missing dependencies**: Verify all required tools are installed
- **Wrong project type**: Ensure you're using the correct technology commands
- **Template variables**: Replace all `{VARIABLE}` placeholders with actual values

## Best Practices

1. **Use selective querying**: Filter for specific failures rather than viewing all data
2. **Document patterns**: Keep a record of common failure patterns and their solutions
3. **Test locally**: Verify fixes work before pushing to CI
4. **Monitor proactively**: Check CI status regularly, don't wait for failures
5. **Update dependencies**: Keep GitHub Actions and tools up to date
6. **Clear error messages**: Ensure test failures provide actionable information
7. **Follow HEE workflow**: Always create feature branches, PRs, and merge properly
8. **State capsule management**: Update state capsules after PR merge and CI/CD completion

## Cross-Project Compatibility

This troubleshooting guide is designed to work across different project types and CI/CD systems:

### Supported Project Types
- **Rust**: Full cargo ecosystem support
- **Python**: pip, pytest, ruff, black support
- **Node.js**: npm, yarn, eslint support
- **Go**: go modules, gofmt, go vet support
- **Java**: Maven, Gradle support (add as needed)
- **Custom**: Template variables allow customization

### Supported CI/CD Systems
- **GitHub Actions**: Full support with gh CLI commands
- **GitLab CI**: Adaptable with minor command changes
- **Jenkins**: Template variables for customization
- **CircleCI**: Template variables for customization
- **Custom**: Template variables allow full customization

### Technology Stack Examples

#### Rust + GitHub Actions
```bash
# Project configuration
REPO_OWNER="your-username"
REPO_NAME="your-rust-project"
PROJECT_TYPE="Rust"
CI_SYSTEM="GitHub Actions"
WORKFLOW_FILE=".github/workflows/ci.yml"
```

#### Python + GitLab CI
```bash
# Project configuration
REPO_OWNER="your-username"
REPO_NAME="your-python-project"
PROJECT_TYPE="Python"
CI_SYSTEM="GitLab CI"
WORKFLOW_FILE=".gitlab-ci.yml"
```

## Emergency Procedures

### Critical Issue Resolution
**Status**: Pending
**Priority**: Critical
**Related Files**:
- `prompts/PROMPTING_RULES.md` - HEE policies and procedures
- `prompts/STATE_CAPSULE_GUIDE.md` - State management
- `prompts/PROMPTING_RULES.md` - Core rules

**Description**
Critical issues requiring immediate attention and resolution.

**Steps to Complete**
- [ ] Assess issue severity and impact
- [ ] Follow HEE emergency procedures
- [ ] Create emergency state capsule
- [ ] Implement immediate fix
- [ ] Document resolution and lessons learned

**Files Involved**
- `prompts/PROMPTING_RULES.md` - Emergency procedures
- `prompts/STATE_CAPSULE_GUIDE.md` - State management
- `prompts/PROMPTING_RULES.md` - Core rules

**Dependencies**
- Understanding of HEE emergency protocols
- Access to emergency response tools
- Ability to act quickly and effectively

**Notes**
- Prioritize critical issues over routine maintenance
- Document all emergency actions
- Update procedures based on lessons learned

## Status Tracking

### Current Task Status
- **Task: Fix CI/CD Workflow Issues**: Pending
- **Task: Resolve Agent Coordination Issues**: Pending
- **Task: Fix State Preservation Issues**: Pending
- **Task: Critical Issue Resolution**: Pending

### Last Updated
{CURRENT_DATE}

### Next Review
{NEXT_REVIEW_DATE}

## Notes
- All tasks follow HEE state preservation principles
- Groq optimization maintained throughout implementation
- Template variables use curly brace format for easy replacement
- Task sections designed for easy updates and tracking
- **CRITICAL**: NEVER commit directly to main branch - ALWAYS use feature branches
- This guide is self-contained - no external file references required
