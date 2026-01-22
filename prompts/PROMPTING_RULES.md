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

---

**These are ENFORCEMENT RULES, not guidelines. Violation constitutes process failure.**
