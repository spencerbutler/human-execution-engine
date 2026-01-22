"""
HEE/HEER Security Input Validation

This module provides comprehensive input validation for Human Execution Engine
and Runtime systems. All validation follows security-first principles with
defense-in-depth approach.

Security Requirements:
- Unicode normalization and validation
- Control character blocking
- Zero-width character detection
- Content length limits and format validation
"""

import unicodedata
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Security constants
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 2000
MAX_TAG_LENGTH = 50
MAX_TAGS_COUNT = 10
MAX_WORKSPACE_LENGTH = 100

# Unicode security patterns
CONTROL_CHARS = {chr(i) for i in range(32)} - {'\t', '\n', '\r'}
ZERO_WIDTH_CHARS = {'\u200B', '\u200C', '\u200D', '\uFEFF'}  # BOM

# UUID v4 pattern
UUID_V4_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    re.IGNORECASE
)

@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    error_message: Optional[str] = None
    sanitized_value: Optional[str] = None

class SecurityValidator:
    """
    Comprehensive input validation for HEE/HEER systems.

    Implements security-first validation with multiple layers:
    1. Unicode security validation
    2. Content sanitization
    3. Business rule validation
    """

    @staticmethod
    def validate_unicode_input(input_str: str) -> ValidationResult:
        """
        Validate input against HEE/HEER unicode security requirements.

        Args:
            input_str: Input string to validate

        Returns:
            ValidationResult with validation status and details
        """
        if not isinstance(input_str, str):
            return ValidationResult(
                is_valid=False,
                error_message="Input must be string type"
            )

        # Unicode normalization (NFC form required)
        normalized = unicodedata.normalize('NFC', input_str)

        # Control character blocking (except tab, newline, carriage return)
        if any(c in CONTROL_CHARS for c in normalized):
            logger.warning("Control character detected in input")
            return ValidationResult(
                is_valid=False,
                error_message="Control characters not allowed"
            )

        # Zero-width character detection
        if any(c in ZERO_WIDTH_CHARS for c in normalized):
            logger.warning("Zero-width character detected in input")
            return ValidationResult(
                is_valid=False,
                error_message="Zero-width characters not allowed"
            )

        # Check for suspicious unicode categories
        for char in normalized:
            category = unicodedata.category(char)
            # Block format characters and private use
            if category.startswith(('Cf', 'Co', 'Cn')):
                logger.warning(f"Suspicious unicode category {category} in input")
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Unicode category {category} not allowed"
                )

        return ValidationResult(
            is_valid=True,
            sanitized_value=normalized
        )

    @staticmethod
    def validate_task_title(title: str) -> ValidationResult:
        """
        Validate task title against HEE/HEER requirements.

        Args:
            title: Task title to validate

        Returns:
            ValidationResult with validation status
        """
        # Unicode validation first
        unicode_result = SecurityValidator.validate_unicode_input(title)
        if not unicode_result.is_valid:
            return unicode_result

        validated_title = unicode_result.sanitized_value

        # Length validation
        if len(validated_title) < 1:
            return ValidationResult(
                is_valid=False,
                error_message="Title cannot be empty"
            )

        if len(validated_title) > MAX_TITLE_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"Title too long (max {MAX_TITLE_LENGTH} characters)"
            )

        # Content validation - must have non-whitespace
        if not validated_title.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Title cannot be only whitespace"
            )

        return ValidationResult(
            is_valid=True,
            sanitized_value=validated_title.strip()
        )

    @staticmethod
    def validate_task_description(description: str) -> ValidationResult:
        """
        Validate task description against HEE/HEER requirements.

        Args:
            description: Task description to validate

        Returns:
            ValidationResult with validation status
        """
        # Unicode validation first
        unicode_result = SecurityValidator.validate_unicode_input(description)
        if not unicode_result.is_valid:
            return unicode_result

        validated_desc = unicode_result.sanitized_value

        # Length validation
        if len(validated_desc) > MAX_DESCRIPTION_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"Description too long (max {MAX_DESCRIPTION_LENGTH} characters)"
            )

        return ValidationResult(
            is_valid=True,
            sanitized_value=validated_desc
        )

    @staticmethod
    def validate_task_tags(tags: List[str]) -> ValidationResult:
        """
        Validate task tags against HEE/HEER requirements.

        Args:
            tags: List of tag strings to validate

        Returns:
            ValidationResult with validation status
        """
        if not isinstance(tags, list):
            return ValidationResult(
                is_valid=False,
                error_message="Tags must be a list"
            )

        if len(tags) > MAX_TAGS_COUNT:
            return ValidationResult(
                is_valid=False,
                error_message=f"Too many tags (max {MAX_TAGS_COUNT})"
            )

        validated_tags = []
        seen_tags = set()

        for tag in tags:
            # Unicode validation
            unicode_result = SecurityValidator.validate_unicode_input(tag)
            if not unicode_result.is_valid:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Invalid tag '{tag}': {unicode_result.error_message}"
                )

            # Tag-specific validation
            validated_tag = unicode_result.sanitized_value.strip().lower()

            # Length check
            if len(validated_tag) < 1:
                return ValidationResult(
                    is_valid=False,
                    error_message="Tags cannot be empty"
                )

            if len(validated_tag) > MAX_TAG_LENGTH:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Tag too long (max {MAX_TAG_LENGTH} characters)"
                )

            # Uniqueness check
            if validated_tag in seen_tags:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Duplicate tag: {validated_tag}"
                )

            seen_tags.add(validated_tag)
            validated_tags.append(validated_tag)

        return ValidationResult(
            is_valid=True,
            sanitized_value=validated_tags
        )

    @staticmethod
    def validate_uuid(uuid_str: str) -> ValidationResult:
        """
        Validate UUID string format (v4 only).

        Args:
            uuid_str: UUID string to validate

        Returns:
            ValidationResult with validation status
        """
        if not isinstance(uuid_str, str):
            return ValidationResult(
                is_valid=False,
                error_message="UUID must be string type"
            )

        if not UUID_V4_PATTERN.match(uuid_str):
            return ValidationResult(
                is_valid=False,
                error_message="Invalid UUID v4 format"
            )

        return ValidationResult(is_valid=True)

    @staticmethod
    def validate_workspace_name(workspace: str) -> ValidationResult:
        """
        Validate workspace name against HEE/HEER requirements.

        Args:
            workspace: Workspace name to validate

        Returns:
            ValidationResult with validation status
        """
        if not workspace:  # Empty string is allowed (optional field)
            return ValidationResult(is_valid=True, sanitized_value="")

        # Unicode validation
        unicode_result = SecurityValidator.validate_unicode_input(workspace)
        if not unicode_result.is_valid:
            return unicode_result

        validated_workspace = unicode_result.sanitized_value.strip()

        # Length validation
        if len(validated_workspace) > MAX_WORKSPACE_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"Workspace name too long (max {MAX_WORKSPACE_LENGTH} characters)"
            )

        return ValidationResult(
            is_valid=True,
            sanitized_value=validated_workspace
        )

    @staticmethod
    def validate_context_enum(context: str) -> ValidationResult:
        """
        Validate context enum value.

        Args:
            context: Context value to validate

        Returns:
            ValidationResult with validation status
        """
        valid_contexts = {'personal', 'professional', 'mixed'}

        if context not in valid_contexts:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid context. Must be one of: {valid_contexts}"
            )

        return ValidationResult(is_valid=True)

    @staticmethod
    def validate_priority_enum(priority: str) -> ValidationResult:
        """
        Validate priority enum value.

        Args:
            priority: Priority value to validate

        Returns:
            ValidationResult with validation status
        """
        valid_priorities = {'low', 'medium', 'high', 'urgent'}

        if priority not in valid_priorities:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid priority. Must be one of: {valid_priorities}"
            )

        return ValidationResult(is_valid=True)

    @staticmethod
    def validate_status_enum(status: str) -> ValidationResult:
        """
        Validate status enum value.

        Args:
            status: Status value to validate

        Returns:
            ValidationResult with validation status
        """
        valid_statuses = {'todo', 'doing', 'blocked', 'done', 'archived'}

        if status not in valid_statuses:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid status. Must be one of: {valid_statuses}"
            )

        return ValidationResult(is_valid=True)

