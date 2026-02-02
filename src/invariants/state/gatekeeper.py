"""
HEE State Change Gatekeeper for I09: Words Not State Invariant

Enforces the rule: "Language alone cannot change system state"
Prevents state changes based solely on claims/words without immutable evidence.

Key Functions:
- Validate state change requests require proper evidence
- Block language-only state modifications
- Maintain audit trail of state change attempts
- Integrate with evidence management system
"""

import logging
import os
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class StateChangeType(Enum):
    """Types of state changes that require validation"""
    FILE_MODIFICATION = "file_modification"
    CONFIGURATION_CHANGE = "configuration_change"
    DEPLOYMENT = "deployment"
    DATABASE_CHANGE = "database_change"
    SYSTEM_SETTING = "system_setting"
    SECURITY_POLICY = "security_policy"

@dataclass
class StateChangeRequest:
    """Represents a state change request"""
    agent_type: str
    change_type: StateChangeType
    target_path: str
    change_description: str
    evidence_paths: List[str]
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class StateChangeValidationResult:
    """Result of state change validation"""
    is_valid: bool
    required_evidence: List[str]
    evidence_status: Dict[str, bool]
    message: str = ""
    audit_log: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.audit_log is None:
            self.audit_log = []

class StateChangeGatekeeper:
    """
    Gatekeeper that prevents state changes based solely on language/claims.

    I09 Invariant: Language alone cannot change system state
    """

    def __init__(self, repo_path: str):
        """
        Initialize the state change gatekeeper.

        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = repo_path
        self.evidence_requirements = self._load_evidence_requirements()
        self.audit_log_file = os.path.join(repo_path, ".hee", "audit", "state_changes.json")
        self._ensure_audit_directory()

    def _load_evidence_requirements(self) -> Dict[StateChangeType, List[str]]:
        """
        Load evidence requirements for different state change types.

        Returns:
            Dictionary mapping state change types to required evidence
        """
        return {
            StateChangeType.FILE_MODIFICATION: [
                "implementation_code",
                "test_results"
            ],
            StateChangeType.CONFIGURATION_CHANGE: [
                "configuration_files",
                "deployment_evidence"
            ],
            StateChangeType.DEPLOYMENT: [
                "deployment_evidence",
                "test_results",
                "configuration_files"
            ],
            StateChangeType.DATABASE_CHANGE: [
                "implementation_code",
                "migration_scripts",
                "backup_evidence"
            ],
            StateChangeType.SYSTEM_SETTING: [
                "configuration_files",
                "security_approval"
            ],
            StateChangeType.SECURITY_POLICY: [
                "security_approval",
                "risk_assessment",
                "implementation_code"
            ]
        }

    def _ensure_audit_directory(self):
        """Ensure audit directory exists"""
        os.makedirs(os.path.dirname(self.audit_log_file), exist_ok=True)

    def validate_state_change(self, agent_type: str, target_state: str,
                            evidence_paths: List[str]) -> StateChangeValidationResult:
        """
        Validate a state change request against I09 invariant.

        Args:
            agent_type: Type of agent requesting change
            target_state: Description of target state
            evidence_paths: Paths to evidence files

        Returns:
            StateChangeValidationResult indicating validation status
        """
        # Classify the state change type
        change_type = self._classify_state_change(target_state)

        # Get required evidence for this change type
        required_evidence = self.evidence_requirements.get(change_type, [])

        # Check if agent type is authorized for this change
        authorization_result = self._check_agent_authorization(agent_type, change_type)

        # Validate evidence presence and immutability
        evidence_status = self._validate_evidence(evidence_paths, required_evidence)

        # Determine overall validation result
        is_valid = (
            authorization_result.is_authorized and
            all(evidence_status.values()) and
            len(evidence_status) > 0
        )

        # Generate message
        if not authorization_result.is_authorized:
            message = f"Agent type '{agent_type}' not authorized for {change_type.value} changes"
        elif not evidence_status:
            message = "No evidence provided for state change"
        elif not all(evidence_status.values()):
            missing = [evidence for evidence, status in evidence_status.items() if not status]
            message = f"Missing immutable evidence: {missing}"
        else:
            message = "State change validation passed"

        # Create audit log entry
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_type": agent_type,
            "change_type": change_type.value,
            "target_state": target_state,
            "evidence_paths": evidence_paths,
            "is_valid": is_valid,
            "message": message,
            "required_evidence": required_evidence,
            "evidence_status": evidence_status
        }

        # Log the audit entry
        self._log_audit_entry(audit_entry)

        return StateChangeValidationResult(
            is_valid=is_valid,
            required_evidence=required_evidence,
            evidence_status=evidence_status,
            message=message,
            audit_log=[audit_entry]
        )

    def _classify_state_change(self, target_state: str) -> StateChangeType:
        """
        Classify a state change based on the target state description.

        Args:
            target_state: Description of the target state

        Returns:
            StateChangeType classification
        """
        state_lower = target_state.lower()

        # File modification
        if any(keyword in state_lower for keyword in [
            "file", "code", "source", "implementation", "modify", "update", "create", "delete"
        ]):
            return StateChangeType.FILE_MODIFICATION

        # Configuration change
        elif any(keyword in state_lower for keyword in [
            "config", "setting", "environment", "variable", "parameter", "option"
        ]):
            return StateChangeType.CONFIGURATION_CHANGE

        # Deployment
        elif any(keyword in state_lower for keyword in [
            "deploy", "release", "publish", "production", "staging", "environment"
        ]):
            return StateChangeType.DEPLOYMENT

        # Database change
        elif any(keyword in state_lower for keyword in [
            "database", "db", "migration", "schema", "table", "query", "data"
        ]):
            return StateChangeType.DATABASE_CHANGE

        # System setting
        elif any(keyword in state_lower for keyword in [
            "system", "os", "kernel", "service", "daemon", "process"
        ]):
            return StateChangeType.SYSTEM_SETTING

        # Security policy
        elif any(keyword in state_lower for keyword in [
            "security", "policy", "permission", "access", "auth", "encrypt", "firewall"
        ]):
            return StateChangeType.SECURITY_POLICY

        # Default to file modification
        return StateChangeType.FILE_MODIFICATION

    def _check_agent_authorization(self, agent_type: str, change_type: StateChangeType) -> Any:
        """
        Check if an agent type is authorized for a specific state change type.

        Args:
            agent_type: Type of agent
            change_type: Type of state change

        Returns:
            Authorization result object
        """
        # Define authorization rules
        authorization_rules = {
            "chat-agent": [],  # chat-agent cannot make state changes
            "gpt-agent": [StateChangeType.FILE_MODIFICATION],  # gpt-agent can propose file changes only
            "hee-agent": list(StateChangeType)  # hee-agent can make all state changes with evidence
        }

        authorized_changes = authorization_rules.get(agent_type, [])

        class AuthorizationResult:
            def __init__(self, is_authorized: bool, message: str = ""):
                self.is_authorized = is_authorized
                self.message = message

        if change_type in authorized_changes:
            return AuthorizationResult(True, f"{agent_type} authorized for {change_type.value}")
        else:
            return AuthorizationResult(False, f"{agent_type} not authorized for {change_type.value}")

    def _validate_evidence(self, evidence_paths: List[str],
                          required_evidence: List[str]) -> Dict[str, bool]:
        """
        Validate that required evidence is present and immutable.

        Args:
            evidence_paths: List of evidence file paths
            required_evidence: List of required evidence types

        Returns:
            Dictionary mapping evidence types to immutability status
        """
        evidence_status = {}

        for evidence_type in required_evidence:
            # Find files that match this evidence type
            matching_files = self._find_evidence_files(evidence_paths, evidence_type)

            if not matching_files:
                evidence_status[evidence_type] = False
                continue

            # Check if any matching files are immutable
            immutable_found = False
            for file_path in matching_files:
                if self._is_file_immutable(file_path):
                    immutable_found = True
                    break

            evidence_status[evidence_type] = immutable_found

        return evidence_status

    def _find_evidence_files(self, evidence_paths: List[str], evidence_type: str) -> List[str]:
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
            "implementation_code": ["src", "lib", "code", "implementation", ".py", ".js", ".rs"],
            "test_results": ["test", "spec", "test_results", "coverage", ".spec", ".test"],
            "configuration_files": ["config", "settings", "env", "cfg", ".config", ".env"],
            "deployment_evidence": ["deploy", "release", "ci", "cd", "docker", "k8s"],
            "migration_scripts": ["migration", "migrate", "schema", "db"],
            "backup_evidence": ["backup", "dump", "export", "snapshot"],
            "security_approval": ["security", "approval", "audit", "compliance"],
            "risk_assessment": ["risk", "assessment", "security", "threat"]
        }

        search_patterns = patterns.get(evidence_type, [])

        for path in evidence_paths:
            # Check if path contains any of the patterns
            path_lower = path.lower()
            if any(pattern in path_lower for pattern in search_patterns):
                matching_files.append(path)

        return matching_files

    def _is_file_immutable(self, file_path: str) -> bool:
        """
        Check if a file is immutable (tracked by git and cannot be easily modified).

        Args:
            file_path: Path to the file

        Returns:
            True if file is immutable, False otherwise
        """
        full_path = os.path.join(self.repo_path, file_path)

        # Check if file exists
        if not os.path.exists(full_path):
            return False

        try:
            # Check if file is tracked by git
            import subprocess
            result = subprocess.run(
                ['git', 'ls-files', file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and file_path in result.stdout:
                # File is tracked by git - consider immutable
                return True
            else:
                # File not tracked by git - not immutable
                return False

        except Exception as e:
            logger.warning(f"Failed to check immutability for {file_path}: {e}")
            return False

    def _log_audit_entry(self, audit_entry: Dict[str, Any]):
        """
        Log an audit entry to the audit file.

        Args:
            audit_entry: Audit entry to log
        """
        # Load existing audit log
        audit_log = []
        if os.path.exists(self.audit_log_file):
            try:
                with open(self.audit_log_file, 'r') as f:
                    audit_log = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load existing audit log: {e}")

        # Append new entry
        audit_log.append(audit_entry)

        # Write back to file
        try:
            with open(self.audit_log_file, 'w') as f:
                json.dump(audit_log, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def get_audit_summary(self) -> Dict[str, Any]:
        """
        Get a summary of state change audit log.

        Returns:
            Audit summary statistics
        """
        if not os.path.exists(self.audit_log_file):
            return {"total_requests": 0, "approved": 0, "rejected": 0, "by_agent_type": {}}

        try:
            with open(self.audit_log_file, 'r') as f:
                audit_log = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load audit log for summary: {e}")
            return {"total_requests": 0, "approved": 0, "rejected": 0, "by_agent_type": {}}

        # Calculate summary statistics
        total_requests = len(audit_log)
        approved = sum(1 for entry in audit_log if entry.get("is_valid", False))
        rejected = total_requests - approved

        # Group by agent type
        by_agent_type = {}
        for entry in audit_log:
            agent_type = entry.get("agent_type", "unknown")
            if agent_type not in by_agent_type:
                by_agent_type[agent_type] = {"total": 0, "approved": 0, "rejected": 0}

            by_agent_type[agent_type]["total"] += 1
            if entry.get("is_valid", False):
                by_agent_type[agent_type]["approved"] += 1
            else:
                by_agent_type[agent_type]["rejected"] += 1

        return {
            "total_requests": total_requests,
            "approved": approved,
            "rejected": rejected,
            "by_agent_type": by_agent_type,
            "recent_entries": audit_log[-10:]  # Last 10 entries
        }

    def block_state_change(self, agent_type: str, target_state: str, reason: str) -> Dict[str, Any]:
        """
        Record a blocked state change attempt.

        Args:
            agent_type: Type of agent attempting change
            target_state: Description of target state
            reason: Reason for blocking

        Returns:
            Block record
        """
        block_record = {
            "timestamp": datetime.now().isoformat(),
            "agent_type": agent_type,
            "target_state": target_state,
            "reason": reason,
            "type": "blocked_state_change"
        }

        # Log to audit file
        self._log_audit_entry(block_record)

        logger.warning(f"Blocked state change: {agent_type} -> {target_state} - {reason}")

        return block_record
