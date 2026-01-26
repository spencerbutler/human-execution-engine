# Universal CI Troubleshooting Guide - Template

## Overview

This is a template version of the comprehensive troubleshooting guide. Replace all template variables (marked with `{}`) with your project-specific values before use.

## Template Variables

**Required replacements before using this template:**

```yaml
# Repository Information
{REPO_OWNER}: "your-username"                    # GitHub/GitLab username
{REPO_NAME}: "your-repo-name"                   # Repository name
{FULL_REPO_PATH}: "{REPO_OWNER}/{REPO_NAME}"    # Full repository path

# Project Information
{PROJECT_NAME}: "Your Project Name"             # Human-readable project name
{PROJECT_TYPE}: "Rust|Python|Node.js|Go|Java"   # Primary technology stack
{PROJECT_DESCRIPTION}: "Brief project description"

# CI/CD Configuration
{CI_SYSTEM}: "GitHub Actions|GitLab CI|Jenkins|CircleCI"  # CI/CD platform
{WORKFLOW_FILE}: ".github/workflows/ci.yml"     # Path to main workflow file
{BRANCH_NAME}: "main|master|develop"            # Primary branch name

# Technology Stack
{BUILD_COMMAND}: "cargo build|npm run build|go build"  # Build command for your project
{TEST_COMMAND}: "cargo test|npm test|go test"   # Test command for your project
{LINT_COMMAND}: "cargo clippy|ruff|eslint"      # Linting command for your project
{FORMAT_COMMAND}: "cargo fmt|black|prettier"    # Code formatting command

# HEE Configuration (if using HEE)
{HEE_INTEGRATION}: "enabled|disabled"           # Whether HEE is used
{STATE_CAPSULE_PATH}: "docs/history/state_capsules/"   # Path to state capsules
{PROMPT_PATH}: "prompts/"                       # Path to prompt files

# Date Information
{CURRENT_DATE}: "2026-01-24"                    # Current date
{NEXT_REVIEW_DATE}: "2026-01-31"                # Next review date
```

## Quick Start

1. **Replace all template variables** with your project-specific values
2. **Identify the failure type** (build, test, deploy, etc.)
3. **Determine project technology** (use the technology-specific commands below)
4. **Apply appropriate troubleshooting steps**
5. **Use embedded commands and templates**

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

### Java Projects

```bash
# Fix linting issues
./gradlew check
mvn checkstyle:check

# Run tests
./gradlew test
mvn test

# Build project
./gradlew build
mvn clean package

# Check dependencies
./gradlew dependencyCheckAnalyze
mvn dependency:tree
```

## Embedded References

### HEE State Capsule Format (if using HEE)

```
chat: {PROJECT_NAME} {Phase/Session}
purpose: [one-sentence objective]
context:
  - Project: {PROJECT_DESCRIPTION}
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

### HEE Prompting Rules (if using HEE)

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

### HEE Branch Management (if using HEE)

```
# Correct workflow - ALWAYS use feature branches
git checkout -b feature/your-feature-name
# Make changes, commit frequently
git checkout {BRANCH_NAME} && git pull origin {BRANCH_NAME}
git push origin feature/your-feature-name
gh pr create --base {BRANCH_NAME} --head feature/your-feature-name
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

## CI/CD System-Specific Commands

### GitHub Actions

```bash
# Get the most recent workflow run
gh api repos/{FULL_REPO_PATH}/actions/runs | jq '.workflow_runs[0].id'

# Get all recent runs with status
gh api repos/{FULL_REPO_PATH}/actions/runs | jq '.workflow_runs[] | {id: .id, name: .name, status: .status, conclusion: .conclusion, created_at: .created_at}'

# List failed jobs in a specific run
RUN_ID=21304793158
gh api repos/{FULL_REPO_PATH}/actions/runs/$RUN_ID/jobs | jq '.jobs[] | select(.conclusion == "failure") | {name: .name, id: .id}'

# Fast log analysis
gh run view <RUN_ID> --log | grep -A 10 -B 5 "Job Name"
```

### GitLab CI

