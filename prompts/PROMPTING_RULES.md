# Agent Prompting Rules (human-execution-engine)

## Scope Discipline - RULE ENFORCEMENT ONLY

**NO CODE UNTIL PROMPTS/SPECS ARE MERGED TO MAIN**

- Implementation code forbidden until prompts/spec complete and merged
- Optimize for security validation, not free tier usage
- Apply Groq free tier optimization rules when using Groq models
- No dynamic content generation without spec approval

## Security Discipline - HIGHEST PRIORITY

**SECURITY VALIDATION BEFORE ANY IMPLEMENTATION**

- All inputs validated against HEE/HEER security requirements
- No shell commands without security pre-check
- Content sanitization required for all user inputs
- Threat model verification mandatory

## Plan Adherence - ZERO DEVIATION

**FOLLOW PLAN EXACTLY - NO ASSUMPTIONS**

- Verify repository state before any git operations
- Check file existence before creation/modification
- No references to non-existent components
- Documentation paramount - no undefined references

## Command Safety - VALIDATE BEFORE EXECUTE

**PRE-VALIDATION REQUIRED FOR ALL COMMANDS**

```bash
# Pattern: Validate then execute
[ -f file.txt ] && echo "File exists" || echo "File missing - plan violation"
```

- Syntax validation with `bash -n` for all shell commands
- Path verification before file operations
- Git state verification before repository operations
- No execution without explicit validation

## Content Rules - SANITIZE AND VALIDATE

**ALL CONTENT SUBJECT TO SECURITY RULES**

- Unicode validation for all text inputs
- Control character blocking
- Zero-width character detection
- Safe character normalization

## Git Operations - VERIFY STATE FIRST

## HEE Git/GH Admission Control (Strong)

- Agents MUST NOT run raw mutating `git` / `gh` commands.
- Any mutation MUST be executed via: `scripts/hee_git_ops.sh`
- Liveness gating: if mutation requested while not in ACT tool-mode, emit:
  `BLOCKER: Mutation requested but HEE_TOOL_MODE!=ACT or --act missing. Refusing.`
  then STOP.
- Branch gating: mutations on `main` are forbidden.

Mutation protocol:
- Set `HEE_TOOL_MODE=ACT`
- Use `--act` and `--reason "..."` on every invocation
- Examples:
  - `HEE_TOOL_MODE=ACT scripts/hee_git_ops.sh add --act --reason "stage files" <paths...>`
  - `HEE_TOOL_MODE=ACT scripts/hee_git_ops.sh commit --act --reason "commit changes" -m "..."`

**NEVER ASSUME GIT STATE**

```bash
# Required pattern for all git operations
if [ ! -d .git ]; then
    echo "ERROR: Not a git repository"
    exit 1
fi
# Then proceed with git operations
```

- Repository existence verification mandatory
- Branch state validation required
- Remote verification before push operations
- SSH authentication confirmation required

## File Operations - EXISTENCE CHECKS REQUIRED

**VERIFY BEFORE CREATE/MODIFY/DELETE**

```bash
# Required pattern for file operations
if [ -f target.txt ]; then
    echo "File exists - proceeding with modification"
elif [ ! -d "$(dirname target.txt)" ]; then
    echo "Directory missing - plan violation"
    exit 1
else
    echo "Safe to create file"
fi
```

- Directory existence validation
- File existence checking
- Permission verification
- Safe creation patterns only

## Model Disclosure - MANDATORY

**ALL COMMITS REQUIRE MODEL DISCLOSURE**

```
Pattern: [model: model-name]
Example: [model: claude-3.5-sonnet]
```

- No commits without model identification
- Model name must match actual model used
- Disclosure required in commit subject line
- No exceptions for any commit

## Documentation Enforcement - NO UNDEFINED REFERENCES

**DOCUMENTATION IS PARAMOUNT**

- No references to non-existent files/tools
- All README examples must work immediately
- API documentation must reflect actual implementation
- Specs must be canonical and complete

## Testing Discipline - SECURITY FIRST

**SECURITY VALIDATION BEFORE FUNCTIONALITY**

- Security test vectors run before feature tests
- Input validation tested before business logic
- Compliance checking before integration tests
- No functionality without security coverage

## Integration Rules - VALIDATE COMPATIBILITY

**HEE/HEER COMPLIANCE ENFORCED**

- All changes validated against HEE conceptual model
- HEER runtime contract compliance required
- Breaking changes require ecosystem coordination
- Integration examples must be executable immediately

## Branch Management - FEATURE BRANCHES ONLY

**NEVER COMMIT DIRECTLY TO MAIN**

