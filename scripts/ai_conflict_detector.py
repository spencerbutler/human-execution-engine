#!/usr/bin/env python3
"""
AI-Assisted Conflict Detection System
Intelligent analysis and prevention of merge conflicts in HEE development.
"""

import json
import os
import re
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set


class AIConflictDetector:
    """AI-assisted merge conflict detection and prevention system."""

    def __init__(self):
        self.conflict_patterns = {
            'high_risk': [
                r'docs/.*\.md$',           # Documentation files
                r'prompts/.*\.md$',        # Prompt files
                r'\.github/workflows/.*',  # CI/CD workflows
                r'docs/history/state_capsules/',  # State capsules
            ],
            'medium_risk': [
                r'scripts/.*\.py$',        # Python scripts
                r'scripts/.*\.sh$',        # Shell scripts
                r'\.pre-commit-config\.yaml',  # Pre-commit config
            ],
            'low_risk': [
                r'README\.md$',           # Root README
                r'CHANGELOG\.md$',        # Changelog
                r'\.gitignore$',          # Git ignore
            ]
        }

        self.risk_scores = {
            'high_risk': 3.0,
            'medium_risk': 2.0,
            'low_risk': 1.0
        }

    def analyze_branch_conflict_risk(self, branch_name: str = 'HEAD') -> Dict:
        """Analyze conflict risk for a branch compared to main."""
        try:
            # Get files changed in branch
            branch_files = self.get_changed_files(branch_name)

            # Get files changed in main since branch point
            main_files = self.get_changed_files('origin/main', since_branch=branch_name)

            # Find overlapping files
            overlapping = set(branch_files.keys()) & set(main_files.keys())

            conflict_analysis = {
                'branch_files_changed': len(branch_files),
                'main_files_changed': len(main_files),
                'overlapping_files': len(overlapping),
                'high_risk_overlaps': 0,
                'total_risk_score': 0.0,
                'recommendations': [],
                'detailed_analysis': {}
            }

            # Analyze overlapping files
            for file_path in overlapping:
                branch_changes = branch_files[file_path]
                main_changes = main_files[file_path]

                file_risk = self.assess_file_conflict_risk(file_path, branch_changes, main_changes)

                if file_risk['risk_level'] == 'high_risk':
                    conflict_analysis['high_risk_overlaps'] += 1

                conflict_analysis['total_risk_score'] += file_risk['score']
                conflict_analysis['detailed_analysis'][file_path] = file_risk

            # Generate recommendations
            conflict_analysis['recommendations'] = self.generate_recommendations(conflict_analysis)

            # Overall risk assessment
            conflict_analysis['overall_risk'] = self.assess_overall_risk(conflict_analysis)

            return conflict_analysis

        except Exception as e:
            return {
                'error': str(e),
                'branch_files_changed': 0,
                'main_files_changed': 0,
                'overlapping_files': 0,
                'high_risk_overlaps': 0,
                'total_risk_score': 0.0,
                'recommendations': ['Unable to analyze branch conflict risk'],
                'detailed_analysis': {},
                'overall_risk': 'unknown'
            }

    def get_changed_files(self, ref: str, since_branch: Optional[str] = None) -> Dict[str, List[str]]:
        """Get files changed in a reference with their change types."""
        try:
            cmd = ['git', 'diff', '--name-status', ref]
            if since_branch:
                # Compare since branch point
                merge_base = subprocess.run(
                    ['git', 'merge-base', since_branch, ref],
                    capture_output=True, text=True, check=True
                ).stdout.strip()
                cmd = ['git', 'diff', '--name-status', merge_base, ref]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            files = {}

            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('\t', 1)
                    if len(parts) == 2:
                        status, file_path = parts
                        files[file_path] = status

            return files

        except subprocess.CalledProcessError:
            return {}

    def assess_file_conflict_risk(self, file_path: str, branch_status: str, main_status: str) -> Dict:
        """Assess conflict risk for a specific file."""
        risk_level = 'low_risk'
        score = 1.0

        # Check file against risk patterns
        for pattern_level, patterns in self.conflict_patterns.items():
            for pattern in patterns:
                if re.search(pattern, file_path):
                    risk_level = pattern_level
                    score = self.risk_scores[pattern_level]
                    break
            if risk_level != 'low_risk':
                break

        # Increase score if both branches modified the file
        if branch_status in ['M', 'A'] and main_status in ['M', 'A']:
            score *= 1.5  # Both modified = higher risk

        # Increase score for deletions
        if 'D' in branch_status or 'D' in main_status:
            score *= 2.0  # Deletions are very risky

        return {
            'file_path': file_path,
            'branch_status': branch_status,
            'main_status': main_status,
            'risk_level': risk_level,
            'score': score,
            'recommendation': self.get_file_recommendation(file_path, risk_level)
        }

    def get_file_recommendation(self, file_path: str, risk_level: str) -> str:
        """Get recommendation for handling a risky file."""
        if risk_level == 'high_risk':
            if 'docs/history/state_capsules' in file_path:
                return "Rebase immediately - state capsules are critical for HEE operations"
            elif 'workflows' in file_path:
                return "Coordinate with team - CI/CD changes require synchronization"
            else:
                return "Review changes carefully - high-risk documentation conflict"

        elif risk_level == 'medium_risk':
            return "Test changes thoroughly - scripts and configuration conflicts"

        else:
            return "Monitor during merge - low-risk changes"

    def generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate overall recommendations based on analysis."""
        recommendations = []

        if analysis['high_risk_overlaps'] > 0:
            recommendations.append(f"🚨 URGENT: {analysis['high_risk_overlaps']} high-risk file conflicts detected - rebase immediately")

        if analysis['total_risk_score'] > 10:
            recommendations.append("⚠️ High conflict risk detected - consider rebasing before further development")

        if analysis['overlapping_files'] > 5:
            recommendations.append("📊 Many files overlap - review changes systematically")

        # Specific recommendations
        if analysis['overlapping_files'] == 0:
            recommendations.append("✅ No overlapping changes - low conflict risk")

        if analysis['total_risk_score'] < 3:
            recommendations.append("🟢 Low conflict risk - proceed with development")

        return recommendations

    def assess_overall_risk(self, analysis: Dict) -> str:
        """Assess overall conflict risk level."""
        score = analysis['total_risk_score']
        high_risk_count = analysis['high_risk_overlaps']

        if high_risk_count > 0 or score > 15:
            return 'critical'
        elif score > 10:
            return 'high'
        elif score > 5:
            return 'medium'
        elif score > 0:
            return 'low'
        else:
            return 'none'

    def predict_conflicts(self, branch_name: str) -> Dict:
        """Predict potential conflicts for a branch."""
        analysis = self.analyze_branch_conflict_risk(branch_name)

        prediction = {
            'risk_assessment': analysis['overall_risk'],
            'confidence': self.calculate_confidence(analysis),
            'predicted_conflicts': self.estimate_conflict_count(analysis),
            'time_to_resolve': self.estimate_resolution_time(analysis),
            'recommendations': analysis['recommendations']
        }

        return prediction

    def calculate_confidence(self, analysis: Dict) -> float:
        """Calculate confidence in conflict prediction."""
        base_confidence = 0.8  # Base confidence in analysis

        # Reduce confidence for uncertain factors
        if analysis['branch_files_changed'] == 0:
            base_confidence *= 0.5  # No branch changes to analyze

        if analysis.get('error'):
            base_confidence *= 0.3  # Analysis error

        return base_confidence

    def estimate_conflict_count(self, analysis: Dict) -> int:
        """Estimate number of conflicts that might occur."""
        risk_score = analysis['total_risk_score']

        if risk_score > 20:
            return max(3, int(risk_score / 5))
        elif risk_score > 10:
            return max(1, int(risk_score / 8))
        elif risk_score > 5:
            return 1
        else:
            return 0

    def estimate_resolution_time(self, analysis: Dict) -> str:
        """Estimate time to resolve predicted conflicts."""
        conflict_count = self.estimate_conflict_count(analysis)

        if conflict_count == 0:
            return "0 minutes"
        elif conflict_count == 1:
            return "15-30 minutes"
        elif conflict_count <= 3:
            return "1-2 hours"
        else:
            return "2-4 hours"


def main():
    """Command-line interface for AI conflict detection."""
    import argparse

    parser = argparse.ArgumentParser(description='AI-Assisted Conflict Detection System')
    parser.add_argument('action', choices=['analyze', 'predict'],
                       help='Action to perform')
    parser.add_argument('--branch', default='HEAD',
                       help='Branch to analyze (default: HEAD)')

    args = parser.parse_args()

    detector = AIConflictDetector()

    if args.action == 'analyze':
        print(f"🔍 Analyzing conflict risk for branch: {args.branch}")
        analysis = detector.analyze_branch_conflict_risk(args.branch)

        print(f"\n📊 Conflict Risk Analysis:")
        print(f"   Branch files changed: {analysis['branch_files_changed']}")
        print(f"   Main files changed: {analysis['main_files_changed']}")
        print(f"   Overlapping files: {analysis['overlapping_files']}")
        print(f"   High-risk overlaps: {analysis['high_risk_overlaps']}")
        print(f"   Total risk score: {analysis['total_risk_score']:.1f}")
        print(f"   Overall risk: {analysis['overall_risk']}")

        if analysis['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in analysis['recommendations']:
                print(f"   - {rec}")

        if analysis.get('error'):
            print(f"\n❌ Error: {analysis['error']}")
            return 1

    elif args.action == 'predict':
        print(f"🔮 Predicting conflicts for branch: {args.branch}")
        prediction = detector.predict_conflicts(args.branch)

        print(f"\n🎯 Conflict Prediction:")
        print(f"   Risk Assessment: {prediction['risk_assessment']}")
        print(f"   Confidence: {prediction['confidence']:.1f}")
        print(f"   Predicted Conflicts: {prediction['predicted_conflicts']}")
        print(f"   Est. Resolution Time: {prediction['time_to_resolve']}")

        if prediction['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in prediction['recommendations']:
                print(f"   - {rec}")

    return 0


if __name__ == '__main__':
    exit(main())