```bash
# Get pipeline status
curl --header "PRIVATE-TOKEN: {GITLAB_TOKEN}" "https://gitlab.com/api/v4/projects/{FULL_REPO_PATH}/pipelines"

# Get job details
curl --header "PRIVATE-TOKEN: {GITLAB_TOKEN}" "https://gitlab.com/api/v4/projects/{FULL_REPO_PATH}/jobs"

# Download job logs
curl --header "PRIVATE-TOKEN: {GITLAB_TOKEN}" "https://gitlab.com/api/v4/projects/{FULL_REPO_PATH}/jobs/{JOB_ID}/trace"
```

### Jenkins

```bash
# Get job status
curl -s "http://{JENKINS_URL}/job/{JOB_NAME}/lastBuild/api/json"

# Get console output
curl -s "http://{JENKINS_URL}/job/{JOB_NAME}/lastBuild/consoleText"

# Trigger build
curl -X POST "http://{JENKINS_URL}/job/{JOB_NAME}/build" --user "{USERNAME}:{API_TOKEN}"
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
- [ ] Validate HEE-specific workflow requirements (if applicable)
- [ ] Monitor workflow execution and results

**Files Involved**

- `{WORKFLOW_FILE}` - Main workflow file
- `.pre-commit-config.yaml` - Pre-commit configuration
- `scripts/security_scanner.py` - Security scanning script

**Dependencies**

- Access to CI/CD logs
- Understanding of project CI/CD requirements
- Ability to test workflow changes

**Notes**

- Follow project workflow rules for PR creation and merging
- Ensure proper state capsule updates after merges (if using HEE)
- Monitor for security vulnerabilities

### Task: Resolve Agent Coordination Issues (if using HEE)

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

### Task: Fix State Preservation Issues (if using HEE)

**Status**: Pending
**Priority**: High
**Related Files**:

- `prompts/STATE_CAPSULE_GUIDE.md` - State preservation rules
- State capsule files in `{STATE_CAPSULE_PATH}`
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
- State capsule files in `{STATE_CAPSULE_PATH}`
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

1. **Replace all template variables** with your project-specific values
2. **Understand the project structure**: Identify the project type and CI system
3. **Learn the commands**: Familiarize yourself with the technology-specific commands above
4. **Use the templates**: Replace template variables with your project details
5. **Follow the patterns**: Use the common failure patterns as a starting point
6. **Check the embedded references**: All necessary information is included above

### Quick Reference Checklist

- [ ] Replace all template variables with actual values
- [ ] Identify failure type (build/test/deploy/etc.)
- [ ] Determine project technology stack
- [ ] Check CI/CD logs for specific errors
- [ ] Apply technology-specific fixes
- [ ] Test the fix locally before pushing
- [ ] Update state capsule with resolution (if using HEE)
- [ ] Follow project workflow for PR creation and merging

### Common First-Time Issues

- **Authentication problems**: Check `gh auth status` or equivalent for your CI system
- **Missing dependencies**: Verify all required tools are installed
- **Wrong project type**: Ensure you're using the correct technology commands
- **Template variables**: Replace all `{VARIABLE}` placeholders with actual values
- **CI system differences**: Adapt commands for your specific CI/CD platform

## Best Practices

1. **Use selective querying**: Filter for specific failures rather than viewing all data
2. **Document patterns**: Keep a record of common failure patterns and their solutions
3. **Test locally**: Verify fixes work before pushing to CI
4. **Monitor proactively**: Check CI status regularly, don't wait for failures
5. **Update dependencies**: Keep CI/CD tools and actions up to date
6. **Clear error messages**: Ensure test failures provide actionable information
7. **Follow project workflow**: Always create feature branches, PRs, and merge properly
8. **State capsule management**: Update state capsules after PR merge and CI/CD completion (if using HEE)

## Cross-Project Compatibility

This troubleshooting guide template is designed to work across different project types and CI/CD systems:

### Supported Project Types

- **Rust**: Full cargo ecosystem support
- **Python**: pip, pytest, ruff, black support
- **Node.js**: npm, yarn, eslint support
- **Go**: go modules, gofmt, go vet support
- **Java**: Maven, Gradle support
- **Custom**: Template variables allow customization

### Supported CI/CD Systems

- **GitHub Actions**: Full support with gh CLI commands
- **GitLab CI**: Adaptable with minor command changes
- **Jenkins**: Template variables for customization
- **CircleCI**: Template variables for customization
- **Azure DevOps**: Template variables for customization
- **Custom**: Template variables allow full customization

### Technology Stack Examples

#### Rust + GitHub Actions

```yaml
# Project configuration
REPO_OWNER: "your-username"
REPO_NAME: "your-rust-project"
PROJECT_NAME: "Your Rust Project"
PROJECT_TYPE: "Rust"
CI_SYSTEM: "GitHub Actions"
WORKFLOW_FILE: ".github/workflows/ci.yml"
BUILD_COMMAND: "cargo build"
TEST_COMMAND: "cargo test"
LINT_COMMAND: "cargo clippy"
```

#### Python + GitLab CI

```yaml
# Project configuration
REPO_OWNER: "your-username"
REPO_NAME: "your-python-project"
PROJECT_NAME: "Your Python Project"
PROJECT_TYPE: "Python"
CI_SYSTEM: "GitLab CI"
WORKFLOW_FILE: ".gitlab-ci.yml"
BUILD_COMMAND: "pip install -r requirements.txt"
TEST_COMMAND: "pytest"
LINT_COMMAND: "ruff"
```

#### Node.js + Jenkins

```yaml
# Project configuration
REPO_OWNER: "your-username"
REPO_NAME: "your-node-project"
PROJECT_NAME: "Your Node.js Project"
PROJECT_TYPE: "Node.js"
CI_SYSTEM: "Jenkins"
WORKFLOW_FILE: "Jenkinsfile"
BUILD_COMMAND: "npm run build"
TEST_COMMAND: "npm test"
LINT_COMMAND: "npm run lint"
```

## Emergency Procedures

### Critical Issue Resolution

**Status**: Pending
**Priority**: Critical
**Related Files**:

- `prompts/PROMPTING_RULES.md` - HEE policies and procedures (if using HEE)
- `prompts/STATE_CAPSULE_GUIDE.md` - State management (if using HEE)
- `prompts/PROMPTING_RULES.md` - Core rules (if using HEE)

**Description**
Critical issues requiring immediate attention and resolution.

**Steps to Complete**

- [ ] Assess issue severity and impact
- [ ] Follow emergency procedures for your project
- [ ] Create emergency state capsule (if using HEE)
- [ ] Implement immediate fix
- [ ] Document resolution and lessons learned

**Files Involved**

- Project-specific emergency procedures
- State capsule files (if using HEE)
- Core project rules

**Dependencies**

- Understanding of project emergency protocols
- Access to emergency response tools
- Ability to act quickly and effectively

**Notes**

- Prioritize critical issues over routine maintenance
- Document all emergency actions
- Update procedures based on lessons learned

## Status Tracking

### Current Task Status

- **Task: Fix CI/CD Workflow Issues**: Pending
- **Task: Resolve Agent Coordination Issues**: Pending (if using HEE)
- **Task: Fix State Preservation Issues**: Pending (if using HEE)
- **Task: Critical Issue Resolution**: Pending

### Last Updated

{CURRENT_DATE}

### Next Review

{NEXT_REVIEW_DATE}

## Notes

- All tasks follow project-specific state preservation principles (if applicable)
- Template variables use curly brace format for easy replacement
- Task sections designed for easy updates and tracking
- **CRITICAL**: NEVER commit directly to main branch - ALWAYS use feature branches
- This guide is self-contained - no external file references required
- Replace ALL template variables before using this template

## Authority
Canonical authority: HEE doctrine and repository governance rules.
This prompt is subordinate to docs/doctrine/ and repository policy enforcement.

## Scope
Defines the operating rules and intended usage for this prompt file only.

## Invariants
- Do not contradict docs/doctrine/.
- Prefer minimal diffs; no opportunistic refactors.
- If requirements conflict, escalate rather than invent policy.
