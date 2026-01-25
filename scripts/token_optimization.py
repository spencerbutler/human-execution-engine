#!/usr/bin/env python3
"""
HEE Token Optimization System
Tracks and optimizes token usage for AI-assisted development operations.
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class TokenOptimizer:
    """AI-assisted token optimization system for HEE operations."""

    def __init__(self, log_file: str = "docs/TOKEN_OPTIMIZATION_LOG.json"):
        self.log_file = log_file
        self.usage_history = []
        self.optimization_rules = {
            "rebase_operations": {
                "cost_threshold": 1000,
                "optimization_suggestion": "Use scheduled daily rebases instead of on-demand"
            },
            "conflict_resolution": {
                "cost_threshold": 2000,
                "optimization_suggestion": "Implement preventive conflict detection"
            },
            "documentation_generation": {
                "cost_threshold": 1500,
                "optimization_suggestion": "Use templates and standardize formats"
            }
        }
        self.load_history()

    def load_history(self) -> None:
        """Load token usage history from file."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.usage_history = data.get('history', [])
            except (json.JSONDecodeError, IOError):
                self.usage_history = []

    def save_history(self) -> None:
        """Save token usage history to file."""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, 'w') as f:
            json.dump({
                'last_updated': datetime.now().isoformat(),
                'total_entries': len(self.usage_history),
                'history': self.usage_history[-100:]  # Keep last 100 entries
            }, f, indent=2)

    def log_operation(self, operation_type: str, tokens_used: int,
                     description: str, success: bool = True) -> None:
        """Log a token-consuming operation."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'operation_type': operation_type,
            'tokens_used': tokens_used,
            'description': description,
            'success': success,
            'efficiency_score': self.calculate_efficiency(operation_type, tokens_used)
        }

        self.usage_history.append(entry)
        self.save_history()

    def calculate_efficiency(self, operation_type: str, tokens_used: int) -> float:
        """Calculate efficiency score for operation (lower is better)."""
        base_efficiency = tokens_used

        # Adjust for operation complexity
        complexity_multipliers = {
            'rebase': 0.8,  # Rebases are relatively efficient
            'conflict_resolution': 1.5,  # Conflicts are expensive
            'documentation': 1.0,  # Baseline
            'code_generation': 1.2,  # Code generation is moderately expensive
            'analysis': 0.9  # Analysis is efficient
        }

        multiplier = complexity_multipliers.get(operation_type, 1.0)
        return base_efficiency * multiplier

    def get_optimization_recommendations(self, operation_type: str,
                                       tokens_used: int) -> List[str]:
        """Get optimization recommendations for an operation."""
        recommendations = []

        # Check against thresholds
        rule = self.optimization_rules.get(operation_type)
        if rule and tokens_used > rule['cost_threshold']:
            recommendations.append(rule['optimization_suggestion'])

        # General recommendations based on patterns
        recent_ops = self.get_recent_operations(operation_type, hours=24)
        if len(recent_ops) > 3:
            avg_tokens = sum(op['tokens_used'] for op in recent_ops) / len(recent_ops)
            if tokens_used > avg_tokens * 1.5:
                recommendations.append(f"Token usage is 50% above recent average for {operation_type}")

        # Time-based recommendations
        if operation_type == 'rebase' and tokens_used > 500:
            recommendations.append("Consider implementing automated daily rebase scheduling")

        if operation_type == 'conflict_resolution':
            recommendations.append("Implement conflict prevention through regular rebasing")
            recommendations.append("Use AI-assisted conflict detection before manual resolution")

        return recommendations

    def get_recent_operations(self, operation_type: Optional[str] = None,
                            hours: int = 24) -> List[Dict]:
        """Get operations from the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = []

        for entry in self.usage_history:
            entry_time = datetime.fromisoformat(entry['timestamp'])
            if entry_time > cutoff:
                if operation_type is None or entry['operation_type'] == operation_type:
                    recent.append(entry)

        return recent

    def generate_report(self, days: int = 7) -> Dict:
        """Generate comprehensive token usage report."""
        cutoff = datetime.now() - timedelta(days=days)
        period_usage = [entry for entry in self.usage_history
                       if datetime.fromisoformat(entry['timestamp']) > cutoff]

        total_tokens = sum(entry['tokens_used'] for entry in period_usage)
        operations_by_type = {}

        for entry in period_usage:
            op_type = entry['operation_type']
            if op_type not in operations_by_type:
                operations_by_type[op_type] = []
            operations_by_type[op_type].append(entry)

        # Calculate statistics
        stats = {}
        for op_type, operations in operations_by_type.items():
            tokens = [op['tokens_used'] for op in operations]
            stats[op_type] = {
                'count': len(operations),
                'total_tokens': sum(tokens),
                'avg_tokens': sum(tokens) / len(tokens) if tokens else 0,
                'max_tokens': max(tokens) if tokens else 0
            }

        return {
            'period_days': days,
            'total_operations': len(period_usage),
            'total_tokens': total_tokens,
            'operations_by_type': stats,
            'recommendations': self.analyze_patterns(operations_by_type)
        }

    def analyze_patterns(self, operations_by_type: Dict) -> List[str]:
        """Analyze usage patterns and provide recommendations."""
        recommendations = []

        # Check for high-frequency expensive operations
        for op_type, stats in operations_by_type.items():
            if stats['avg_tokens'] > 2000 and stats['count'] > 5:
                recommendations.append(f"High token usage in {op_type}: {stats['count']} operations averaging {stats['avg_tokens']:.0f} tokens")

        # Check for conflict resolution patterns
        conflict_ops = operations_by_type.get('conflict_resolution', {})
        if conflict_ops.get('count', 0) > 3:
            recommendations.append("Multiple conflict resolutions detected - implement prevention strategies")

        return recommendations


