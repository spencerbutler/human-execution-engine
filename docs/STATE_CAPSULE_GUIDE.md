# HEE State Capsule Guide

## Overview
Comprehensive guide for HEE state capsule management including the .done extension rule for completed tasks.

## State Capsule Lifecycle

### 1. Creation
- **When**: Start of any HEE session or task
- **Format**: `YYYY-MM-DD/HEE-[Project]-Session.md`
- **Location**: `docs/STATE_CAPSULES/`
- **Content**: Task tracking, progress, decisions, and context

### 2. Active Management
- **Update Frequency**: After significant operations
- **Content**: Current status, violations, progress tracking
- **Validation**: Use `scripts/validate_hee_capsule.py`

### 3. Completion (.done Extension Rule)
**Rule**: When all tasks in a state capsule are completed, rename with `.done` extension

#### Completion Criteria
- All tasks marked as completed ✅
- No active violations
- All documentation updated
- Session cleanup completed

#### Completion Process
```bash
# 1. Verify all tasks are complete
grep -q "✅" docs/STATE_CAPSULES/2026-01-24/HEE-Current-Tasks.md

# 2. Rename with .done extension
mv docs/STATE_CAPSULES/2026-01-24/HEE-Current-Tasks.md \
   docs/STATE_CAPSULES/2026-01-24/HEE-Current-Tasks.md.done

# 3. Create new capsule for next session
cp docs/TEMPLATES/STATE_CAPSULE_TEMPLATE.md \
   docs/STATE_CAPSULES/2026-01-24/HEE-Next-Session.md
```

#### .done Extension Benefits
- **Clear Status**: Immediately identifies completed work
- **Processing Skip**: Violation script skips .done files
- **Archive Ready**: Easy identification for cleanup
- **Historical Tracking**: Maintains completion timeline

### 4. Archiving
- **When**: 30 days after .done extension
- **Process**: Move to `docs/STATE_CAPSULES/archive/`
- **Format**: Preserve original .done extension

## Violation Script Integration

### .done Extension Handling
The violation checker script (`scripts/violation_checker.sh`) includes special handling for .done files:

```bash
# Check for .done files (completed capsules)
done_capsules=($(find "$state_capsule_dir" -name "*.md.done" -type f 2>/dev/null))
if [[ ${#done_capsules[@]} -gt 0 ]]; then
    add_success "Found ${#done_capsules[@]} completed state capsule(s) with .done extension"
    # Skip processing .done capsules
    for done_capsule in "${done_capsules[@]}"; do
        echo "  - Skipping completed capsule: $(basename "$done_capsule")"
    done
fi
```

### Validation Rules
- **Active Capsules**: Must not have .done extension
- **Processing**: Only active capsules are validated
- **Completion**: .done capsules are skipped during violation checks
- **Cleanup**: .done capsules flagged for archival after 30 days

## Best Practices

### Task Management
- Use clear, descriptive task names
- Mark tasks complete IMMEDIATELY after finishing
- Update progress in real-time
- Document decisions and rationale

### File Organization
- Use consistent naming conventions
- Group related tasks logically
- Maintain chronological order
- Use relative paths for portability

### Completion Workflow
1. **Review**: Verify all tasks are truly complete
2. **Document**: Ensure all changes are recorded
3. **Validate**: Run state capsule validation
4. **Rename**: Apply .done extension
5. **Archive**: Plan archival after 30 days

### Error Prevention
- **NEVER** commit directly to main branch
- **ALWAYS** create feature branches for changes
- **UPDATE** state capsule after significant operations
- **VALIDATE** before marking tasks complete

## Integration with HEE Workflow

### Pre-commit Integration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: hee-state-capsule-check
        name: HEE State Capsule Validation
        entry: bash -c 'echo "🔍 Validating state capsule..." && ./scripts/validate_hee_capsule.py --input docs/STATE_CAPSULES/current.md'
        language: system
        files: '.*'
        pass_filenames: false
```

### CI/CD Integration
- Validate state capsule completeness
- Check for .done extension compliance
- Ensure no active violations
- Verify documentation updates

### Monitoring and Reporting
- Track completion rates
- Monitor .done extension usage
- Report on state capsule health
- Identify workflow bottlenecks

## Troubleshooting

### Common Issues

#### Issue: "Task not marked complete but work is done"
**Solution**: Update state capsule IMMEDIATELY after task completion
```bash
# Update task status
sed -i 's/- \[ \] Task description/- [x] Task description/' docs/STATE_CAPSULES/current.md
```

#### Issue: "Violation script processes .done files"
**Solution**: Ensure .done extension is properly applied
```bash
# Check for .done files
ls -la docs/STATE_CAPSULES/*.done
```

#### Issue: "State capsule not found"
**Solution**: Verify file exists and path is correct
```bash
# Check state capsule directory
ls -la docs/STATE_CAPSULES/
```

### Recovery Procedures

#### Recover from Missing State Capsule
1. Create new capsule from template
2. Document current state
3. Update task tracking
4. Validate and commit

#### Recover from Incomplete Tasks
1. Review task list
2. Identify incomplete items
3. Update status accordingly
4. Plan completion strategy

#### Recover from Violation Issues
1. Run violation checker
2. Address all violations
3. Update state capsule
4. Validate compliance

## Templates and Examples

### Basic State Capsule Template
```markdown
# HEE Session Report

## Overview
[Session purpose and scope]

## Session Details
- **Date**: [YYYY-MM-DD]
- **Time Started**: [HH:MM:SS TZ]
- **Branch**: [feature/branch-name]
- **Status**: [In Progress/Completed]
- **Model**: [model-name]

## Current Work
### Task: [Task Name]
**Status**: [In Progress/Completed/Pending]
**Priority**: [High/Medium/Low]
**Related Files**: [file1, file2, ...]

**Description**: [Task details]

**Steps to Complete**:
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

**Files Involved**:
- [file1] - [description]
- [file2] - [description]

**Dependencies**: [list dependencies]

**Notes**: [additional notes]

## HEE State Management
### Current State Capsule
- **File**: [path]
- **Status**: [Active/Completed]
- **Branch**: [branch-name]

### Previous State Capsules
- [list previous capsules]

### .done Extension Rule
**Rule**: When all tasks in a state capsule are completed, rename with `.done` extension
- Example: `HEE-Current-Tasks.md` → `HEE-Current-Tasks.md.done`
- Violation script should skip processing any files with `.done` extension
- Archive .done capsules after 30 days to prevent accumulation

## Problem Analysis
[Document issues, root causes, and solutions]

## Next Steps
[list upcoming tasks and actions]

## HEE Compliance
- [ ] Feature branch created for all changes
- [ ] Working from proper project directory
- [ ] State capsule created and updated
- [ ] Model disclosure in commit messages
- [ ] Pre-commit checks configured

## Files Modified
[list modified files]

## Pending Actions
[list pending items]

## Status Tracking
- **Session Started**: [timestamp]
- **Current Status**: [status]
- **Progress**: [X/Y tasks completed]
- **Next Update**: [timestamp]
```

### .done Extension Example
```bash
# Before completion
docs/STATE_CAPSULES/2026-01-24/HEE-Current-Tasks.md

# After completion
docs/STATE_CAPSULES/2026-01-24/HEE-Current-Tasks.md.done
```

## References
- [HEE Policy](HEE_POLICY.md)
- [Violation Metrics](VIOLATION_METRICS.md)
- [Prompting Rules](PROMPTING_RULES.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
