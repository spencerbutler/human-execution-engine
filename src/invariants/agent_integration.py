"""
HEE Agent Integration for Invariant Enforcement

Integrates the invariant enforcement system with existing agent types.
Extends the agent taxonomy to include invariant validation requirements.

Integration Points:
- chat-agent: Enhanced with I08 validation for any claims
- gpt-agent: Extended with I08/I09 validation for proposals
- hee-agent: Full integration with all three invariants
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .engine import InvariantEnforcementEngine, ValidationContext, InvariantResult
from .proof.validator import ProofValidator
from .state.gatekeeper import StateChangeGatekeeper
from .learning.prevention import RepetitionPrevention

logger = logging.getLogger(__name__)

class AgentIntegrationMode(Enum):
    """Integration modes for different agent types"""
    STRICT = "strict"  # Full invariant enforcement
    PROPOSAL_ONLY = "proposal_only"  # Only proposal validation
    CONVERSATIONAL = "conversational"  # Minimal validation

@dataclass
class AgentValidationResult:
    """Result of agent validation"""
    is_valid: bool
    violations: List[Dict[str, Any]]
    warnings: List[str]
    integration_mode: AgentIntegrationMode
    message: str = ""

class AgentInvariantIntegration:
    """
    Integrates invariant enforcement with existing agent types.
    
    Provides agent-specific validation based on agent taxonomy.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize agent integration.
        
        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = repo_path
        self.invariant_engine = InvariantEnforcementEngine(repo_path)
        self.integration_modes = self._define_integration_modes()
        
    def _define_integration_modes(self) -> Dict[str, AgentIntegrationMode]:
        """
        Define integration modes for each agent type.
        
        Returns:
            Dictionary mapping agent types to integration modes
        """
        return {
            "chat-agent": AgentIntegrationMode.CONVERSATIONAL,
            "gpt-agent": AgentIntegrationMode.PROPOSAL_ONLY,
            "hee-agent": AgentIntegrationMode.STRICT
        }
    
    def validate_agent_action(self, agent_type: str, action: str, 
                            claims: List[str], evidence_paths: List[str],
                            target_state: Optional[str] = None,
                            previous_attempts: Optional[List[str]] = None) -> AgentValidationResult:
        """
        Validate an agent action against appropriate invariants.
        
        Args:
            agent_type: Type of agent
            action: Description of the action
            claims: List of claims being made
            evidence_paths: Paths to evidence files
            target_state: Target state if state-changing
            previous_attempts: List of previous attempt hashes
            
        Returns:
            AgentValidationResult with validation status
        """
        # Determine integration mode
        integration_mode = self.integration_modes.get(agent_type, AgentIntegrationMode.STRICT)
        
        # Create validation context
        context = ValidationContext(
            agent_type=agent_type,
            action=action,
            claims=claims,
            evidence_paths=evidence_paths,
            target_state=target_state,
            previous_attempts=previous_attempts or []
        )
        
        violations = []
        warnings = []
        
        # Apply validation based on integration mode
        if integration_mode == AgentIntegrationMode.STRICT:
            # Full validation for hee-agent
            result, invariant_violations = self.invariant_engine.validate_action(context)
            violations.extend([{
                'invariant_id': v.invariant_id,
                'violation_type': v.violation_type,
                'message': v.message
            } for v in invariant_violations])
            
        elif integration_mode == AgentIntegrationMode.PROPOSAL_ONLY:
            # Proposal validation for gpt-agent
            if claims:
                proof_validator = ProofValidator(self.repo_path)
                for claim in claims:
                    proof_result = proof_validator.validate_claim(
                        agent_type=agent_type,
                        claim=claim,
                        evidence_paths=evidence_paths
                    )
                    
                    if not proof_result.is_valid:
                        violations.append({
                            'invariant_id': 'I08',
                            'violation_type': 'missing_lane_proof',
                            'message': f"Proposal '{claim}' lacks design evidence"
                        })
            
            # Check for state change attempts (forbidden for gpt-agent)
            if target_state:
                violations.append({
                    'invariant_id': 'I09',
                    'violation_type': 'unauthorized_state_change',
                    'message': 'gpt-agent cannot make state changes without gate approval'
                })
                
        elif integration_mode == AgentIntegrationMode.CONVERSATIONAL:
            # Minimal validation for chat-agent
            if claims and not self._is_conversational_claim(claims):
                warnings.append("chat-agent making non-conversational claims")
                
            # Check for state change attempts (forbidden for chat-agent)
            if target_state:
                violations.append({
                    'invariant_id': 'I09',
                    'violation_type': 'unauthorized_state_change',
                    'message': 'chat-agent cannot make state changes'
                })
        
        # Check for repetition (applies to all agent types)
        if previous_attempts:
            repetition_prevention = RepetitionPrevention(self.repo_path)
            repeat_result = repetition_prevention.check_repetition(
                context_hash=context.to_hash(),
                previous_attempts=previous_attempts
            )
            
            if not repeat_result.is_valid:
                violations.append({
                    'invariant_id': 'I10',
                    'violation_type': 'uncorrected_repetition',
                    'message': repeat_result.message
                })
        
        # Generate message
        if violations:
            message = f"Validation failed with {len(violations)} violations"
        elif warnings:
            message = f"Validation passed with {len(warnings)} warnings"
        else:
            message = "Validation passed"
        
        return AgentValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            integration_mode=integration_mode,
            message=message
        )
    
    def _is_conversational_claim(self, claims: List[str]) -> bool:
        """
        Check if claims are conversational in nature.
        
        Args:
            claims: List of claims
            
        Returns:
            True if claims are conversational, False otherwise
        """
        conversational_keywords = [
            "think", "believe", "suggest", "maybe", "perhaps", "could", "should",
            "idea", "thought", "opinion", "discussion", "conversation"
        ]
        
        for claim in claims:
            claim_lower = claim.lower()
            if any(keyword in claim_lower for keyword in conversational_keywords):
                return True
        
        return False
    
    def get_agent_compliance_report(self, agent_type: str) -> Dict[str, Any]:
        """
        Get compliance report for an agent type.
        
        Args:
            agent_type: Type of agent
            
        Returns:
            Compliance report with statistics
        """
        integration_mode = self.integration_modes.get(agent_type, AgentIntegrationMode.STRICT)
        
        # Get violation summary from engine
        violation_summary = self.invariant_engine.get_violation_summary()
        
        # Filter violations by agent type
        agent_violations = []
        for violation in self.invariant_engine.violations_log:
            if violation.evidence and violation.evidence.get('agent_type') == agent_type:
                agent_violations.append(violation)
        
        return {
            "agent_type": agent_type,
            "integration_mode": integration_mode.value,
            "total_violations": len(agent_violations),
            "violations_by_invariant": self._count_violations_by_invariant(agent_violations),
            "recent_violations": [v.__dict__ for v in agent_violations[-5:]],
            "compliance_score": self._calculate_compliance_score(agent_violations),
            "recommendations": self._generate_recommendations(agent_type, agent_violations)
        }
    
    def _count_violations_by_invariant(self, violations: List) -> Dict[str, int]:
        """Count violations by invariant"""
        counts = {}
        for violation in violations:
            invariant_id = violation.invariant_id
            if invariant_id not in counts:
                counts[invariant_id] = 0
            counts[invariant_id] += 1
        return counts
    
    def _calculate_compliance_score(self, violations: List) -> float:
        """Calculate compliance score (0.0 to 1.0)"""
        if not violations:
            return 1.0
        
        # Weight violations by severity
        severity_weights = {
            'I09': 3.0,  # State changes without evidence - highest severity
            'I08': 2.0,  # Missing proof - medium severity
            'I10': 1.0   # Repetition - lowest severity
        }
        
        total_weight = sum(severity_weights.get(v.invariant_id, 1.0) for v in violations)
        
        # Calculate score (inverse of violation weight)
        max_score = 10.0
        score = max(0.0, max_score - total_weight)
        
        return min(1.0, score / max_score)
    
    def _generate_recommendations(self, agent_type: str, violations: List) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []
        
        # Count violation types
        violation_types = [v.violation_type for v in violations]
        
        if 'missing_lane_proof' in violation_types:
            recommendations.append("Provide lane-appropriate evidence for all claims")
            
        if 'language_only_state_change' in violation_types:
            recommendations.append("Ensure state changes have immutable evidence")
            
        if 'uncorrected_repetition' in violation_types:
            recommendations.append("Apply corrections before retrying failed attempts")
            
        if not recommendations:
            recommendations.append("Maintain current compliance practices")
            
        return recommendations
    
    def enforce_agent_constraints(self, agent_type: str, action: str) -> bool:
        """
        Enforce agent-specific constraints before action execution.
        
        Args:
            agent_type: Type of agent
            action: Action to validate
            
        Returns:
            True if action is allowed, False if blocked
        """
        # Check if agent type is authorized for this action
        authorized_actions = {
            "chat-agent": ["conversational", "informational"],
            "gpt-agent": ["proposal", "planning", "recommendation"],
            "hee-agent": ["execution", "deployment", "verification", "state_change"]
        }
        
        allowed_actions = authorized_actions.get(agent_type, [])
        
        action_lower = action.lower()
        if not any(allowed in action_lower for allowed in allowed_actions):
            logger.warning(f"Agent {agent_type} attempting unauthorized action: {action}")
            return False
        
        return True

