"""
HEE/HEER Security Audit Framework

This module provides security monitoring, audit logging, and compliance tracking
for Human Execution Engine and Runtime systems.

Security Requirements:
- Immutable audit trails for all security events
- Real-time security monitoring and alerting
- Compliance violation detection and reporting
- Forensic analysis capabilities
"""

import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging
import threading
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """Security event for audit logging"""
    event_id: str
    timestamp: str
    event_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    source: str
    user_context: Optional[Dict[str, Any]] = None
    event_data: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[str] = None

class SecurityAuditor:
    """
    Security audit framework for HEE/HEER systems.

    Provides comprehensive audit logging, monitoring, and compliance tracking.
    """

    def __init__(self, audit_log_path: str = "security_audit.log"):
        self.audit_log_path = audit_log_path
        self._lock = threading.Lock()
        self.event_counter = 0

    def log_security_event(self, event: SecurityEvent) -> str:
        """
        Log a security event with immutable audit trail.

        Args:
            event: Security event to log

        Returns:
            Event hash for verification
        """
        with self._lock:
            # Add sequence number for ordering
            self.event_counter += 1
            event_dict = asdict(event)
            event_dict['sequence_number'] = self.event_counter
            event_dict['log_timestamp'] = datetime.now(timezone.utc).isoformat()

            # Create event hash for integrity verification
            event_json = json.dumps(event_dict, sort_keys=True)
            event_hash = hashlib.sha256(event_json.encode()).hexdigest()
            event_dict['integrity_hash'] = event_hash

            # Log based on severity
            log_level = getattr(logging, event.severity.upper(), logging.INFO)
            logger.log(log_level, f"Security Event: {event.event_type} - {event.risk_assessment}")

            # Write to audit log
            try:
                with open(self.audit_log_path, 'a', encoding='utf-8') as f:
                    json.dump(event_dict, f, ensure_ascii=False)
                    f.write('\n')
            except Exception as e:
                logger.error(f"Failed to write audit log: {e}")
                raise

            return event_hash

    def log_input_validation_failure(self, input_type: str, input_value: str,
                                   validation_error: str, user_context: Optional[Dict] = None) -> str:
        """
        Log input validation failure.

        Args:
            input_type: Type of input that failed validation
            input_value: The invalid input (sanitized for logging)
            validation_error: Description of validation failure
            user_context: Optional user context information

        Returns:
            Event hash
        """
        # Sanitize input value for logging (don't log actual malicious input)
        sanitized_value = input_value[:50] + "..." if len(input_value) > 50 else input_value
        if any(ord(c) < 32 for c in sanitized_value):
            sanitized_value = "[CONTAINS CONTROL CHARS]"

        event = SecurityEvent(
            event_id=f"input_validation_failure_{datetime.now(timezone.utc).timestamp()}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="input_validation_failure",
            severity="medium",
            source="validation_layer",
            user_context=user_context,
            event_data={
                "input_type": input_type,
                "input_value": sanitized_value,
                "validation_error": validation_error
            },
            risk_assessment="Potential injection attack or malformed input"
        )

        return self.log_security_event(event)

    def log_sanitization_event(self, content_type: str, original_length: int,
                              sanitized_length: int, user_context: Optional[Dict] = None) -> str:
        """
        Log content sanitization event.

        Args:
            content_type: Type of content sanitized
            original_length: Original content length
            sanitized_length: Sanitized content length
            user_context: Optional user context

        Returns:
            Event hash
        """
        modification_detected = original_length != sanitized_length
        severity = "low" if modification_detected else "info"

        event = SecurityEvent(
            event_id=f"sanitization_{datetime.now(timezone.utc).timestamp()}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="content_sanitization",
            severity=severity,
            source="sanitization_layer",
            user_context=user_context,
            event_data={
                "content_type": content_type,
                "original_length": original_length,
                "sanitized_length": sanitized_length,
                "modification_detected": modification_detected
            },
            risk_assessment="Content sanitized to prevent security threats" if modification_detected else "Content validated as safe"
        )

        return self.log_security_event(event)

    def log_policy_violation(self, policy_type: str, violation_details: Dict[str, Any],
                           user_context: Optional[Dict] = None) -> str:
        """
        Log policy violation event.

        Args:
            policy_type: Type of policy violated
            violation_details: Details of the violation
            user_context: Optional user context

        Returns:
            Event hash
        """
        event = SecurityEvent(
            event_id=f"policy_violation_{datetime.now(timezone.utc).timestamp()}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="policy_violation",
            severity="high",
            source="policy_enforcement",
            user_context=user_context,
            event_data={
                "policy_type": policy_type,
                "violation_details": violation_details
            },
            risk_assessment="Security policy violated - potential system compromise"
        )

        return self.log_security_event(event)

    def log_runtime_anomaly(self, anomaly_type: str, anomaly_data: Dict[str, Any],
                           risk_level: str = "medium", user_context: Optional[Dict] = None) -> str:
        """
        Log runtime anomaly detection.

        Args:
            anomaly_type: Type of anomaly detected
            anomaly_data: Anomaly details and metrics
            risk_level: Risk assessment level
            user_context: Optional user context

        Returns:
            Event hash
        """
        event = SecurityEvent(
            event_id=f"runtime_anomaly_{datetime.now(timezone.utc).timestamp()}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="runtime_anomaly",
            severity=risk_level,
            source="runtime_monitoring",
            user_context=user_context,
            event_data={
                "anomaly_type": anomaly_type,
                "anomaly_data": anomaly_data
            },
            risk_assessment=f"Runtime anomaly detected: {anomaly_type}"
        )

        return self.log_security_event(event)

    def get_audit_trail(self, start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None,
                       event_type: Optional[str] = None,
                       severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve audit trail with optional filtering.

        Args:
            start_time: Start time for filtering
            end_time: End time for filtering
            event_type: Event type filter
            severity: Severity level filter

        Returns:
            List of audit events matching criteria
        """
        events = []

        try:
            with open(self.audit_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        event = json.loads(line)

                        # Apply filters
                        if start_time and datetime.fromisoformat(event['timestamp']) < start_time:
                            continue
                        if end_time and datetime.fromisoformat(event['timestamp']) > end_time:
                            continue
                        if event_type and event['event_type'] != event_type:
                            continue
                        if severity and event['severity'] != severity:
                            continue

                        events.append(event)

                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid audit log entry: {e}")
                        continue

        except FileNotFoundError:
            logger.warning("Audit log file not found")
        except Exception as e:
            logger.error(f"Error reading audit log: {e}")

        return events

    def verify_audit_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of audit log.

        Returns:
            Integrity verification results
        """
        results = {
            'total_events': 0,
            'valid_events': 0,
            'invalid_events': 0,
            'integrity_violations': []
        }

        try:
            with open(self.audit_log_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    results['total_events'] += 1

                    try:
                        event = json.loads(line)

                        # Verify integrity hash
                        event_copy = event.copy()
                        stored_hash = event_copy.pop('integrity_hash', None)

                        if stored_hash:
                            event_json = json.dumps(event_copy, sort_keys=True)
                            calculated_hash = hashlib.sha256(event_json.encode()).hexdigest()

                            if calculated_hash == stored_hash:
                                results['valid_events'] += 1
                            else:
                                results['invalid_events'] += 1
                                results['integrity_violations'].append({
                                    'line': line_num,
                                    'event_id': event.get('event_id', 'unknown'),
                                    'stored_hash': stored_hash,
                                    'calculated_hash': calculated_hash
                                })
                        else:
                            # Legacy events without hash
                            results['valid_events'] += 1

                    except json.JSONDecodeError:
                        results['invalid_events'] += 1
                        results['integrity_violations'].append({
                            'line': line_num,
                            'error': 'Invalid JSON'
                        })

        except Exception as e:
            logger.error(f"Error verifying audit integrity: {e}")
            results['error'] = str(e)

        return results

# Global security auditor instance
security_auditor = SecurityAuditor()

def get_security_auditor() -> SecurityAuditor:
    """Get the global security auditor instance"""
    return security_auditor

# Convenience functions for common audit operations
def audit_input_validation_failure(input_type: str, input_value: str,
                                 validation_error: str, user_context: Optional[Dict] = None) -> str:
    """Convenience function for input validation failures"""
    return security_auditor.log_input_validation_failure(
        input_type, input_value, validation_error, user_context
    )

def audit_sanitization_event(content_type: str, original_length: int,
                           sanitized_length: int, user_context: Optional[Dict] = None) -> str:
    """Convenience function for sanitization events"""
    return security_auditor.log_sanitization_event(
        content_type, original_length, sanitized_length, user_context
    )

def audit_policy_violation(policy_type: str, violation_details: Dict[str, Any],
                         user_context: Optional[Dict] = None) -> str:
    """Convenience function for policy violations"""
    return security_auditor.log_policy_violation(
        policy_type, violation_details, user_context
    )

if __name__ == "__main__":
    # Demonstrate audit capabilities
    auditor = SecurityAuditor()

    # Log some test events
    print("Logging security events...")

    event1 = auditor.log_input_validation_failure(
        "task_title",
        "Invalid<script>alert(1)</script>",
        "Script injection attempt detected"
    )
    print(f"Logged input validation failure: {event1[:16]}...")

    event2 = auditor.log_sanitization_event(
        "markdown_description",
        100,
        85
    )
    print(f"Logged sanitization event: {event2[:16]}...")

    # Verify audit integrity
    print("\nVerifying audit integrity...")
    integrity = auditor.verify_audit_integrity()
    print(f"Total events: {integrity['total_events']}")
    print(f"Valid events: {integrity['valid_events']}")
    print(f"Integrity violations: {integrity['invalid_events']}")

    print("\nAudit demonstration complete.")
