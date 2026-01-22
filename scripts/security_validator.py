#!/usr/bin/env python3
"""
HEE/HEER Security Validator

Command-line tool for validating HEE/HEER security compliance.
Tests implementations against canonical security requirements.

Usage:
    python scripts/security_validator.py validate-input --input "test input"
    python scripts/security_validator.py validate-file --path src/security/validator.py
    python scripts/security_validator.py run-tests
    python scripts/security_validator.py --help
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from security.validator import SecurityValidator, run_security_tests
    from security.sanitizer import ContentSanitizer
    from security.audit import SecurityAuditor
except ImportError as e:
    print(f"Error importing security modules: {e}")
    print("Make sure you're running from the project root and security modules are available.")
    sys.exit(1)

class SecurityValidatorCLI:
    """Command-line interface for HEE/HEER security validation"""

    def __init__(self):
        self.validator = SecurityValidator()
        self.sanitizer = ContentSanitizer()
        self.auditor = SecurityAuditor()

    def validate_input(self, input_str: str, input_type: str = 'text') -> Dict[str, Any]:
        """
        Validate input against HEE/HEER security requirements.

        Args:
            input_str: Input to validate
            input_type: Type of input (text, title, description, etc.)

        Returns:
            Validation results
        """
        results = {
            'input': input_str,
            'type': input_type,
            'unicode_validation': {},
            'content_validation': {},
            'sanitization': {},
            'overall_valid': True,
            'issues': []
        }

        # Unicode validation
        unicode_result = self.validator.validate_unicode_input(input_str)
        results['unicode_validation'] = {
            'valid': unicode_result.is_valid,
            'error': unicode_result.error_message,
            'normalized': unicode_result.sanitized_value
        }

        if not unicode_result.is_valid:
            results['overall_valid'] = False
            results['issues'].append(f"Unicode validation failed: {unicode_result.error_message}")

        # Type-specific validation
        validated_input = unicode_result.sanitized_value or input_str

        if input_type == 'title':
            title_result = self.validator.validate_task_title(validated_input)
            results['content_validation'] = {
                'valid': title_result.is_valid,
                'error': title_result.error_message,
                'sanitized': title_result.sanitized_value
            }
            if not title_result.is_valid:
                results['overall_valid'] = False
                results['issues'].append(f"Title validation failed: {title_result.error_message}")

        elif input_type == 'description':
            desc_result = self.validator.validate_task_description(validated_input)
            results['content_validation'] = {
                'valid': desc_result.is_valid,
                'error': desc_result.error_message,
                'sanitized': desc_result.sanitized_value
            }
            if not desc_result.is_valid:
                results['overall_valid'] = False
                results['issues'].append(f"Description validation failed: {desc_result.error_message}")

        elif input_type == 'tags':
            # Assume comma-separated tags
            tag_list = [tag.strip() for tag in validated_input.split(',') if tag.strip()]
            tags_result = self.validator.validate_task_tags(tag_list)
            results['content_validation'] = {
                'valid': tags_result.is_valid,
                'error': tags_result.error_message,
                'sanitized': tags_result.sanitized_value
            }
            if not tags_result.is_valid:
                results['overall_valid'] = False
                results['issues'].append(f"Tags validation failed: {tags_result.error_message}")

        # Content sanitization
        if input_type in ['description', 'markdown']:
            sanitized = self.sanitizer.sanitize_markdown_content(validated_input)
        else:
            sanitized = self.sanitizer.sanitize_plain_text(validated_input)

        results['sanitization'] = {
            'original_length': len(validated_input),
            'sanitized_length': len(sanitized),
            'modified': len(sanitized) != len(validated_input),
            'sanitized_content': sanitized
        }

        return results

    def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate a file for HEE/HEER security compliance.

        Args:
            file_path: Path to file to validate

        Returns:
            Validation results
        """
        results = {
            'file_path': str(file_path),
            'file_exists': file_path.exists(),
            'validation_results': {},
            'overall_valid': True,
            'issues': []
        }

        if not file_path.exists():
            results['overall_valid'] = False
            results['issues'].append(f"File does not exist: {file_path}")
            return results

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Basic content validation
            validation_result = self.validate_input(content, 'text')
            results['validation_results'] = validation_result

            if not validation_result['overall_valid']:
                results['overall_valid'] = False
                results['issues'].extend(validation_result['issues'])

            # Check for security imports
            if file_path.suffix == '.py':
                has_security_imports = any(imp in content for imp in [
                    'from security.validator import',
                    'from security.sanitizer import',
                    'from security.audit import'
                ])
                results['validation_results']['has_security_imports'] = has_security_imports

                if not has_security_imports and 'input' in content.lower():
                    results['issues'].append("Python file handles input but doesn't import security modules")

        except Exception as e:
            results['overall_valid'] = False
            results['issues'].append(f"Error reading file: {e}")

        return results

    def run_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive security test suite.

        Returns:
            Test results
        """
        results = {
            'security_tests': {},
            'validation_tests': {},
            'sanitization_tests': {},
            'overall_passed': True,
            'summary': {}
        }

        # Run security test vectors
        print("Running security test vectors...")
        security_results = run_security_tests()
        results['security_tests'] = security_results

        if security_results['failed'] > 0:
            results['overall_passed'] = False

        # Test validation functions
        print("Testing validation functions...")
        validation_tests = self._run_validation_tests()
        results['validation_tests'] = validation_tests

        if not validation_tests['all_passed']:
            results['overall_passed'] = False

        # Test sanitization functions
        print("Testing sanitization functions...")
        sanitization_tests = self._run_sanitization_tests()
        results['sanitization_tests'] = sanitization_tests

        if not sanitization_tests['all_passed']:
            results['overall_passed'] = False

        # Generate summary
        results['summary'] = {
            'security_tests_passed': security_results['passed'],
            'security_tests_failed': security_results['failed'],
            'validation_tests_passed': sum(1 for t in validation_tests['tests'] if t['passed']),
            'validation_tests_failed': sum(1 for t in validation_tests['tests'] if not t['passed']),
            'sanitization_tests_passed': sum(1 for t in sanitization_tests['tests'] if t['passed']),
            'sanitization_tests_failed': sum(1 for t in sanitization_tests['tests'] if not t['passed']),
            'overall_status': 'PASSED' if results['overall_passed'] else 'FAILED'
        }

        return results

    def _run_validation_tests(self) -> Dict[str, Any]:
        """Run validation function tests"""
        tests = []

        # Test valid title
        result = self.validator.validate_task_title("Valid Task Title")
        tests.append({
            'test': 'valid_title',
            'passed': result.is_valid,
            'expected': True,
            'actual': result.is_valid
        })

        # Test invalid title (empty)
        result = self.validator.validate_task_title("")
        tests.append({
            'test': 'invalid_title_empty',
            'passed': not result.is_valid,
            'expected': False,
            'actual': result.is_valid
        })

        # Test invalid title (too long)
        long_title = "A" * 201
        result = self.validator.validate_task_title(long_title)
        tests.append({
            'test': 'invalid_title_too_long',
            'passed': not result.is_valid,
            'expected': False,
            'actual': result.is_valid
        })

        # Test valid tags
        result = self.validator.validate_task_tags(['tag1', 'tag2'])
        tests.append({
            'test': 'valid_tags',
            'passed': result.is_valid,
            'expected': True,
            'actual': result.is_valid
        })

        return {
            'tests': tests,
            'all_passed': all(t['passed'] for t in tests)
        }

    def _run_sanitization_tests(self) -> Dict[str, Any]:
        """Run sanitization function tests"""
        tests = []

        # Test script removal
        input_text = 'Normal text <script>alert(1)</script> more text'
        sanitized = self.sanitizer.sanitize_markdown_content(input_text)
        expected_removed = '[SCRIPT REMOVED]' in sanitized and '<script>' not in sanitized
        tests.append({
            'test': 'script_removal',
            'passed': expected_removed,
            'input': input_text,
            'output': sanitized
        })

        # Test plain text sanitization
        input_text = "Text with control chars: \x00\x01\x02"
        sanitized = self.sanitizer.sanitize_plain_text(input_text)
        expected_clean = '\x00' not in sanitized and '\x01' not in sanitized
        tests.append({
            'test': 'control_char_removal',
            'passed': expected_clean,
            'input': input_text,
            'output': sanitized
        })

        return {
            'tests': tests,
            'all_passed': all(t['passed'] for t in tests)
        }

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='HEE/HEER Security Validator')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # validate-input command
    input_parser = subparsers.add_parser('validate-input', help='Validate input string')
    input_parser.add_argument('--input', required=True, help='Input string to validate')
    input_parser.add_argument('--type', default='text',
                             choices=['text', 'title', 'description', 'tags', 'markdown'],
                             help='Type of input to validate')

    # validate-file command
    file_parser = subparsers.add_parser('validate-file', help='Validate file for security compliance')
    file_parser.add_argument('--path', required=True, help='Path to file to validate')

    # run-tests command
    test_parser = subparsers.add_parser('run-tests', help='Run comprehensive security test suite')

    # Common options
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cli = SecurityValidatorCLI()

    try:
        if args.command == 'validate-input':
            result = cli.validate_input(args.input, args.type)

        elif args.command == 'validate-file':
            result = cli.validate_file(Path(args.path))

        elif args.command == 'run-tests':
            result = cli.run_tests()

        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)

        # Output results
        if args.format == 'json':
            print(json.dumps(result, indent=2))
        else:
            cli._print_text_result(result, args.command)

        # Exit with error code for failures
        if args.command in ['validate-input', 'validate-file']:
            if not result.get('overall_valid', True):
                sys.exit(1)
        elif args.command == 'run-tests':
            if not result.get('overall_passed', True):
                sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    def _print_text_result(self, result: Dict[str, Any], command: str):
        """Print results in text format"""
        if command == 'validate-input':
            status = "✅ VALID" if result['overall_valid'] else "❌ INVALID"
            print(f"Input Validation: {status}")
            print(f"Type: {result['type']}")
            print(f"Input: {repr(result['input'])}")

            if not result['overall_valid']:
                print("Issues:")
                for issue in result['issues']:
                    print(f"  - {issue}")

            if result['sanitization']['modified']:
                print(f"Content was sanitized (length: {result['sanitization']['original_length']} → {result['sanitization']['sanitized_length']})")

        elif command == 'validate-file':
            status = "✅ VALID" if result['overall_valid'] else "❌ INVALID"
            print(f"File Validation: {status}")
            print(f"Path: {result['file_path']}")
            print(f"Exists: {result['file_exists']}")

            if not result['overall_valid']:
                print("Issues:")
                for issue in result['issues']:
                    print(f"  - {issue}")

        elif command == 'run-tests':
            status = "✅ PASSED" if result['overall_passed'] else "❌ FAILED"
            print(f"Security Test Suite: {status}")
            summary = result['summary']
            print(f"Security Tests: {summary['security_tests_passed']}/{summary['security_tests_passed'] + summary['security_tests_failed']} passed")
            print(f"Validation Tests: {summary['validation_tests_passed']}/{summary['validation_tests_passed'] + summary['validation_tests_failed']} passed")
            print(f"Sanitization Tests: {summary['sanitization_tests_passed']}/{summary['sanitization_tests_passed'] + summary['sanitization_tests_failed']} passed")

if __name__ == "__main__":
    main()
