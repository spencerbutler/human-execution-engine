# Smart Approval Contract Policy

## Contract Freezing

The `safety_profiles.yml` file is now frozen at version 1.0. Any changes require:

1. **Pull Request**: All changes must be proposed via PR
2. **Security Review**: Changes affecting allowlists/denylists require security team review
3. **Testing**: Full replay corpus validation must pass
4. **Approval**: At least 2 maintainer approvals required
5. **Documentation**: Change must be documented in CHANGELOG.md

## Versioning Schema

- **Major (X.0)**: Breaking changes to profile structure or decision logic
- **Minor (1.X)**: New command classifications or expanded allowlists
- **Patch (1.0.X)**: Bug fixes, clarifications, or documentation updates

## Current Frozen Contract: v1.0

```yaml
command_safety_profiles:
  version: 1
  profiles:
    read_only:
      # Read-only operations (ls, cat, git status, etc.)
    low_risk:
      # Bounded local changes (git add, mkdir, etc.)
```

## Change Process

1. Create feature branch: `feature/safety-profile-update-<change>`
2. Update `safety_profiles.yml` with proposed changes
3. Run full test suite: `python -m pytest tooling/smart-approval/test_policy.py`
4. Validate replay corpus: Check all test cases still pass
5. Submit PR with comprehensive description
6. Security review for allowlist/denylist changes
7. CI validation passes
8. 2+ maintainer approvals
9. Merge and tag new version

## Emergency Changes

In case of critical security issues:

1. Immediate PR creation with `security:` prefix
2. Expedited security review (within 4 hours)
3. Emergency deployment allowed with 1 maintainer approval
4. Post-mortem review required within 24 hours

## Audit Trail

All contract changes are tracked in:

- `CHANGELOG.md`: User-facing change descriptions
- Git history: Complete change trail
- PR discussions: Decision rationale
- Security reviews: Risk assessments

## Contact

For contract change requests:

- Open issue with `safety-profile` label
- Include rationale and impact assessment
- Tag security team for allowlist/denylist changes
