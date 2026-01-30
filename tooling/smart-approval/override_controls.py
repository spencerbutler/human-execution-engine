"""
Override Controls for Smart Approval Workflow
Allows explicit user control over approval decisions.
"""

class ApprovalOverrideController:
    """Manages explicit user overrides for approval decisions"""
    
    def __init__(self):
        self.overrides = {}
    
    def force_approve(self, command_pattern):
        """Force approve commands matching pattern"""
        self.overrides[command_pattern] = "force_approve"
    
    def force_prompt(self, command_pattern):
        """Force prompt for commands matching pattern"""
        self.overrides[command_pattern] = "force_prompt"
    
    def clear_override(self, command_pattern):
        """Clear override for pattern"""
        self.overrides.pop(command_pattern, None)
    
    def apply_override(self, command, base_decision):
        """Apply any matching overrides to base decision"""
        for pattern, action in self.overrides.items():
            if pattern in command:
                if action == "force_approve":
                    return {**base_decision, "requires_approval": False, 
                           "override_applied": True, "override_reason": f"force_approve:{pattern}"}
                elif action == "force_prompt":
                    return {**base_decision, "requires_approval": True,
                           "override_applied": True, "override_reason": f"force_prompt:{pattern}"}
        
        return {**base_decision, "override_applied": False}
