#!/usr/bin/env python3
"""
HEE Compliance Monitor
Tracks HEE governance compliance and prevents violations through continuous monitoring.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path


class HEEComplianceMonitor:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.violations_log = self.repo_path / "docs" / "STATE_CAPSULES" / "compliance_violations.json"
        self.ensure_violations_log_exists()

    def ensure_violations_log_exists(self):
        """Ensure the violations log file exists with proper structure."""
        if not self.violations_log.parent.exists():
            self.violations_log.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.violations_log.exists():
            with open(self.violations_log, 'w') as f:
                json.dump({
                    "violations": [],
                    "last_check": None,
                    "compliance_score": 100
                }, f, indent=2)

    def get_current_branch(self):
        """Get the current git branch name."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, cwd=self.repo_path
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def get_latest_commit_info(self):
        """Get information about the latest commit."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%s|%an|%ad", "--date=iso"],
                capture_output=True, text=True, cwd=self.repo_path
            )
            commit_data = result.stdout.strip().split('|')
            return {
                "hash": commit_data[0],
                "message": commit_data[1],
                "author": commit_data[2],
                "date": commit_data[3]
            }
        except (subprocess.CalledProcessError, IndexError):
            return None

    def check_main_branch_violation(self):
        """Check for direct commits to main branch."""
        current_branch = self.get_current_branch()
        if current_branch == "main":
            return {
                "type": "MAIN_BRANCH_COMMIT",
                "severity": "HIGH",
                "description": "Direct commit to main branch detected",
                "branch": current_branch,
                "timestamp": datetime.now().isoformat()
            }
        return None

    def check_model_disclosure(self):
        """Check if commit message includes model disclosure."""
        commit_info = self.get_latest_commit_info()
        if commit_info and "[model:" not in commit_info["message"]:
            return {
                "type": "MISSING_MODEL_DISCLOSURE",
                "severity": "MEDIUM",
                "description": "Commit message missing model disclosure",
                "commit": commit_info["hash"],
                "message": commit_info["message"],
                "timestamp": datetime.now().isoformat()
            }
        return None

    def check_feature_branch_naming(self):
        """Check if feature branch follows naming convention."""
        current_branch = self.get_current_branch()
        if current_branch and not current_branch.startswith(("feature/", "fix/")):
            return {
                "type": "INVALID_BRANCH_NAME",
                "severity": "MEDIUM",
                "description": "Branch name doesn't follow HEE convention",
                "branch": current_branch,
                "timestamp": datetime.now().isoformat()
            }
        return None

    def run_compliance_checks(self):
        """Run all compliance checks and return violations."""
        violations = []
        
        # Check main branch violation
        violation = self.check_main_branch_violation()
        if violation:
            violations.append(violation)

        # Check model disclosure
        violation = self.check_model_disclosure()
        if violation:
            violations.append(violation)

        # Check branch naming
        violation = self.check_feature_branch_naming()
        if violation:
            violations.append(violation)

        return violations

    def log_violations(self, violations):
        """Log violations to the violations log file."""
        if not violations:
            return

        # Load existing violations
        with open(self.violations_log, 'r') as f:
            data = json.load(f)

        # Add new violations
        data["violations"].extend(violations)
        data["last_check"] = datetime.now().isoformat()
        
        # Calculate compliance score
        total_violations = len(data["violations"])
        compliance_score = max(0, 100 - (total_violations * 10))
        data["compliance_score"] = compliance_score

        # Save updated violations
        with open(self.violations_log, 'w') as f:
            json.dump(data, f, indent=2)

    def generate_report(self):
        """Generate a compliance report."""
        with open(self.violations_log, 'r') as f:
            data = json.load(f)

        report = f"""
# HEE Compliance Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Compliance Score**: {data["compliance_score"]}/100
**Last Check**: {data["last_check"] or "Never"}
**Total Violations**: {len(data["violations"])}

## Recent Violations

"""
        
        if data["violations"]:
            for i, violation in enumerate(data["violations"][-5:], 1):  # Show last 5 violations
                report += f"""
### {i}. {violation["type"]} - {violation["severity"]}
- **Description**: {violation["description"]}
- **Timestamp**: {violation["timestamp"]}
- **Details**: {violation.get("branch", violation.get("commit", "N/A"))}
"""
        else:
            report += "✅ No violations detected. HEE compliance is maintained."

        return report

    def print_violations(self, violations):
        """Print violations to console."""
        if not violations:
            print("✅ HEE compliance check passed")
            return

        print("🚨 HEE Compliance Violations Detected:")
        for violation in violations:
            print(f"  - {violation['type']}: {violation['description']}")
            print(f"    Severity: {violation['severity']}")
            print(f"    Time: {violation['timestamp']}")
            print()

    def monitor_compliance(self):
        """Main monitoring function."""
        print("🔍 Running HEE compliance checks...")
        
        violations = self.run_compliance_checks()
        self.log_violations(violations)
        self.print_violations(violations)
        
        if violations:
            print("💡 To fix violations:")
            print("  - Create feature branches for all changes")
            print("  - Include [model: claude-3.5-sonnet] in commit messages")
            print("  - Follow HEE branch naming conventions")
            return False
        
        print("✅ All HEE compliance checks passed!")
        return True


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        # Generate and print compliance report
        monitor = HEEComplianceMonitor()
        report = monitor.generate_report()
        print(report)
    else:
        # Run compliance monitoring
        monitor = HEEComplianceMonitor()
        success = monitor.monitor_compliance()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
