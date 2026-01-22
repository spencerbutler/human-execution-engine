# Agent Prompting Rules (human-execution-engine)

## Scope Discipline - RULE ENFORCEMENT ONLY

**NO CODE UNTIL PROMPTS/SPECS ARE MERGED TO MAIN**
- Implementation code forbidden until prompts/spec complete and merged
- Optimize for security validation, not free tier usage
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

---

**These are ENFORCEMENT RULES, not guidelines. Violation constitutes process failure.**

**Workflow Learnings (Updated 2026-01-22)**:
- Always use feature branches, never direct main commits
- Clean up merged branches immediately to avoid confusion
- Handle authentication issues gracefully with status checks
- Create Cursor wrappers for all prompt modifications
- Commit frequently to preserve state during development
- Create PRs for all changes and wait for proper review/merge
