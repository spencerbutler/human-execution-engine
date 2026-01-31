#!/usr/bin/env python3
"""
Smart Approval Workflow Prototype
Evaluates commands against safety profiles to determine approval requirements.
"""

import sys
import os
import subprocess
import yaml
from pathlib import Path

class CommandSafetyEvaluator:
    def __init__(self, profiles_path=None):
        if profiles_path is None:
            # Look for profiles relative to this script
            script_dir = Path(__file__).parent
            profiles_path = script_dir / "safety_profiles.yml"
        
        with open(profiles_path, 'r') as f:
            self.profiles = yaml.safe_load(f)
    
    def tokenize_command(self, command_string):
        """Tokenize command while preserving quoted strings"""
        tokens = []
        current_token = ""
        in_quotes = False
        quote_char = None
        
        for char in command_string:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_token += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                current_token += char
                quote_char = None
            elif char.isspace() and not in_quotes:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char
        
        if current_token:
            tokens.append(current_token)
        
        return tokens
    
    def check_git_status(self):
        """Check if working directory is clean"""
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=os.getcwd())
            return len(result.stdout.strip()) == 0
        except:
            return False  # Assume not clean if git fails
    
    def evaluate_command(self, command_string):
        """Evaluate command against safety profiles"""
        tokens = self.tokenize_command(command_string)
        if not tokens:
            return {"approval_required": True, "confidence": 0.0, "reason": "empty_command"}
        
        command_base = tokens[0]
        full_command = ' '.join(tokens)
        
        # Check for denied patterns first
        for profile_name, profile in self.profiles['command_safety_profiles']['profiles'].items():
            if 'denylist_contains' in profile:
                for denied in profile['denylist_contains']:
                    # Trim whitespace from denied patterns for matching
                    trimmed_denied = denied.strip()
                    if trimmed_denied in full_command:
                        return {
                            "approval_required": True, 
                            "confidence": 1.0, 
                            "reason": f"denied_pattern_{profile_name}",
                            "denied_pattern": trimmed_denied
                        }

        # Check low_risk profile (requires clean working directory)
        low_risk = self.profiles['command_safety_profiles']['profiles']['low_risk']
        is_clean = self.check_git_status()

        # First check for exact matches in low_risk
        if full_command in low_risk.get('allowlist_exact', []):
            if is_clean:
                return {"approval_required": False, "confidence": 0.95, "reason": "low_risk_exact_clean"}
            else:
                return {"approval_required": True, "confidence": 0.95, "reason": "low_risk_exact_dirty"}

        # Then check for prefix matches in low_risk
        if command_base in low_risk.get('allowlist_prefixes', []):
            # For prefix matches, check if the full command matches any exact commands
            if any(full_command.startswith(exact) for exact in low_risk.get('allowlist_exact', [])):
                if is_clean:
                    return {"approval_required": False, "confidence": 0.95, "reason": "low_risk_exact_clean"}
                else:
                    return {"approval_required": True, "confidence": 0.95, "reason": "low_risk_exact_dirty"}
            else:
                if is_clean:
                    return {"approval_required": False, "confidence": 0.8, "reason": "low_risk_prefix_clean"}
                else:
                    return {"approval_required": True, "confidence": 0.9, "reason": "low_risk_prefix_dirty"}

# Check read_only profile
        read_only = self.profiles['command_safety_profiles']['profiles']['read_only']
        if full_command in read_only.get('allowlist_exact', []):
            return {"approval_required": False, "confidence": 1.0, "reason": "read_only_exact"}

        if command_base in read_only.get('allowlist_prefixes', []):
            return {"approval_required": False, "confidence": 0.9, "reason": "read_only_prefix"}
        
        # Default: require approval for unknown commands
        return {"approval_required": True, "confidence": 0.5, "reason": "unknown_command"}

def main():
    if len(sys.argv) < 2:
        print("Usage: python prototype.py 'command to evaluate'")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        evaluator = CommandSafetyEvaluator()
        result = evaluator.evaluate_command(command)
        
        print(f"Command: {command}")
        print(f"Approval Required: {result['approval_required']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Reason: {result['reason']}")
        
        if 'denied_pattern' in result:
            print(f"Denied Pattern: {result['denied_pattern']}")
            
    except Exception as e:
        print(f"Error evaluating command: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
