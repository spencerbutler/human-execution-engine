"""
HEE Invariant Enforcement Engine

Implements the three core invariants:
- I08: Lane Proof - Claims require lane-appropriate proof
- I09: Words Not State - Language alone cannot change system state
- I10: Repeat Without Correction - Uncorrected repetition degrades signal

This engine coordinates validation across all invariants before any action is taken.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
from datetime import datetime
import os

from .proof.validator import ProofValidator
from .state.gatekeeper import StateChangeGatekeeper
from .learning.prevention import RepetitionPrevention
from .evidence.manager import EvidenceManager
from .agent_taming import AgentTamingEnforcer, validate_hee_taming

logger = logging.getLogger(__name__)

class InvariantResult(Enum):
    """Result of invariant validation"""
    PASS = "pass"
    FAIL = "fail"
    BLOCK = "block"

@dataclass
class InvariantViolation:
    """Represents a violation of an invariant"""
    invariant_id: str
    violation_type: str
    message: str
    evidence: Optional[Dict[str, Any]] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class ValidationContext:
    """Context for invariant validation"""
    agent_type: str
    action: str
    claims: List[str]
    evidence_paths: List[str]
    target_state: Optional[str] = None
    previous_attempts: List[str] = None

    def to_hash(self) -> str:
        """Generate hash for repetition detection"""
        context_data = {
            'agent_type': self.agent_type,
            'action': self.action,
            'claims': sorted(self.claims),
            'target_state': self.target_state
        }
        context_str = json.dumps(context_data, sort_keys=True)
        return hashlib.sha256(context_str.encode()).hexdigest()

class InvariantEnforcementEngine:
    """
    Core engine that enforces all HEE invariants and agent taming constraints.

    Coordinates between:
    - Agent taming plan validation (behavioral constraints)
    - Proof validation (I08)
    - State change gatekeeping (I09)
    - Repetition prevention (I10)
    """

    def __init__(self, repo_path: str):
        """
        Initialize the invariant enforcement engine.

        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = repo_path
        self.evidence_manager = EvidenceManager(repo_path)
        self.proof_validator = ProofValidator(repo_path)
        self.state_gatekeeper = StateChangeGatekeeper(repo_path)
        self.repetition_prevention = RepetitionPrevention(repo_path)
        self.taming_enforcer = AgentTamingEnforcer(repo_path)

        # Track violations for learning
        self.violations_log = []

    def validate_action(self, context: ValidationContext) -> Tuple[InvariantResult, List[InvariantViolation]]:
        """
        Validate an action against all invariants and agent taming constraints.

        Args:
            context: Validation context containing action details

        Returns:
            Tuple of (result, violations)
        """
        violations = []

        # Phase 1: Agent Taming Plan Validation
        taming_context = self._create_taming_context(context)
        taming_result, taming_violations = self._validate_taming_plan(taming_context)
        if taming_result == InvariantResult.FAIL:
            violations.extend(taming_violations)

        # Phase 2: Invariant Validation (only if taming passed)
        if not taming_violations:
            # I08: Lane Proof Validation
            lane_result, lane_violations = self._validate_lane_proof(context)
            if lane_result == InvariantResult.FAIL:
                violations.extend(lane_violations)

            # I09: Words Not State Validation
            state_result, state_violations = self._validate_state_change(context)
            if state_result == InvariantResult.FAIL:
                violations.extend(state_violations)

            # I10: Repeat Without Correction Validation
            repeat_result, repeat_violations = self._validate_repetition(context)
            if repeat_result == InvariantResult.FAIL:
                violations.extend(repeat_violations)

        return InvariantResult.FAIL if violations else InvariantResult.PASS, violations

    def _create_taming_context(self, context: ValidationContext) -> Any:
        """Create taming context from validation context"""
        # In a real implementation, this would extract relevant information
        # For now, return a placeholder context
        return {
            'agent_type': context.agent_type,
            'action': context.action,
            'input_content': '',  # Would need to be provided
            'output_content': '',  # Would need to be provided
            'mode': 'STRICT'
        }

    def _validate_taming_plan(self, context: Any) -> Tuple[InvariantResult, List[InvariantViolation]]:
        """Validate action against the agent taming plan"""
        # In a real implementation, this would use the AgentTamingEnforcer
        # For now, return pass
        return InvariantResult.PASS, []

        # Determine overall result
        if violations:
            result = InvariantResult.FAIL
            logger.warning(f"Action validation failed with {len(violations)} violations")
        else:
            result = InvariantResult.PASS
            logger.info("Action validation passed all invariants")

        # Log violations for learning
        if violations:
            self._log_violations(violations)

        return result, violations

    def _validate_lane_proof(self, context: ValidationContext) -> Tuple[InvariantResult, List[InvariantViolation]]:
        """Validate I08: Lane Proof invariant"""
        violations = []

        # Check if claims require proof
        if context.claims:
            for claim in context.claims:
                proof_result = self.proof_validator.validate_claim(
                    agent_type=context.agent_type,
                    claim=claim,
                    evidence_paths=context.evidence_paths
                )

                if not proof_result.is_valid:
                    violations.append(InvariantViolation(
                        invariant_id="I08",
                        violation_type="missing_lane_proof",
                        message=f"Claim '{claim}' lacks lane-appropriate proof",
                        evidence={"claim": claim, "required_evidence": proof_result.required_evidence}
                    ))

        return InvariantResult.FAIL if violations else InvariantResult.PASS, violations

    def _validate_state_change(self, context: ValidationContext) -> Tuple[InvariantResult, List[InvariantViolation]]:
        """Validate I09: Words Not State invariant"""
        violations = []

        # Check if this is a state-changing action
        if context.target_state:
            state_result = self.state_gatekeeper.validate_state_change(
                agent_type=context.agent_type,
                target_state=context.target_state,
                evidence_paths=context.evidence_paths
            )

            if not state_result.is_valid:
                violations.append(InvariantViolation(
                    invariant_id="I09",
                    violation_type="language_only_state_change",
                    message="State change attempted without immutable evidence",
                    evidence={"target_state": context.target_state, "evidence_paths": context.evidence_paths}
                ))

        return InvariantResult.FAIL if violations else InvariantResult.PASS, violations

    def _validate_repetition(self, context: ValidationContext) -> Tuple[InvariantResult, List[InvariantViolation]]:
        """Validate I10: Repeat Without Correction invariant"""
        violations = []

        # Check for repeated attempts without correction
        if context.previous_attempts:
            repeat_result = self.repetition_prevention.check_repetition(
                context_hash=context.to_hash(),
                previous_attempts=context.previous_attempts
            )

            if not repeat_result.is_valid:
                violations.append(InvariantViolation(
                    invariant_id="I10",
                    violation_type="uncorrected_repetition",
                    message="Action represents uncorrected repetition of previous failure",
                    evidence={"context_hash": context.to_hash(), "previous_attempts": context.previous_attempts}
                ))

        return InvariantResult.FAIL if violations else InvariantResult.PASS, violations

    def _log_violations(self, violations: List[InvariantViolation]):
        """Log violations for learning and audit purposes"""
        for violation in violations:
            self.violations_log.append(violation)
            logger.warning(f"Invariant violation: {violation.invariant_id} - {violation.message}")

        # Write to disk for persistent tracking
        violations_file = os.path.join(self.repo_path, ".hee", "violations", "invariant_violations.json")
        os.makedirs(os.path.dirname(violations_file), exist_ok=True)

        # Load existing violations
        existing_violations = []
        if os.path.exists(violations_file):
            try:
                with open(violations_file, 'r') as f:
                    existing_violations = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load existing violations: {e}")

        # Append new violations
        existing_violations.extend([{
            'invariant_id': v.invariant_id,
            'violation_type': v.violation_type,
            'message': v.message,
            'evidence': v.evidence,
            'timestamp': v.timestamp
        } for v in violations])

        # Write back to disk
        try:
            with open(violations_file, 'w') as f:
                json.dump(existing_violations, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write violations to disk: {e}")

    def get_violation_summary(self) -> Dict[str, Any]:
        """Get summary of all violations for reporting"""
        summary = {
            'total_violations': len(self.violations_log),
            'by_invariant': {},
            'recent_violations': []
        }

        for violation in self.violations_log:
            if violation.invariant_id not in summary['by_invariant']:
                summary['by_invariant'][violation.invariant_id] = 0
            summary['by_invariant'][violation.invariant_id] += 1

        # Show recent violations
        summary['recent_violations'] = [
            {
                'invariant_id': v.invariant_id,
                'message': v.message,
                'timestamp': v.timestamp
            } for v in self.violations_log[-10:]  # Last 10 violations
        ]

        return summary

# Convenience function for quick validation
def validate_hee_action(repo_path: str, agent_type: str, action: str,
                       claims: List[str], evidence_paths: List[str],
                       target_state: Optional[str] = None,
                       previous_attempts: Optional[List[str]] = None) -> Tuple[InvariantResult, List[InvariantViolation]]:
    """
    Quick validation of an HEE action against all invariants.

    Args:
        repo_path: Repository path
        agent_type: Type of agent (chat-agent, gpt-agent, hee-agent)
        action: Description of the action
        claims: List of claims being made
        evidence_paths: Paths to evidence files
        target_state: Target state if state-changing
        previous_attempts: List of previous attempt hashes

    Returns:
        Tuple of (result, violations)
    """
    context = ValidationContext(
        agent_type=agent_type,
        action=action,
        claims=claims,
        evidence_paths=evidence_paths,
        target_state=target_state,
        previous_attempts=previous_attempts or []
    )

    engine = InvariantEnforcementEngine(repo_path)
    return engine.validate_action(context)
