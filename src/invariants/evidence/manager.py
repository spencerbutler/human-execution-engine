"""
HEE Evidence Manager for Immutable Evidence Storage

Manages evidence lifecycle for all three invariants:
- I08: Lane-appropriate evidence storage and validation
- I09: Immutable evidence for state changes
- I10: Evidence tracking for learning and repetition prevention

Key Functions:
- Store and organize evidence by type and lane
- Validate evidence immutability and integrity
- Provide evidence lookup and retrieval
- Maintain evidence lifecycle and cleanup
"""

import logging
import os
import json
import shutil
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import hashlib
import subprocess

logger = logging.getLogger(__name__)

class EvidenceCategory(Enum):
    """Categories of evidence"""
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    CONFIGURATION = "configuration"
    AUDIT = "audit"
    LEARNING = "learning"

@dataclass
class EvidenceRecord:
    """Record of stored evidence"""
    evidence_id: str
    file_path: str
    category: EvidenceCategory
    agent_type: str
    timestamp: str
    hash_value: str
    lane: str
    immutable: bool = False
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class EvidenceManager:
    """
    Manages evidence storage, validation, and lifecycle.
    
    Provides immutable evidence storage for all HEE invariants.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize the evidence manager.
        
        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = repo_path
        self.evidence_root = os.path.join(repo_path, ".hee", "evidence")
        self.evidence_index_file = os.path.join(self.evidence_root, "evidence_index.json")
        
        self._ensure_evidence_directories()
        self.evidence_index = self._load_evidence_index()
        
    def _ensure_evidence_directories(self):
        """Ensure evidence directories exist"""
        # Create main evidence directory
        os.makedirs(self.evidence_root, exist_ok=True)
        
        # Create subdirectories for each category
        for category in EvidenceCategory:
            category_dir = os.path.join(self.evidence_root, category.value)
            os.makedirs(category_dir, exist_ok=True)
    
    def _load_evidence_index(self) -> Dict[str, EvidenceRecord]:
        """Load evidence index from disk"""
        if not os.path.exists(self.evidence_index_file):
            return {}
        
        try:
            with open(self.evidence_index_file, 'r') as f:
                data = json.load(f)
                return {eid: EvidenceRecord(**record) for eid, record in data.items()}
        except Exception as e:
            logger.error(f"Failed to load evidence index: {e}")
            return {}
    
    def _save_evidence_index(self):
        """Save evidence index to disk"""
        try:
            with open(self.evidence_index_file, 'w') as f:
                data = {eid: record.__dict__ for eid, record in self.evidence_index.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save evidence index: {e}")
    
    def store_evidence(self, file_path: str, category: EvidenceCategory, 
                      agent_type: str, lane: str, metadata: Optional[Dict[str, Any]] = None) -> EvidenceRecord:
        """
        Store evidence file with proper categorization and indexing.
        
        Args:
            file_path: Path to the evidence file
            category: Category of the evidence
            agent_type: Type of agent providing evidence
            lane: Lane context for the evidence
            metadata: Additional metadata about the evidence
            
        Returns:
            EvidenceRecord of the stored evidence
        """
        # Generate evidence ID
        evidence_id = self._generate_evidence_id(file_path, category, agent_type, lane)
        
        # Calculate file hash for integrity
        hash_value = self._calculate_file_hash(file_path)
        
        # Determine storage path
        storage_path = self._get_storage_path(evidence_id, category)
        
        # Copy file to evidence storage
        try:
            shutil.copy2(file_path, storage_path)
        except Exception as e:
            logger.error(f"Failed to copy evidence file {file_path}: {e}")
            raise
        
        # Check if file is tracked by git (immutable)
        immutable = self._is_file_tracked_by_git(storage_path)
        
        # Create evidence record
        evidence_record = EvidenceRecord(
            evidence_id=evidence_id,
            file_path=storage_path,
            category=category,
            agent_type=agent_type,
            timestamp=datetime.now().isoformat(),
            hash_value=hash_value,
            lane=lane,
            immutable=immutable,
            metadata=metadata or {}
        )
        
        # Add to index
        self.evidence_index[evidence_id] = evidence_record
        self._save_evidence_index()
        
        logger.info(f"Stored evidence {evidence_id} in category {category.value}")
        
        return evidence_record
    
    def retrieve_evidence(self, evidence_id: str) -> Optional[EvidenceRecord]:
        """
        Retrieve evidence record by ID.
        
        Args:
            evidence_id: ID of the evidence to retrieve
            
        Returns:
            EvidenceRecord if found, None otherwise
        """
        return self.evidence_index.get(evidence_id)
    
    def find_evidence(self, category: Optional[EvidenceCategory] = None,
                     agent_type: Optional[str] = None,
                     lane: Optional[str] = None,
                     time_range: Optional[tuple] = None) -> List[EvidenceRecord]:
        """
        Find evidence matching criteria.
        
        Args:
            category: Category to filter by
            agent_type: Agent type to filter by
            lane: Lane to filter by
            time_range: Tuple of (start_time, end_time) to filter by
            
        Returns:
            List of matching evidence records
        """
        matching_evidence = []
        
        for evidence in self.evidence_index.values():
            # Apply filters
            if category and evidence.category != category:
                continue
            if agent_type and evidence.agent_type != agent_type:
                continue
            if lane and evidence.lane != lane:
                continue
            if time_range:
                evidence_time = datetime.fromisoformat(evidence.timestamp)
                start_time, end_time = time_range
                if evidence_time < start_time or evidence_time > end_time:
                    continue
            
            matching_evidence.append(evidence)
        
        # Sort by timestamp, most recent first
        matching_evidence.sort(key=lambda x: x.timestamp, reverse=True)
        return matching_evidence
    
    def validate_evidence_integrity(self, evidence_id: str) -> bool:
        """
        Validate that evidence file has not been tampered with.
        
        Args:
            evidence_id: ID of the evidence to validate
            
        Returns:
            True if evidence is valid, False otherwise
        """
        evidence = self.evidence_index.get(evidence_id)
        if not evidence:
            logger.warning(f"Evidence {evidence_id} not found in index")
            return False
        
        # Calculate current hash
        current_hash = self._calculate_file_hash(evidence.file_path)
        
        # Compare with stored hash
        if current_hash != evidence.hash_value:
            logger.error(f"Evidence {evidence_id} integrity check failed")
            return False
        
        return True
    
    def get_lane_appropriate_evidence(self, agent_type: str, claim_type: str) -> List[EvidenceRecord]:
        """
        Get evidence that is appropriate for the agent's lane and claim type.
        
        Args:
            agent_type: Type of agent
            claim_type: Type of claim being made
            
        Returns:
            List of lane-appropriate evidence
        """
        # Define lane-appropriate evidence requirements
        lane_requirements = {
            "chat-agent": {
                "conversational": [],
                "implementation": [],  # Forbidden
                "design": []  # Forbidden
            },
            "gpt-agent": {
                "proposal": [EvidenceCategory.DESIGN],
                "plan": [EvidenceCategory.DESIGN],
                "recommendation": [EvidenceCategory.DESIGN],
                "implementation": []  # Forbidden without gate
            },
            "hee-agent": {
                "execution": [EvidenceCategory.IMPLEMENTATION, EvidenceCategory.TESTING],
                "deployment": [EvidenceCategory.DEPLOYMENT, EvidenceCategory.CONFIGURATION],
                "verification": [EvidenceCategory.AUDIT, EvidenceCategory.TESTING],
                "proposal": [EvidenceCategory.DESIGN]  # Should have human approval
            }
        }
        
        required_categories = lane_requirements.get(agent_type, {}).get(claim_type, [])
        
        # Find evidence matching required categories
        matching_evidence = []
        for evidence in self.evidence_index.values():
            if evidence.category in required_categories and evidence.immutable:
                matching_evidence.append(evidence)
        
        return matching_evidence
    
    def cleanup_old_evidence(self, days_to_keep: int = 30):
        """
        Clean up old evidence files that are no longer needed.
        
        Args:
            days_to_keep: Number of days to keep evidence files
        """
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
        
        cleaned_count = 0
        for evidence_id, evidence in list(self.evidence_index.items()):
            evidence_time = datetime.fromisoformat(evidence.timestamp).timestamp()
            
            # Only clean up non-immutable evidence
            if not evidence.immutable and evidence_time < cutoff_time:
                try:
                    os.remove(evidence.file_path)
                    del self.evidence_index[evidence_id]
                    cleaned_count += 1
                    logger.info(f"Cleaned up old evidence {evidence_id}")
                except Exception as e:
                    logger.error(f"Failed to clean up evidence {evidence_id}: {e}")
        
        if cleaned_count > 0:
            self._save_evidence_index()
            logger.info(f"Cleaned up {cleaned_count} old evidence files")
    
    def get_evidence_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about stored evidence.
        
        Returns:
            Evidence summary statistics
        """
        total_evidence = len(self.evidence_index)
        immutable_count = sum(1 for evidence in self.evidence_index.values() if evidence.immutable)
        
        # Group by category
        by_category = {}
        for evidence in self.evidence_index.values():
            category = evidence.category.value
            if category not in by_category:
                by_category[category] = 0
            by_category[category] += 1
        
        # Group by agent type
        by_agent = {}
        for evidence in self.evidence_index.values():
            agent_type = evidence.agent_type
            if agent_type not in by_agent:
                by_agent[agent_type] = 0
            by_agent[agent_type] += 1
        
        # Group by lane
        by_lane = {}
        for evidence in self.evidence_index.values():
            lane = evidence.lane
            if lane not in by_lane:
                by_lane[lane] = 0
            by_lane[lane] += 1
        
        return {
            "total_evidence": total_evidence,
            "immutable_evidence": immutable_count,
            "mutable_evidence": total_evidence - immutable_count,
            "by_category": by_category,
            "by_agent_type": by_agent,
            "by_lane": by_lane,
            "recent_evidence": [e.__dict__ for e in list(self.evidence_index.values())[-10:]]
        }
    
    def _generate_evidence_id(self, file_path: str, category: EvidenceCategory, 
                            agent_type: str, lane: str) -> str:
        """
        Generate unique evidence ID based on file content and metadata.
        
        Args:
            file_path: Path to the evidence file
            category: Category of the evidence
            agent_type: Type of agent
            lane: Lane context
            
        Returns:
            Unique evidence ID
        """
        # Calculate file hash
        file_hash = self._calculate_file_hash(file_path)
        
        # Create ID from hash and metadata
        id_data = f"{file_hash}_{category.value}_{agent_type}_{lane}"
        return hashlib.sha256(id_data.encode()).hexdigest()[:16]
    
    def _get_storage_path(self, evidence_id: str, category: EvidenceCategory) -> str:
        """
        Get storage path for evidence file.
        
        Args:
            evidence_id: ID of the evidence
            category: Category of the evidence
            
        Returns:
            Storage path for the evidence file
        """
        return os.path.join(self.evidence_root, category.value, f"{evidence_id}.evidence")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA256 hash of the file
        """
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def _is_file_tracked_by_git(self, file_path: str) -> bool:
        """
        Check if a file is tracked by git.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is tracked by git, False otherwise
        """
        try:
            result = subprocess.run(
                ['git', 'ls-files', file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and file_path in result.stdout
        except Exception as e:
            logger.warning(f"Failed to check git status for {file_path}: {e}")
            return False