#!/usr/bin/env python3
"""
HEE/HEER Security Scanner

Automated security scanning tool for HEE/HEER implementations and codebases.
Scans for security vulnerabilities, compliance issues, and best practice violations.

Usage:
    python scripts/security_scanner.py [path/to/scan]
    python scripts/security_scanner.py --help
"""

import os
import sys
import argparse
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SecurityFinding:
    """Security finding from scan"""
    file_path: str
    line_number: int
    finding_type: str
    severity: str
    description: str
    code_snippet: str
    recommendation: str

class SecurityScanner:
    """
    Comprehensive security scanner for HEE/HEER codebases.

    Scans for common security vulnerabilities, compliance issues,
    and best practice violations specific to HEE/HEER implementations.
    """

    def __init__(self):
        self.findings: List[SecurityFinding] = []

        # Security patterns to scan for
        self.security_patterns = {
            # Dangerous functions
            'dangerous_functions': {
                'pattern': r'\b(eval|exec|__import__|file|input)\s*\(',
                'severity': 'high',
                'description': 'Use of potentially dangerous function',
                'recommendation': 'Avoid eval/exec for security. Use safe alternatives.'
            },

            # Hardcoded secrets
            'hardcoded_secrets': {
                'pattern': r'(password|secret|key|token)\s*[=:]\s*["\'][^"\']+["\']',
                'severity': 'critical',
                'description': 'Potential hardcoded secret or credential',
                'recommendation': 'Use environment variables or secure credential storage.'
            },

            # SQL injection patterns
            'sql_injection': {
                'pattern': r'(SELECT|INSERT|UPDATE|DELETE).*%s',
                'severity': 'high',
                'description': 'Potential SQL injection vulnerability',
                'recommendation': 'Use parameterized queries or ORM.'
            },

            # Command injection
            'command_injection': {
                'pattern': r'(subprocess\.call|os\.system|os\.popen).*\+\s*.*',
                'severity': 'critical',
                'description': 'Potential command injection vulnerability',
                'recommendation': 'Avoid string concatenation in shell commands.'
            },

            # Insecure random
            'insecure_random': {
                'pattern': r'\b(random\.random|random\.randint)\b',
                'severity': 'medium',
                'description': 'Use of insecure random number generation',
                'recommendation': 'Use secrets module for security-sensitive operations.'
            },

            # Missing input validation
            'missing_validation': {
                'pattern': r'def.*input.*:\s*$',
                'severity': 'medium',
                'description': 'Function accepting input without clear validation',
                'recommendation': 'Add comprehensive input validation.'
            },

            # Unsafe deserialization
            'unsafe_deserialization': {
                'pattern': r'(pickle\.loads?|yaml\.unsafe_load)',
                'severity': 'high',
                'description': 'Unsafe deserialization may lead to code execution',
                'recommendation': 'Use safe deserialization methods or validate input.'
            },

            # Path traversal
            'path_traversal': {
                'pattern': r'\.\./',
                'severity': 'high',
                'description': 'Potential path traversal vulnerability',
                'recommendation': 'Validate and sanitize file paths.'
            }
        }

        # HEE/HEER specific security checks
        self.hee_patterns = {
            # Missing security validation
            'missing_security_validation': {
                'pattern': r'def.*input.*:\s*$',
                'exclude_pattern': r'(validate|sanitize|audit)',
                'severity': 'medium',
                'description': 'Input function without security validation',
                'recommendation': 'Add HEE/HEER security validation (validator.py).'
            },

            # Unsafe direct database access
            'unsafe_db_access': {
                'pattern': r'(sqlite3|psycopg2|mysql).*\.execute.*%.*',
                'severity': 'high',
                'description': 'Unsafe database query with string formatting',
                'recommendation': 'Use parameterized queries for HEE/HEER data.'
            },

            # Missing audit logging
            'missing_audit': {
                'pattern': r'(create_task|update_task|delete_task)',
                'exclude_pattern': r'audit|log',
                'severity': 'medium',
                'description': 'Task operation without audit logging',
                'recommendation': 'Add audit logging for HEE/HEER operations.'
            }
        }

    def scan_file(self, file_path: Path) -> None:
        """
        Scan a single file for security issues.

        Args:
            file_path: Path to file to scan
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # Check general security patterns
                for pattern_name, pattern_info in self.security_patterns.items():
                    if re.search(pattern_info['pattern'], line, re.IGNORECASE):
                        # Skip if it's in a comment or test file
                        if self._is_excluded_line(line, file_path):
                            continue

                        finding = SecurityFinding(
                            file_path=str(file_path),
                            line_number=line_num,
                            finding_type=pattern_name,
                            severity=pattern_info['severity'],
                            description=pattern_info['description'],
                            code_snippet=line.strip(),
                            recommendation=pattern_info['recommendation']
                        )
                        self.findings.append(finding)

                # Check HEE/HEER specific patterns
                for pattern_name, pattern_info in self.hee_patterns.items():
                    if re.search(pattern_info['pattern'], line, re.IGNORECASE):
                        # Check exclude pattern if present
                        if 'exclude_pattern' in pattern_info:
                            if re.search(pattern_info['exclude_pattern'], line, re.IGNORECASE):
                                continue

                        if self._is_excluded_line(line, file_path):
                            continue

                        finding = SecurityFinding(
                            file_path=str(file_path),
                            line_number=line_num,
                            finding_type=pattern_name,
                            severity=pattern_info['severity'],
                            description=pattern_info['description'],
                            code_snippet=line.strip(),
                            recommendation=pattern_info['recommendation']
                        )
                        self.findings.append(finding)

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

    def _is_excluded_line(self, line: str, file_path: Path) -> bool:
        """
        Check if a line should be excluded from security scanning.

        Args:
            line: Code line to check
            file_path: Path to the file

        Returns:
            True if line should be excluded
        """
        # Skip comments
        if line.strip().startswith('#'):
            return True

        # Skip test files
        if 'test' in file_path.name.lower():
            return True

        # Skip example/documentation files
        if any(part in str(file_path) for part in ['examples', 'docs', 'README']):
            return True

        return False

    def scan_directory(self, directory: Path, exclude_patterns: Optional[List[str]] = None) -> None:
        """
        Scan a directory recursively for security issues.

        Args:
            directory: Directory to scan
            exclude_patterns: Patterns of files/directories to exclude
        """
        exclude_patterns = exclude_patterns or ['__pycache__', '.git', 'node_modules', '.venv']

        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]

            for file in files:
                file_path = Path(root) / file

                # Skip non-code files
                if file_path.suffix not in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']:
                    continue

                # Skip excluded patterns
                if any(pattern in str(file_path) for pattern in exclude_patterns):
                    continue

                self.scan_file(file_path)

    def generate_report(self, output_format: str = 'text') -> str:
        """
        Generate security scan report.

        Args:
            output_format: Output format ('text', 'json')

        Returns:
            Formatted report
        """
        if output_format == 'json':
            return self._generate_json_report()
        else:
            return self._generate_text_report()

    def _generate_text_report(self) -> str:
        """Generate text format report"""
        if not self.findings:
            return "✅ No security issues found!"

        report = []
        report.append("🚨 Security Scan Report")
        report.append("=" * 50)

        # Group by severity
        severity_counts = {}
        severity_groups = {}

        for finding in self.findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1

            if finding.severity not in severity_groups:
                severity_groups[finding.severity] = []
            severity_groups[finding.severity].append(finding)

        # Summary
        report.append("Summary:")
        for severity, count in severity_counts.items():
            report.append(f"  {severity.upper()}: {count}")
        report.append("")

        # Details by severity
        severity_order = ['critical', 'high', 'medium', 'low', 'info']
        for severity in severity_order:
            if severity in severity_groups:
                report.append(f"{severity.upper()} SEVERITY FINDINGS:")
                report.append("-" * 30)

                for finding in severity_groups[severity]:
                    report.append(f"File: {finding.file_path}:{finding.line_number}")
                    report.append(f"Type: {finding.finding_type}")
                    report.append(f"Description: {finding.description}")
                    report.append(f"Code: {finding.code_snippet}")
                    report.append(f"Recommendation: {finding.recommendation}")
                    report.append("")

        return "\n".join(report)

    def _generate_json_report(self) -> str:
        """Generate JSON format report"""
        findings_data = []
        for finding in self.findings:
            findings_data.append({
                'file_path': finding.file_path,
                'line_number': finding.line_number,
                'finding_type': finding.finding_type,
                'severity': finding.severity,
                'description': finding.description,
                'code_snippet': finding.code_snippet,
                'recommendation': finding.recommendation
            })

        return json.dumps({
            'scan_summary': {
                'total_findings': len(self.findings),
                'severity_breakdown': self._get_severity_breakdown()
            },
            'findings': findings_data
        }, indent=2)

    def _get_severity_breakdown(self) -> Dict[str, int]:
        """Get severity breakdown counts"""
        breakdown = {}
        for finding in self.findings:
            breakdown[finding.severity] = breakdown.get(finding.severity, 0) + 1
        return breakdown

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='HEE/HEER Security Scanner')
    parser.add_argument('path', nargs='?', default='.', help='Path to scan (default: current directory)')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    parser.add_argument('--exclude', nargs='*', help='Patterns to exclude')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    scan_path = Path(args.path)
    if not scan_path.exists():
        print(f"Error: Path {scan_path} does not exist")
        sys.exit(1)

    scanner = SecurityScanner()

    if scan_path.is_file():
        scanner.scan_file(scan_path)
    else:
        exclude_patterns = args.exclude or ['__pycache__', '.git', 'node_modules', '.venv']
        scanner.scan_directory(scan_path, exclude_patterns)

    report = scanner.generate_report(args.format)
    print(report)

    # Exit with error code if critical/high severity findings
    critical_high = sum(1 for f in scanner.findings
                       if f.severity in ['critical', 'high'])
    if critical_high > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