def main():
    """Command-line interface for token optimization."""
    import argparse

    parser = argparse.ArgumentParser(description='HEE Token Optimization System')
    parser.add_argument('action', choices=['log', 'report', 'optimize'],
                       help='Action to perform')
    parser.add_argument('--operation-type', help='Type of operation')
    parser.add_argument('--tokens', type=int, help='Tokens used')
    parser.add_argument('--description', help='Operation description')
    parser.add_argument('--days', type=int, default=7, help='Report period in days')

    args = parser.parse_args()

    optimizer = TokenOptimizer()

    if args.action == 'log':
        if not all([args.operation_type, args.tokens, args.description]):
            print("Error: log action requires --operation-type, --tokens, and --description")
            return 1

        optimizer.log_operation(args.operation_type, args.tokens, args.description)
        recommendations = optimizer.get_optimization_recommendations(args.operation_type, args.tokens)

        print(f"✅ Logged {args.operation_type} operation: {args.tokens} tokens")
        if recommendations:
            print("💡 Optimization suggestions:")
            for rec in recommendations:
                print(f"   - {rec}")

    elif args.action == 'report':
        report = optimizer.generate_report(args.days)
        print(f"📊 Token Usage Report (Last {args.days} days)")
        print(f"   Total Operations: {report['total_operations']}")
        print(f"   Total Tokens: {report['total_tokens']}")

        print("\n📋 Operations by Type:")
        for op_type, stats in report['operations_by_type'].items():
            print(f"   {op_type}: {stats['count']} ops, {stats['total_tokens']} tokens (avg: {stats['avg_tokens']:.0f})")

        if report['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   - {rec}")

    elif args.action == 'optimize':
        print("🔍 Analyzing token usage patterns...")
        report = optimizer.generate_report(30)  # Last 30 days

        if report['total_operations'] > 0:
            print(f"Found {report['total_operations']} operations to analyze")
            print("Top optimization opportunities:")
            for rec in report['recommendations'][:5]:  # Top 5
                print(f"   - {rec}")
        else:
            print("No operation data available for optimization analysis")

    return 0


if __name__ == '__main__':
    exit(main())
