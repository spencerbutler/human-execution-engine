"""
HEE Repetition Prevention System for I10: Repeat Without Correction Invariant

Enforces the rule: "Uncorrected repetition degrades signal"
Prevents repeating the same mistakes without learning and correction.

Key Functions:
- Track failed attempts and their root causes
- Detect when similar attempts are repeated without correction
- Require learning and correction before retrying
- Maintain signal quality through proper learning cycles
"""

import logging
import os
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

class FailureType(Enum):
    """Types of failures that can occur"""
    MISSING_EVIDENCE = "missing_evidence"
    INVALID_EVIDENCE = "invalid_evidence"
    UNAUTHORIZED_AGENT = "unauthorized_agent"
    INCORRECT_CLAIM = "incorrect_claim"
    REPEATED_ATTEMPT = "repeated_attempt"
    SYSTEM_ERROR = "system_error"

@dataclass
class FailureRecord:
    """Record of a failed attempt"""
    context_hash: str
    failure_type: FailureType
    failure_message: str
    timestamp: str
    agent_type: str
    action: str
    claims: List[str]
    evidence_paths: List[str]
    root_cause: Optional[str] = None
    suggested_correction: Optional[str] = None

@dataclass
class LearningRecord:
    """Record of learning from a failure"""
    context_hash: str
    correction_applied: str
    evidence_improvements: List[str]
    timestamp: str
    agent_type: str

