"""
HEE Proof Validator for I08: Lane Proof Invariant

Validates that claims are supported by lane-appropriate evidence.
Enforces the rule: "Claims require lane-appropriate proof"

Lane Requirements:
- chat-agent: conversational_only, no claims about implementation
- gpt-agent: proposals require design artifacts as proof
- hee-agent: execution claims require actual implementation evidence
"""

import logging
import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class EvidenceType(Enum):
    """Types of evidence for different lanes"""
    DESIGN_SPECIFICATION = "design_specification"
    ARCHITECTURE_DOCUMENT = "architecture_document"
    REQUIREMENT_DOCUMENT = "requirement_document"
    IMPLEMENTATION_CODE = "implementation_code"
    TEST_RESULTS = "test_results"
    DEPLOYMENT_EVIDENCE = "deployment_evidence"
    CONFIGURATION_FILES = "configuration_files"
    LOG_FILES = "log_files"

@dataclass
class ProofValidationResult:
    """Result of proof validation"""
    is_valid: bool
    required_evidence: List[EvidenceType]
    missing_evidence: List[EvidenceType]
    message: str = ""
    evidence_found: List[str] = None
    
    def __post_init__(self):
        if self.evidence_found is None:
            self.evidence_found = []

class ProofValidator:
    """
    Validates claims against lane-appropriate evidence requirements.
    
    I08 Invariant: Claims require lane-appropriate proof
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize the proof validator.
        
        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = repo_path
        self.evidence_patterns = self._load_evidence_patterns()
        
    def _load_evidence_patterns(self) -> Dict[str, Dict[str, List[EvidenceType]]]:
        """
        Load evidence requirements for different agent types and claim types.
        
        Returns:
            Dictionary mapping agent_type -> claim_type -> required_evidence
        """
        return {
            "chat-agent": {
                "conversational": [],  # No evidence required for conversation
                "implementation": [EvidenceType.IMPLEMENTATION_CODE],  # Forbidden
                "design": [EvidenceType.DESIGN_SPECIFICATION],  # Forbidden
            },
            "gpt-agent": {
                "proposal": [EvidenceType.DESIGN_SPECIFICATION, EvidenceType.ARCHITECTURE_DOCUMENT],
                "plan": [EvidenceType.REQUIREMENT_DOCUMENT, EvidenceType.DESIGN_SPECIFICATION],
                "recommendation": [EvidenceType.DESIGN_SPECIFICATION],
                "implementation": [EvidenceType.IMPLEMENTATION_CODE],  # Forbidden without gate
            },
            "hee-agent": {
                "execution": [EvidenceType.IMPLEMENTATION_CODE, EvidenceType.TEST_RESULTS],
                "deployment": [EvidenceType.DEPLOYMENT_EVIDENCE, EvidenceType.CONFIGURATION_FILES],
                "verification": [EvidenceType.LOG_FILES, EvidenceType.TEST_RESULTS],
                "proposal": [EvidenceType.DESIGN_SPECIFICATION],  # Should have human approval
            }
        }
    
    def validate_claim(self, agent_type: str, claim: str, evidence_paths: List[str]) -> ProofValidationResult:
        """
        Validate a claim against lane-appropriate evidence.
        
        Args:
            agent_type: Type of agent making the claim
            claim: The claim being made
            evidence_paths: Paths to evidence files
            
        Returns:
            ProofValidationResult indicating validation status
        """
        # Determine claim type from the claim text
        claim_type = self._classify_claim(claim)
        
        # Get required evidence for this agent type and claim type
        required_evidence = self._get_required_evidence(agent_type, claim_type)
        
        # If no evidence required, validation passes
        if not required_evidence:
            if agent_type == "chat-agent" and claim_type != "conversational":
                return ProofValidationResult(
                    is_valid=False,
                    required_evidence=required_evidence,
                    missing_evidence=required_evidence,
                    message=f"chat-agent cannot make {claim_type} claims"
                )
            return ProofValidationResult(
                is_valid=True,
                required_evidence=required_evidence,
                missing_evidence=[],
                message="No evidence required for this claim type"
            )
        
        # Find evidence files that match required types
        evidence_found = []
        missing_evidence = []
        
        for evidence_type in required_evidence:
            found_files = self._find_evidence_files(evidence_paths, evidence_type)
            if found_files:
                evidence_found.extend(found_files)
            else:
                missing_evidence.append(evidence_type)
        
        # Determine validation result
        if missing_evidence:
            return ProofValidationResult(
                is_valid=False,
                required_evidence=required_evidence,
                missing_evidence=missing_evidence,
                message=f"Missing evidence: {[e.value for e in missing_evidence]}",
                evidence_found=evidence_found
            )
        else:
            return ProofValidationResult(
                is_valid=True,
                required_evidence=required_evidence,
                missing_evidence=[],
                message="All required evidence found",
                evidence_found=evidence_found
            )
    
    def _classify_claim(self, claim: str) -> str:
        """
        Classify a claim into a claim type based on keywords.
        
        Args:
            claim: The claim text
            
        Returns:
            Claim type (proposal, plan, recommendation, implementation, deployment, verification, conversational)
        """
        claim_lower = claim.lower()
        
        # Implementation claims
        if any(keyword in claim_lower for keyword in [
            "implement", "code", "write", "build", "create", "develop", "execute"
        ]):
            return "implementation"
            
        # Design/proposal claims
        elif any(keyword in claim_lower for keyword in [
            "propose", "suggest", "recommend", "plan", "design", "architecture"
        ]):
            return "proposal"
            
        # Planning claims
        elif any(keyword in claim_lower for keyword in [
            "plan", "schedule", "timeline", "roadmap", "strategy"
        ]):
            return "plan"
            
        # Recommendation claims
        elif any(keyword in claim_lower for keyword in [
            "recommend", "suggest", "advise", "should", "could"
        ]):
            return "recommendation"
            
        # Deployment claims
        elif any(keyword in claim_lower for keyword in [
            "deploy", "release", "publish", "ship", "production"
        ]):
            return "deployment"
            
        # Verification claims
        elif any(keyword in claim_lower for keyword in [
            "verify", "validate", "test", "check", "confirm", "audit"
        ]):
            return "verification"
            
        # Conversational claims (default for chat-agent)
        else:
            return "conversational"
    
    def _get_required_evidence(self, agent_type: str, claim_type: str) -> List[EvidenceType]:
        """
        Get required evidence types for an agent type and claim type.
        
        Args:
            agent_type: Type of agent
            claim_type: Type of claim
            
        Returns:
            List of required evidence types
        """
        agent_patterns = self.evidence_patterns.get(agent_type, {})
        return agent_patterns.get(claim_type, [])
    
    def _find_evidence_files(self, evidence_paths: List[str], evidence_type: EvidenceType) -> List[str]:
        """
        Find evidence files that match a specific evidence type.
        
        Args:
            evidence_paths: List of evidence file paths
            evidence_type: Type of evidence to find
            
        Returns:
            List of matching file paths
        """
        matching_files = []
        
        # Define patterns for each evidence type
        patterns = {
            EvidenceType.DESIGN_SPECIFICATION: ["design", "spec", "specification"],
            EvidenceType.ARCHITECTURE_DOCUMENT: ["architecture", "arch", "design"],
            EvidenceType.REQUIREMENT_DOCUMENT: ["requirements", "requirement", "req"],
            EvidenceType.IMPLEMENTATION_CODE: ["src", "lib", "code", "implementation"],
            EvidenceType.TEST_RESULTS: ["test", "spec", "test_results"],
            EvidenceType.DEPLOYMENT_EVIDENCE: ["deploy", "release", "ci", "cd"],
            EvidenceType.CONFIGURATION_FILES: ["config", "settings", "env", "cfg"],
            EvidenceType.LOG_FILES: ["log", "audit", "trace", "debug"]
        }
        
        search_patterns = patterns.get(evidence_type, [])
        
        for path in evidence_paths:
            # Check if path contains any of the patterns
            path_lower = path.lower()
            if any(pattern in path_lower for pattern in search_patterns):
                matching_files.append(path)
                
        return matching_files
    
    def validate_evidence_immutability(self, evidence_paths: List[str]) -> Dict[str, bool]:
        """
        Validate that evidence files are immutable (cannot be easily modified).
        
        Args:
            evidence_paths: List of evidence file paths
            
        Returns:
            Dictionary mapping file paths to immutability status
        """
        immutability_status = {}
        
        for path in evidence_paths:
            full_path = os.path.join(self.repo_path, path)
            
            # Check if file exists
            if not os.path.exists(full_path):
                immutability_status[path] = False
                continue
                
            # Check file permissions and git status
            try:
                # Check if file is tracked by git (provides immutability)
                import subprocess
                result = subprocess.run(
                    ['git', 'ls-files', path],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0 and path in result.stdout:
                    # File is tracked by git - consider immutable
                    immutability_status[path] = True
                else:
                    # File not tracked by git - not immutable
                    immutability_status[path] = False
                    
            except Exception as e:
                logger.warning(f"Failed to check immutability for {path}: {e}")
                immutability_status[path] = False
                
        return immutability_status
    
    def generate_proof_report(self, agent_type: str, claims: List[str], evidence_paths: List[str]) -> Dict[str, Any]:
        """
        Generate a comprehensive proof validation report.
        
        Args:
            agent_type: Type of agent
            claims: List of claims being made
            evidence_paths: Paths to evidence files
            
        Returns:
            Comprehensive validation report
        """
        report = {
            "agent_type": agent_type,
            "timestamp": datetime.now().isoformat(),
            "claims": [],
            "evidence_analysis": {},
            "overall_status": "unknown",
            "violations": []
        }
        
        all_valid = True
        
        # Validate each claim
        for claim in claims:
            validation_result = self.validate_claim(agent_type, claim, evidence_paths)
            
            claim_report = {
                "claim": claim,
                "claim_type": self._classify_claim(claim),
                "is_valid": validation_result.is_valid,
                "required_evidence": [e.value for e in validation_result.required_evidence],
                "missing_evidence": [e.value for e in validation_result.missing_evidence],
                "evidence_found": validation_result.evidence_found,
                "message": validation_result.message
            }
            
            report["claims"].append(claim_report)
            
            if not validation_result.is_valid:
                all_valid = False
                report["violations"].append({
                    "claim": claim,
                    "violation": validation_result.message
                })
        
        # Analyze evidence immutability
        immutability_status = self.validate_evidence_immutability(evidence_paths)
        report["evidence_analysis"] = {
            "total_evidence": len(evidence_paths),
            "immutable_evidence": sum(1 for status in immutability_status.values() if status),
            "evidence_immutability": immutability_status
        }
        
        # Determine overall status
        if all_valid and report["evidence_analysis"]["immutable_evidence"] > 0:
            report["overall_status"] = "pass"
        elif not all_valid:
            report["overall_status"] = "fail"
        else:
            report["overall_status"] = "warning"
            
        return report