#!/usr/bin/env python3
"""
Cline Adapter for Smart Approval Workflow
Wraps existing approval hook with intelligent decision engine.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add smart approval to path
sys.path.insert(0, str(Path(__file__).parent))

from prototype import CommandSafetyEvaluator

class ClineSmartApprovalAdapter:
    """Adapter that integrates smart approval with Cline's approval workflow"""

    def __init__(self, log_path=None):
        self.evaluator = CommandSafetyEvaluator()
        self.log_path = log_path or Path("var/smart-approval/transcript.jsonl")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize transcript if it doesn't exist
        if not self.log_path.exists():
            self.log_path.touch()

    def evaluate_command(self, command_string, context=None):
        """
        Evaluate command and return Cline-compatible approval decision

        Args:
            command_string: The command to evaluate
            context: Optional context dict (working_dir, user, etc.)

        Returns:
            dict: {
                "requires_approval": bool,
                "confidence": float,
                "reason": str,
                "decision_details": dict
            }
        """
        # Evaluate with smart approval engine
        result = self.evaluator.evaluate_command(command_string)

        # Enhance result with additional context
        result["decision_details"] = {
            "command": command_string,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "working_directory": os.getcwd(),
            "evaluator_version": "1.0",
            "context": context or {}
        }

        # Log decision to transcript
        self._log_decision(result)

        return result

    def _log_decision(self, decision):
        """Log decision to JSON Lines transcript"""
        try:
            with open(self.log_path, 'a') as f:
                json.dump(decision, f)
                f.write('\n')
        except Exception as e:
            # Fail gracefully - don't break command execution
            print(f"Warning: Failed to log approval decision: {e}", file=sys.stderr)

    def get_transcript_summary(self):
        """Get summary statistics from transcript"""
        try:
            decisions = []
            with open(self.log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        decisions.append(json.loads(line))

            total = len(decisions)
            approved = sum(1 for d in decisions if not d.get("requires_approval", True))
            denied = total - approved

            return {
                "total_decisions": total,
                "auto_approved": approved,
                "required_approval": denied,
                "approval_rate": approved / total if total > 0 else 0
            }
        except Exception:
            return {"error": "Failed to read transcript"}

# Cline Integration Hook
# This would be called by Cline before command execution
def cline_approval_hook(command_string, **kwargs):
    """
    Cline approval hook that integrates smart approval workflow

    Returns:
        dict: Cline-compatible approval decision
    """
    adapter = ClineSmartApprovalAdapter()
    result = adapter.evaluate_command(command_string, kwargs)

    # Convert to Cline's expected format
    return {
        "requires_approval": result["requires_approval"],
        "reason": result["reason"],
        "confidence": result["confidence"],
        "details": result["decision_details"]
    }

if __name__ == "__main__":
    # CLI testing interface
    if len(sys.argv) < 2:
        print("Usage: python cline_adapter.py 'command to evaluate'")
        sys.exit(1)

    command = sys.argv[1]
    adapter = ClineSmartApprovalAdapter()
    result = adapter.evaluate_command(command)

    print("Cline Adapter Evaluation:")
    print(f"Command: {command}")
    print(f"Requires Approval: {result['requires_approval']}")
    print(f"Reason: {result['reason']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Logged to: {adapter.log_path}")