```bash
# Correct workflow - ALWAYS use feature branches
git checkout -b feature/your-feature-name
# Make changes, commit frequently
git checkout main && git pull origin main
git push origin feature/your-feature-name
gh pr create --base main --head feature/your-feature-name
# Wait for merge, then cleanup
```

- All changes made on feature branches only
- Never commit directly to main branch
- Feature branches named: `feature/description-of-work`
- Delete merged branches immediately to prevent confusion

## Git Workflow - STRUCTURED DEVELOPMENT

**COMMIT FREQUENTLY, PRESERVE STATE**

```bash
# Standard workflow pattern
git checkout -b feature/work-description
# Make logical unit of work
git add specific-files
git commit -m "type: Description of changes [model: claude-3.5-sonnet]"
# Repeat for each logical unit
git push origin feature/work-description
gh pr create --base main --head feature/work-description
```

- One logical change per commit
- Descriptive commit messages
- Model disclosure in every commit
- Push and create PR early
- Work incrementally, commit often

## Authentication Handling - GRACEFUL FAILURE

**VALIDATE AUTH BEFORE GITHUB OPERATIONS**

```bash
# Required auth check pattern
gh auth status || echo "Auth issue detected"
# Handle auth problems gracefully
# Retry or report auth issues clearly
```

- Check `gh auth status` before GitHub operations
- Handle authentication failures gracefully
- Report auth issues clearly to user
- Never assume authentication works

## Cursor Integration - MANDATORY SYNC

**WRAPPER FILES REQUIRED FOR ALL PROMPTS**

```bash
# When modifying prompts/ files:
# 1. Update canonical prompt file
# 2. Create/update .cursor/prompts/ wrapper
# 3. Commit both in same commit
```

- Every `prompts/` file needs `.cursor/prompts/` wrapper
- Wrappers created/updated in same commit as canonical files
- Wrapper points to canonical file path
- Ensures Cursor IDE integration

## PR Management - REVIEW BEFORE MERGE

**CREATE PR FOR ALL CHANGES**

```bash
# PR creation pattern
gh pr create --title "type: Clear description" \
             --body "Detailed description of changes" \
             --base main --head feature/branch-name
```

- All feature branches require PR for merge
- Clear, descriptive PR titles and descriptions
- Wait for PR merge before continuing work
- Never merge directly to main without PR

## Output Pager Prevention - CRITICAL HEE VIOLATION

**NEVER ALLOW OUTPUT TO HIT SHELL PAGER**

```bash
# Pager bypass patterns for common commands:
git --no-pager log                    # Git commands
GIT_PAGER=cat git log                 # Environment variable
man -P cat page                       # Manual pages
MANPAGER=cat man page                 # Manual pager override
PAGER=cat command                     # General pager override
command | cat                         # Force output to stdout
command > file.txt                    # Redirect to file
command 2>&1                          # Capture both stdout and stderr
```

- Pager invocation requires oper intervention, violating HEE autonomy
- Different commands require different bypass methods
- Must be documented as enforceable HEE rule with clear consequences
- All shell commands must include pager prevention when applicable

**COMMAND-SPECIFIC PAGER BYPASS METHODS**:

- **Git**: `--no-pager` flag or `GIT_PAGER=cat` environment variable
- **Man pages**: `-P cat` flag or `MANPAGER=cat` environment variable
- **Less/More**: Use `cat` or redirect to file instead
- **Grep**: `--no-pager` where available, otherwise redirect output
- **Find**: Use `-print0` with `xargs -0` or redirect to file
- **System commands**: `PAGER=cat` environment variable or output redirection

**HEE RULE ENFORCEMENT**:

- Output MUST never invoke shell PAGER
- Pager bypass required for ALL interactive commands
- Violation constitutes HEE process failure
- Document pager prevention in all command examples
- Include pager bypass in security validation checks

## Branch Cleanup - IMMEDIATE REMOVAL

**DELETE MERGED BRANCHES IMMEDIATELY**

```bash
# After PR merge:
git checkout main && git pull origin main
git branch -D feature/merged-branch  # Local
git push origin --delete feature/merged-branch  # Remote
```

- Delete local branches after merge
- Delete remote branches after merge
- Prevents branch confusion and conflicts
- Keep repository clean and organized

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

**These are ENFORCEMENT RULES, not guidelines. Violation constitutes process failure.**

**Workflow Learnings (Updated 2026-01-22)**:

- Always use feature branches, never direct main commits
- Clean up merged branches immediately to avoid confusion
- Handle authentication issues gracefully with status checks
- Create Cursor wrappers for all prompt modifications
- Commit frequently to preserve state during development
- Create PRs for all changes and wait for proper review/merge
