#!/usr/bin/env python3
"""
Unit Tests for Smart Approval Policy Engine
Tests tokenization, deny/allow precedence, git-clean gating.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from prototype import CommandSafetyEvaluator

class TestCommandSafetyEvaluator(unittest.TestCase):
    
    def setUp(self):
        self.evaluator = CommandSafetyEvaluator()
    
    def test_tokenize_simple_command(self):
        """Test basic command tokenization"""
        result = self.evaluator.tokenize_command("ls -la")
        expected = ["ls", "-la"]
        self.assertEqual(result, expected)
    
    def test_tokenize_quoted_command(self):
        """Test tokenization with quoted strings"""
        result = self.evaluator.tokenize_command('echo "hello world"')
        expected = ["echo", '"hello world"']
        self.assertEqual(result, expected)
    
    def test_tokenize_complex_command(self):
        """Test complex command with multiple quotes and flags"""
        result = self.evaluator.tokenize_command('git commit -m "fix: bug in parser" --amend')
        expected = ["git", "commit", "-m", '"fix: bug in parser"', "--amend"]
        self.assertEqual(result, expected)
    
    def test_read_only_prefix_allow(self):
        """Test read-only command prefix matching"""
        result = self.evaluator.evaluate_command("git status")
        self.assertFalse(result["approval_required"])
        self.assertEqual(result["reason"], "read_only_exact")
        self.assertEqual(result["confidence"], 1.0)
    
    def test_read_only_prefix_deny(self):
        """Test dangerous command blocked by deny pattern"""
        result = self.evaluator.evaluate_command("git status > /dev/null")
        self.assertTrue(result["approval_required"])
        self.assertEqual(result["reason"], "denied_pattern_read_only")
        self.assertEqual(result["denied_pattern"], ">")
    
    def test_low_risk_clean_repo(self):
        """Test low-risk command in clean repository"""
        with patch.object(self.evaluator, 'check_git_status', return_value=True):
            result = self.evaluator.evaluate_command("git add .")
            self.assertFalse(result["approval_required"])
            self.assertIn("low_risk_exact_clean", result["reason"])
    
    def test_low_risk_dirty_repo(self):
        """Test low-risk command in dirty repository requires approval"""
        with patch.object(self.evaluator, 'check_git_status', return_value=False):
            result = self.evaluator.evaluate_command("git add .")
            self.assertTrue(result["approval_required"])
            self.assertIn("low_risk_exact_dirty", result["reason"])
    
    def test_dangerous_command_blocked(self):
        """Test dangerous commands are always blocked"""
        dangerous_commands = [
            "rm -rf /",
            "sudo rm -rf /",
            "git push origin main",
            "docker run --privileged",
            "kubectl delete namespace default"
        ]
        
        for cmd in dangerous_commands:
            with self.subTest(command=cmd):
                result = self.evaluator.evaluate_command(cmd)
                self.assertTrue(result["approval_required"], 
                              f"Command should require approval: {cmd}")
                self.assertGreaterEqual(result["confidence"], 0.5)
    
    def test_unknown_command_conservative(self):
        """Test unknown commands default to requiring approval"""
        result = self.evaluator.evaluate_command("unknown_command --flag value")
        self.assertTrue(result["approval_required"])
        self.assertEqual(result["reason"], "unknown_command")
        self.assertEqual(result["confidence"], 0.5)
    
    def test_empty_command_handling(self):
        """Test empty/whitespace commands"""
        result = self.evaluator.evaluate_command("")
        self.assertTrue(result["approval_required"])
        self.assertEqual(result["reason"], "empty_command")
        self.assertEqual(result["confidence"], 0.0)
    
    def test_git_status_check(self):
        """Test git status checking functionality"""
        # Mock subprocess to simulate clean repo
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
            result = self.evaluator.check_git_status()
            self.assertTrue(result)
            
            # Verify git command was called correctly
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            self.assertEqual(args[0], ['git', 'status', '--porcelain'])
    
    def test_git_status_check_error(self):
        """Test git status error handling"""
        with patch('subprocess.run', side_effect=Exception("git not found")):
            result = self.evaluator.check_git_status()
            self.assertFalse(result)  # Should default to False on error

if __name__ == '__main__':
    unittest.main(verbosity=2)