class RepetitionPrevention:
    """
    Prevents uncorrected repetition of failed attempts.

    I10 Invariant: Uncorrected repetition degrades signal
    """

    def __init__(self, repo_path: str):
        """
        Initialize the repetition prevention system.

        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = repo_path
        self.failure_log_file = os.path.join(repo_path, ".hee", "learning", "failures.json")
        self.learning_log_file = os.path.join(repo_path, ".hee", "learning", "learning.json")
        self._ensure_learning_directory()

        # Load existing records
        self.failure_records = self._load_failure_records()
        self.learning_records = self._load_learning_records()

    def _ensure_learning_directory(self):
        """Ensure learning directory exists"""
        os.makedirs(os.path.dirname(self.failure_log_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.learning_log_file), exist_ok=True)

    def _load_failure_records(self) -> List[FailureRecord]:
        """Load existing failure records"""
        if not os.path.exists(self.failure_log_file):
            return []

        try:
            with open(self.failure_log_file, 'r') as f:
                data = json.load(f)
                return [FailureRecord(**record) for record in data]
        except Exception as e:
            logger.error(f"Failed to load failure records: {e}")
            return []

    def _load_learning_records(self) -> List[LearningRecord]:
        """Load existing learning records"""
        if not os.path.exists(self.learning_log_file):
            return []

        try:
            with open(self.learning_log_file, 'r') as f:
                data = json.load(f)
                return [LearningRecord(**record) for record in data]
        except Exception as e:
            logger.error(f"Failed to load learning records: {e}")
            return []

    def _save_failure_records(self):
        """Save failure records to disk"""
        try:
            with open(self.failure_log_file, 'w') as f:
                data = [record.__dict__ for record in self.failure_records]
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save failure records: {e}")

    def _save_learning_records(self):
        """Save learning records to disk"""
        try:
            with open(self.learning_log_file, 'w') as f:
                data = [record.__dict__ for record in self.learning_records]
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save learning records: {e}")

    def check_repetition(self, context_hash: str, previous_attempts: List[str]) -> Any:
        """
        Check if an attempt represents uncorrected repetition.

        Args:
            context_hash: Hash of the current attempt context
            previous_attempts: List of previous attempt hashes

        Returns:
            Validation result indicating if repetition is allowed
        """
        # Check for recent failures with the same context
        recent_failures = self._get_recent_failures(context_hash, hours=24)

        if not recent_failures:
            # No recent failures, allow attempt
            return ValidationResult(is_valid=True, message="No recent failures found")

        # Check if learning has occurred since the last failure
        last_failure = recent_failures[0]
        learning_since_failure = self._get_learning_since(last_failure.timestamp, context_hash)

        if not learning_since_failure:
            # No learning occurred, block repetition
            return ValidationResult(
                is_valid=False,
                message=f"Recent failure detected ({last_failure.failure_type.value}) without learning. "
                       f"Apply correction before retrying.",
                details={
                    "last_failure": last_failure.failure_message,
                    "failure_type": last_failure.failure_type.value,
                    "suggested_correction": last_failure.suggested_correction
                }
            )

        # Check if the learning is sufficient for the current attempt
        if self._is_learning_sufficient(learning_since_failure, context_hash):
            return ValidationResult(is_valid=True, message="Learning detected, repetition allowed")
        else:
            return ValidationResult(
                is_valid=False,
                message="Insufficient learning detected. Apply more specific corrections.",
                details={"required_corrections": self._get_required_corrections(last_failure)}
            )

    def record_failure(self, context_hash: str, failure_type: FailureType,
                      failure_message: str, agent_type: str, action: str,
                      claims: List[str], evidence_paths: List[str]) -> FailureRecord:
        """
        Record a failure for future learning.

        Args:
            context_hash: Hash of the attempt context
            failure_type: Type of failure
            failure_message: Detailed failure message
            agent_type: Type of agent that failed
            action: Action that failed
            claims: Claims that were made
            evidence_paths: Evidence paths that were provided

        Returns:
            Created failure record
        """
        # Determine root cause and suggested correction
        root_cause, suggested_correction = self._analyze_failure(
            failure_type, failure_message, claims, evidence_paths
        )

        failure_record = FailureRecord(
            context_hash=context_hash,
            failure_type=failure_type,
            failure_message=failure_message,
            timestamp=datetime.now().isoformat(),
            agent_type=agent_type,
            action=action,
            claims=claims,
            evidence_paths=evidence_paths,
            root_cause=root_cause,
            suggested_correction=suggested_correction
        )

        self.failure_records.append(failure_record)
        self._save_failure_records()

        logger.warning(f"Recorded failure: {failure_type.value} - {failure_message}")

        return failure_record

    def record_learning(self, context_hash: str, correction_applied: str,
                       evidence_improvements: List[str], agent_type: str) -> LearningRecord:
        """
        Record learning that has occurred.

        Args:
            context_hash: Hash of the context being learned from
            correction_applied: Description of correction applied
            evidence_improvements: List of evidence improvements made
            agent_type: Type of agent applying learning

        Returns:
            Created learning record
        """
        learning_record = LearningRecord(
            context_hash=context_hash,
            correction_applied=correction_applied,
            evidence_improvements=evidence_improvements,
            timestamp=datetime.now().isoformat(),
            agent_type=agent_type
        )

        self.learning_records.append(learning_record)
        self._save_learning_records()

        logger.info(f"Recorded learning for context {context_hash}: {correction_applied}")

        return learning_record

    def _get_recent_failures(self, context_hash: str, hours: int = 24) -> List[FailureRecord]:
        """
        Get recent failures for a specific context.

        Args:
            context_hash: Hash of the context to search for
            hours: Number of hours to look back

        Returns:
            List of recent failures for this context
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_failures = []

        for failure in self.failure_records:
            if failure.context_hash == context_hash:
                failure_time = datetime.fromisoformat(failure.timestamp)
                if failure_time >= cutoff_time:
                    recent_failures.append(failure)

        # Sort by timestamp, most recent first
        recent_failures.sort(key=lambda x: x.timestamp, reverse=True)
        return recent_failures

    def _get_learning_since(self, timestamp: str, context_hash: str) -> List[LearningRecord]:
        """
        Get learning records since a specific timestamp for a context.

        Args:
            timestamp: ISO format timestamp to look back from
            context_hash: Hash of the context to search for

        Returns:
            List of learning records since the timestamp
        """
        cutoff_time = datetime.fromisoformat(timestamp)
        learning_since = []

        for learning in self.learning_records:
            if learning.context_hash == context_hash:
                learning_time = datetime.fromisoformat(learning.timestamp)
                if learning_time >= cutoff_time:
                    learning_since.append(learning)

        return learning_since

    def _is_learning_sufficient(self, learning_records: List[LearningRecord],
                               context_hash: str) -> bool:
        """
        Check if the learning records are sufficient for the current context.

        Args:
            learning_records: List of learning records
            context_hash: Hash of the current context

        Returns:
            True if learning is sufficient, False otherwise
        """
        if not learning_records:
            return False

        # Get the last failure for this context to compare against
        recent_failures = self._get_recent_failures(context_hash, hours=168)  # 7 days
        if not recent_failures:
            return False

        last_failure = recent_failures[0]

        # Check if the learning addresses the root cause of the failure
        learning_corrections = set(lr.correction_applied.lower() for lr in learning_records)
        failure_root_cause = last_failure.root_cause.lower() if last_failure.root_cause else ""

        # Simple check: does any learning correction mention the root cause?
        for correction in learning_corrections:
            if failure_root_cause in correction or any(word in correction for word in failure_root_cause.split()):
                return True

        return False

    def _analyze_failure(self, failure_type: FailureType, failure_message: str,
                        claims: List[str], evidence_paths: List[str]) -> tuple[str, str]:
        """
        Analyze a failure to determine root cause and suggested correction.

        Args:
            failure_type: Type of failure
            failure_message: Failure message
            claims: Claims that were made
            evidence_paths: Evidence paths that were provided

        Returns:
            Tuple of (root_cause, suggested_correction)
        """
        if failure_type == FailureType.MISSING_EVIDENCE:
            root_cause = "Insufficient evidence provided for claims"
            suggested_correction = "Gather and provide lane-appropriate evidence before making claims"

        elif failure_type == FailureType.INVALID_EVIDENCE:
            root_cause = "Provided evidence is not immutable or not lane-appropriate"
            suggested_correction = "Ensure evidence is tracked by git and matches required evidence types"

        elif failure_type == FailureType.UNAUTHORIZED_AGENT:
            root_cause = "Agent type not authorized for this type of claim or action"
            suggested_correction = "Use appropriate agent type or obtain necessary permissions"

        elif failure_type == FailureType.INCORRECT_CLAIM:
            root_cause = "Claims do not match available evidence or are factually incorrect"
            suggested_correction = "Review evidence and ensure claims accurately reflect the proof"

        elif failure_type == FailureType.REPEATED_ATTEMPT:
            root_cause = "Repeating previous failed attempt without learning"
            suggested_correction = "Apply corrections from previous failures before retrying"

        else:
            root_cause = "Unknown failure cause"
            suggested_correction = "Review failure details and apply appropriate corrections"

        return root_cause, suggested_correction

    def _get_required_corrections(self, failure_record: FailureRecord) -> List[str]:
        """
        Get list of required corrections based on a failure record.

        Args:
            failure_record: The failure record to analyze

        Returns:
            List of required corrections
        """
        corrections = []

        if failure_record.root_cause:
            corrections.append(f"Address root cause: {failure_record.root_cause}")

        if failure_record.suggested_correction:
            corrections.append(f"Apply correction: {failure_record.suggested_correction}")

        # Add specific corrections based on failure type
        if failure_record.failure_type == FailureType.MISSING_EVIDENCE:
            corrections.append("Gather required evidence types for your agent lane")
            corrections.append("Ensure evidence is immutable (tracked by git)")

        elif failure_record.failure_type == FailureType.INVALID_EVIDENCE:
            corrections.append("Verify evidence files are tracked by git")
            corrections.append("Ensure evidence matches required types for your claims")

        return corrections

    def get_learning_summary(self) -> Dict[str, Any]:
        """
        Get a summary of learning and repetition prevention.

        Returns:
            Learning summary statistics
        """
        total_failures = len(self.failure_records)
        total_learning = len(self.learning_records)

        # Group failures by type
        failures_by_type = {}
        for failure in self.failure_records:
            failure_type = failure.failure_type.value
            if failure_type not in failures_by_type:
                failures_by_type[failure_type] = 0
            failures_by_type[failure_type] += 1

        # Group learning by agent type
        learning_by_agent = {}
        for learning in self.learning_records:
            agent_type = learning.agent_type
            if agent_type not in learning_by_agent:
                learning_by_agent[agent_type] = 0
            learning_by_agent[agent_type] += 1

        # Calculate repetition prevention effectiveness
        prevented_repetitions = 0
        for failure in self.failure_records:
            recent_failures = self._get_recent_failures(failure.context_hash, hours=24)
            if len(recent_failures) > 1:
                prevented_repetitions += len(recent_failures) - 1

        return {
            "total_failures": total_failures,
            "total_learning_records": total_learning,
            "failures_by_type": failures_by_type,
            "learning_by_agent": learning_by_agent,
            "prevented_repetitions": prevented_repetitions,
            "recent_failures": [f.__dict__ for f in self.failure_records[-10:]],
            "recent_learning": [l.__dict__ for l in self.learning_records[-10:]]
        }

@dataclass
class ValidationResult:
    """Result of repetition validation"""
    is_valid: bool
    message: str
    details: Optional[Dict[str, Any]] = None