# Security test vectors (as defined in SECURITY.md)
SECURITY_TEST_VECTORS = [
    # Unicode attacks
    "\u0000\u0001\u0002",  # Control characters
    "\u200B\u200C\u200D",  # Zero-width characters
    "Valid input\uFEFF",    # Hidden BOM character

    # Content attacks
    "<script>alert(1)</script>",  # XSS attempts
    "../../../etc/passwd",       # Path traversal
    "💣".encode('utf-8').decode('latin1') if '💣'.encode('utf-8').decode('latin1', errors='ignore') else "encoding_attack",  # Encoding attacks
]

def run_security_tests() -> Dict[str, Any]:
    """
    Run security test vectors against validation functions.

    Returns:
        Dictionary with test results
    """
    results = {
        'passed': 0,
        'failed': 0,
        'details': []
    }

    validator = SecurityValidator()

    for i, test_vector in enumerate(SECURITY_TEST_VECTORS):
        result = validator.validate_unicode_input(test_vector)

        if result.is_valid:
            results['failed'] += 1
            results['details'].append({
                'test': i,
                'vector': repr(test_vector),
                'result': 'FAILED - Should have been blocked'
            })
        else:
            results['passed'] += 1
            results['details'].append({
                'test': i,
                'vector': repr(test_vector),
                'result': 'PASSED - Correctly blocked'
            })

    return results

if __name__ == "__main__":
    # Run security tests when executed directly
    test_results = run_security_tests()
    print(f"Security Tests: {test_results['passed']} passed, {test_results['failed']} failed")

    for detail in test_results['details']:
        print(f"Test {detail['test']}: {detail['result']}")
        if 'FAILED' in detail['result']:
            print(f"  Vector: {detail['vector']}")
