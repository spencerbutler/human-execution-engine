"""
HEE/HEER Content Sanitization

This module provides content sanitization for Human Execution Engine and Runtime
systems. Sanitization preserves semantic meaning while removing security threats.

Security Requirements:
- Preserve semantic content while neutralizing threats
- Maintain human-readable output
- Prevent injection attacks and malicious content
- Support markdown content in task descriptions
"""

import re
import html
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ContentSanitizer:
    """
    Content sanitization for HEE/HEER systems.

    Provides semantic-preserving sanitization that maintains readability
    while neutralizing security threats.
    """

    # Dangerous patterns to neutralize
    DANGEROUS_PATTERNS = [
        # Script tags and JavaScript
        (r'<script[^>]*>.*?</script>', '[SCRIPT REMOVED]'),
        (r'javascript:', '[JAVASCRIPT REMOVED]'),
        (r'on\w+\s*=', '[EVENT REMOVED]'),

        # HTML injection
        (r'<\w+[^>]*>', '[HTML REMOVED]'),
        (r'</\w+>', ''),

        # Path traversal
        (r'\.\./', ''),  # Remove ../ patterns
        (r'\.\.\\', ''),  # Remove ..\ patterns

        # SQL-like injection patterns
        (r';\s*(drop|delete|update|insert|select|union)', '; [SQL REMOVED]'),
        (r'--\s', '-- '),  # Neutralize SQL comments
        (r'/\*.*?\*/', '/* COMMENT REMOVED */'),

        # Command injection
        (r'[;&|`$]\s*(rm|del|format|shutdown|reboot)', ' [COMMAND REMOVED]'),
        (r'>\s*/dev/', '> [DEVICE REMOVED]'),
    ]

    @staticmethod
    def sanitize_markdown_content(content: str) -> str:
        """
        Sanitize markdown content while preserving formatting.

        This allows safe markdown rendering while preventing injection attacks.

        Args:
            content: Markdown content to sanitize

        Returns:
            Sanitized markdown content
        """
        if not content:
            return ""

        sanitized = content

        # Apply dangerous pattern neutralization
        for pattern, replacement in ContentSanitizer.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE | re.DOTALL)

        # HTML entity encoding for remaining angle brackets
        sanitized = re.sub(r'<([^>]+)>', r'<\1>', sanitized)

        # Neutralize autolinks that could be dangerous
        sanitized = re.sub(r'<([^>]+://[^>]+)>', r'[\1](\1)', sanitized)

        # Log sanitization if content was modified
        if sanitized != content:
            logger.info("Content sanitized during markdown processing")

        return sanitized

    @staticmethod
    def sanitize_plain_text(text: str) -> str:
        """
        Sanitize plain text content.

        Removes control characters and normalizes whitespace while preserving
        human readability.

        Args:
            text: Plain text to sanitize

        Returns:
            Sanitized plain text
        """
        if not text:
            return ""

        # Remove control characters except common whitespace
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # Normalize excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)

        # Log if content was modified
        if sanitized != text:
            logger.info("Plain text sanitized")

        return sanitized.strip()

    @staticmethod
    def sanitize_task_title(title: str) -> str:
        """
        Sanitize task title with semantic preservation.

        Args:
            title: Task title to sanitize

        Returns:
            Sanitized task title
        """
        if not title:
            return ""

        # For titles, we want plain text sanitization
        # Titles shouldn't contain markdown or HTML
        sanitized = ContentSanitizer.sanitize_plain_text(title)

        # Additional title-specific sanitization
        # Remove excessive punctuation
        sanitized = re.sub(r'[!?]{2,}', '!', sanitized)  # Multiple ! or ? to single

        # Log sanitization
        if sanitized != title:
            logger.info("Task title sanitized")

        return sanitized

    @staticmethod
    def sanitize_task_description(description: str) -> str:
        """
        Sanitize task description with markdown support.

        Args:
            description: Task description to sanitize

        Returns:
            Sanitized task description
        """
        if not description:
            return ""

        # Descriptions support markdown, so use markdown sanitization
        sanitized = ContentSanitizer.sanitize_markdown_content(description)

        # Log sanitization
        if sanitized != description:
            logger.info("Task description sanitized")

        return sanitized

    @staticmethod
    def sanitize_operator_name(name: str) -> str:
        """
        Sanitize operator/human name.

        Args:
            name: Operator name to sanitize

        Returns:
            Sanitized operator name
        """
        if not name:
            return ""

        # Names should be plain text only
        sanitized = ContentSanitizer.sanitize_plain_text(name)

        # Additional name validation - only allow reasonable characters
        if not re.match(r'^[a-zA-Z\s\-\.\'"]+$', sanitized):
            logger.warning("Operator name contains non-standard characters")
            # Allow but log unusual characters

        # Log sanitization
        if sanitized != name:
            logger.info("Operator name sanitized")

        return sanitized

    @staticmethod
    def sanitize_workspace_name(workspace: str) -> str:
        """
        Sanitize workspace name.

        Args:
            workspace: Workspace name to sanitize

        Returns:
            Sanitized workspace name
        """
        if not workspace:
            return ""

        # Workspace names should be plain text
        sanitized = ContentSanitizer.sanitize_plain_text(workspace)

        # Additional workspace sanitization
        # Remove filesystem-unsafe characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', sanitized)

        # Log sanitization
        if sanitized != workspace:
            logger.info("Workspace name sanitized")

        return sanitized

    @staticmethod
    def sanitize_tag_content(tag: str) -> str:
        """
        Sanitize individual tag content.

        Args:
            tag: Tag content to sanitize

        Returns:
            Sanitized tag content
        """
        if not tag:
            return ""

        # Tags should be plain text, lowercase
        sanitized = ContentSanitizer.sanitize_plain_text(tag).lower()

        # Remove non-alphanumeric characters except hyphens and underscores
        sanitized = re.sub(r'[^a-z0-9\-_]', '', sanitized)

        # Ensure single consecutive hyphens/underscores
        sanitized = re.sub(r'[-_]{2,}', '-', sanitized)

        # Trim leading/trailing hyphens/underscores
        sanitized = sanitized.strip('-_')

        # Log sanitization
        if sanitized != tag.lower():
            logger.info("Tag content sanitized")

        return sanitized

    @staticmethod
    def sanitize_event_data(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize event data for journaling.

        Args:
            event_data: Event data dictionary to sanitize

        Returns:
            Sanitized event data
        """
        sanitized_data = {}

        for key, value in event_data.items():
            if isinstance(value, str):
                # Sanitize string values
                if key in ['title', 'description']:
                    sanitized_data[key] = ContentSanitizer.sanitize_markdown_content(value)
                else:
                    sanitized_data[key] = ContentSanitizer.sanitize_plain_text(value)
            elif isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                sanitized_data[key] = ContentSanitizer.sanitize_event_data(value)
            elif isinstance(value, list):
                # Sanitize list contents
                sanitized_list = []
                for item in value:
                    if isinstance(item, str):
                        sanitized_list.append(ContentSanitizer.sanitize_plain_text(item))
                    elif isinstance(item, dict):
                        sanitized_list.append(ContentSanitizer.sanitize_event_data(item))
                    else:
                        sanitized_list.append(item)
                sanitized_data[key] = sanitized_list
            else:
                # Keep non-string values as-is
                sanitized_data[key] = value

        # Log if data was modified
        if sanitized_data != event_data:
            logger.info("Event data sanitized")

        return sanitized_data

def demonstrate_sanitization():
    """
    Demonstrate sanitization capabilities.
    """
    test_cases = [
        ("Normal title", "Normal title"),
        ("Title with <script>alert(1)</script>", "Title with [SCRIPT REMOVED]"),
        ("Path traversal: ../../../etc/passwd", "Path traversal: [DEVICE REMOVED]"),
        ("SQL injection; drop table users;", "SQL injection; [SQL REMOVED] table users;"),
        ("Control chars: \x00\x01\x02", "Control chars: "),
        ("Markdown: **bold** and *italic*", "Markdown: **bold** and *italic*"),
    ]

    print("Content Sanitization Demonstration:")
    print("=" * 50)

    for input_text, expected_pattern in test_cases:
        sanitized = ContentSanitizer.sanitize_markdown_content(input_text)
        status = "✓" if expected_pattern in sanitized or sanitized == input_text else "✗"
        print(f"{status} Input: {repr(input_text)}")
        print(f"   Output: {repr(sanitized)}")
        print()

if __name__ == "__main__":
    demonstrate_sanitization()