# Convenience functions for agent integration
def validate_chat_agent_action(repo_path: str, action: str, claims: List[str], 
                              evidence_paths: List[str]) -> AgentValidationResult:
    """Validate chat-agent action"""
    integration = AgentInvariantIntegration(repo_path)
    return integration.validate_agent_action(
        agent_type="chat-agent",
        action=action,
        claims=claims,
        evidence_paths=evidence_paths
    )

def validate_gpt_agent_action(repo_path: str, action: str, claims: List[str], 
                             evidence_paths: List[str], target_state: Optional[str] = None) -> AgentValidationResult:
    """Validate gpt-agent action"""
    integration = AgentInvariantIntegration(repo_path)
    return integration.validate_agent_action(
        agent_type="gpt-agent",
        action=action,
        claims=claims,
        evidence_paths=evidence_paths,
        target_state=target_state
    )

def validate_hee_agent_action(repo_path: str, action: str, claims: List[str], 
                            evidence_paths: List[str], target_state: Optional[str] = None,
                            previous_attempts: Optional[List[str]] = None) -> AgentValidationResult:
    """Validate hee-agent action"""
    integration = AgentInvariantIntegration(repo_path)
    return integration.validate_agent_action(
        agent_type="hee-agent",
        action=action,
        claims=claims,
        evidence_paths=evidence_paths,
        target_state=target_state,
        previous_attempts=previous_attempts
    )