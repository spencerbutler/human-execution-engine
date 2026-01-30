#!/usr/bin/env python3
"""
HEE Branch Health Monitor
Real-time monitoring and health scoring for Git branches in HEE development.
"""

import json
import os
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict


@dataclass
class BranchMetrics:
    """Metrics for branch health assessment."""
    branch_name: str
    last_commit_days: int
    commits_behind_main: int
    conflicts_with_main: bool
    has_open_pr: bool
    pr_age_days: Optional[int]
    health_score: float
    risk_level: str
    recommendations: List[str]
    last_updated: str


@dataclass
class HealthThresholds:
    """Configurable health thresholds."""
    max_age_days: int = 7
    max_commits_behind: int = 10
    critical_score: float = 30.0
    warning_score: float = 60.0
    excellent_score: float = 90.0


class BranchHealthMonitor:
    """Monitor and score branch health in real-time with performance optimization."""

    def __init__(self, repo_path: str = ".", config_file: str = "docs/BRANCH_HEALTH_CONFIG.json"):
        self.repo_path = repo_path
        self.config_file = config_file
        self.thresholds = HealthThresholds()
        self.metrics_history: List[BranchMetrics] = []

        # Performance optimization caches
        self._branch_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_seconds = 30  # Cache for 30 seconds

        self.load_config()

    def load_config(self) -> None:
        """Load health monitoring configuration."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.thresholds = HealthThresholds(**config.get('thresholds', {}))
            except (json.JSONDecodeError, IOError):
                pass  # Use defaults

    def save_config(self) -> None:
        """Save current configuration."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump({
                'thresholds': asdict(self.thresholds),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)

    def _is_cache_valid(self) -> bool:
        """Check if the current cache is still valid."""
        if self._cache_timestamp is None:
            return False
        return (datetime.now() - self._cache_timestamp).seconds < self._cache_ttl_seconds

    def _invalidate_cache(self) -> None:
        """Invalidate the current cache."""
        self._branch_cache = {}
        self._cache_timestamp = None

    def _get_cached_or_compute(self, cache_key: str, compute_func, *args, **kwargs):
        """Get value from cache or compute and cache it."""
        if not self._is_cache_valid():
            self._invalidate_cache()

        if cache_key not in self._branch_cache:
            self._branch_cache[cache_key] = compute_func(*args, **kwargs)
            self._cache_timestamp = datetime.now()

        return self._branch_cache[cache_key]

    def get_all_branches(self) -> List[str]:
        """Get all local branches except main/master with caching."""
        return self._get_cached_or_compute('all_branches', self._get_all_branches_uncached)

    def _get_all_branches_uncached(self) -> List[str]:
        """Get all local branches except main/master (uncached implementation)."""
        try:
            result = subprocess.run(
                ['git', 'branch', '--format=%(refname:short)'],
                cwd=self.repo_path,
                capture_output=True, text=True, check=True
            )
            branches = [b.strip() for b in result.stdout.split('\n') if b.strip()]
            return [b for b in branches if b not in ['main', 'master']]
        except subprocess.CalledProcessError:
            return []

    def get_branch_last_commit(self, branch: str) -> Optional[datetime]:
        """Get last commit date for a branch."""
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%ci', branch],
                cwd=self.repo_path,
                capture_output=True, text=True, check=True
            )
            date_str = result.stdout.strip()
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z').replace(tzinfo=None)
        except (subprocess.CalledProcessError, ValueError):
            return None

    def get_commits_behind_main(self, branch: str) -> int:
        """Get number of commits branch is behind main."""
        try:
            result = subprocess.run(
                ['git', 'rev-list', '--count', f'origin/main..{branch}'],
                cwd=self.repo_path,
                capture_output=True, text=True
            )
            return int(result.stdout.strip()) if result.returncode == 0 else 0
        except (subprocess.CalledProcessError, ValueError):
            return 0

    def check_conflicts_with_main(self, branch: str) -> bool:
        """Check if branch has conflicts with main."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--quiet', f'origin/main...{branch}'],
                cwd=self.repo_path,
                capture_output=True
            )
            return result.returncode != 0  # Non-zero means conflicts
        except subprocess.CalledProcessError:
            return True  # Assume conflicts on error

    def check_open_pr(self, branch: str) -> Tuple[bool, Optional[int]]:
        """Check if branch has an open PR and its age."""
        try:
            result = subprocess.run(
                ['gh', 'pr', 'list', '--head', branch, '--state', 'open', '--json', 'createdAt'],
                cwd=self.repo_path,
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                pr_data = json.loads(result.stdout)
                if pr_data:
                    created_at = datetime.fromisoformat(pr_data[0]['createdAt'].replace('Z', '+00:00'))
                    age_days = (datetime.now() - created_at.replace(tzinfo=None)).days
                    return True, age_days
            return False, None
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return False, None

    def calculate_health_score(self, metrics: BranchMetrics) -> float:
        """Calculate overall health score for a branch."""
        score = 100.0

        # Age penalty
        if metrics.last_commit_days > self.thresholds.max_age_days:
            age_penalty = min(50, (metrics.last_commit_days - self.thresholds.max_age_days) * 5)
            score -= age_penalty

        # Commits behind penalty
        if metrics.commits_behind_main > self.thresholds.max_commits_behind:
            behind_penalty = min(30, metrics.commits_behind_main - self.thresholds.max_commits_behind)
            score -= behind_penalty

        # Conflict penalty
        if metrics.conflicts_with_main:
            score -= 40

        # No PR penalty
        if not metrics.has_open_pr:
            score -= 20

        # Old PR penalty
        if metrics.pr_age_days and metrics.pr_age_days > 14:
            pr_penalty = min(20, (metrics.pr_age_days - 14) * 2)
            score -= pr_penalty

        return max(0, score)

    def assess_risk_level(self, score: float) -> str:
        """Assess risk level based on health score."""
        if score < self.thresholds.critical_score:
            return "critical"
        elif score < self.thresholds.warning_score:
            return "warning"
        elif score >= self.thresholds.excellent_score:
            return "excellent"
        else:
            return "good"

    def generate_recommendations(self, metrics: BranchMetrics) -> List[str]:
        """Generate actionable recommendations for branch health."""
        recommendations = []

        if metrics.last_commit_days > self.thresholds.max_age_days:
            recommendations.append(f"Branch hasn't been updated in {metrics.last_commit_days} days - consider rebasing or closing if inactive")

        if metrics.commits_behind_main > self.thresholds.max_commits_behind:
            recommendations.append(f"Branch is {metrics.commits_behind_main} commits behind main - rebase to stay current")

        if metrics.conflicts_with_main:
            recommendations.append("Branch has conflicts with main - rebase immediately to resolve")

        if not metrics.has_open_pr:
            recommendations.append("No open PR found - create PR for review or close branch if work is complete")

        if metrics.pr_age_days and metrics.pr_age_days > 14:
            recommendations.append(f"PR is {metrics.pr_age_days} days old - review and merge or update with progress")

        if metrics.health_score < self.thresholds.warning_score:
            recommendations.append("Urgent attention needed - branch health is poor")

        return recommendations

    def monitor_branch(self, branch_name: str) -> BranchMetrics:
        """Monitor a single branch and return metrics."""
        last_commit = self.get_branch_last_commit(branch_name)
        last_commit_days = (datetime.now() - last_commit).days if last_commit else 999

        commits_behind = self.get_commits_behind_main(branch_name)
        has_conflicts = self.check_conflicts_with_main(branch_name)
        has_pr, pr_age = self.check_open_pr(branch_name)

        metrics = BranchMetrics(
            branch_name=branch_name,
            last_commit_days=last_commit_days,
            commits_behind_main=commits_behind,
            conflicts_with_main=has_conflicts,
            has_open_pr=has_pr,
            pr_age_days=pr_age,
            health_score=0,  # Will be calculated
            risk_level="",   # Will be assessed
            recommendations=[],  # Will be generated
            last_updated=datetime.now().isoformat()
        )

        metrics.health_score = self.calculate_health_score(metrics)
        metrics.risk_level = self.assess_risk_level(metrics.health_score)
        metrics.recommendations = self.generate_recommendations(metrics)

        return metrics

    def monitor_all_branches(self) -> List[BranchMetrics]:
        """Monitor all active branches."""
        branches = self.get_all_branches()
        metrics = []

        for branch in branches:
            try:
                branch_metrics = self.monitor_branch(branch)
                metrics.append(branch_metrics)
                self.metrics_history.append(branch_metrics)
            except Exception as e:
                print(f"Error monitoring branch {branch}: {e}")

        # Keep only last 1000 entries
        self.metrics_history = self.metrics_history[-1000:]

        return metrics

    def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        metrics = self.monitor_all_branches()

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_branches': len(metrics),
            'health_summary': {
                'critical': len([m for m in metrics if m.risk_level == 'critical']),
                'warning': len([m for m in metrics if m.risk_level == 'warning']),
                'good': len([m for m in metrics if m.risk_level == 'good']),
                'excellent': len([m for m in metrics if m.risk_level == 'excellent'])
            },
            'average_health_score': sum(m.health_score for m in metrics) / len(metrics) if metrics else 0,
            'branches': [asdict(m) for m in metrics],
            'recommendations': self.generate_global_recommendations(metrics)
        }

        return report

    def generate_global_recommendations(self, metrics: List[BranchMetrics]) -> List[str]:
        """Generate global recommendations across all branches."""
        recommendations = []

        critical_count = len([m for m in metrics if m.risk_level == 'critical'])
        if critical_count > 0:
            recommendations.append(f"🚨 {critical_count} branches are in critical health - immediate action required")

        stale_branches = len([m for m in metrics if m.last_commit_days > 30])
        if stale_branches > 0:
            recommendations.append(f"📅 {stale_branches} branches haven't been updated in 30+ days - consider cleanup")

        conflict_branches = len([m for m in metrics if m.conflicts_with_main])
        if conflict_branches > 0:
            recommendations.append(f"⚠️ {conflict_branches} branches have conflicts with main - rebase needed")

        no_pr_branches = len([m for m in metrics if not m.has_open_pr])
        if no_pr_branches > 0:
            recommendations.append(f"📝 {no_pr_branches} branches have no open PR - create PRs or close branches")

        return recommendations

    def save_report(self, report: Dict[str, Any], filename: str = "docs/BRANCH_HEALTH_REPORT.json") -> None:
        """Save health report to file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)


def main():
    """Command-line interface for branch health monitoring."""
    import argparse

    parser = argparse.ArgumentParser(description='HEE Branch Health Monitor')
    parser.add_argument('--branch', help='Monitor specific branch')
    parser.add_argument('--report', action='store_true', help='Generate full health report')
    parser.add_argument('--save', action='store_true', help='Save report to file')
    parser.add_argument('--watch', type=int, help='Monitor continuously (seconds interval)')

    args = parser.parse_args()

    monitor = BranchHealthMonitor()

    if args.branch:
        metrics = monitor.monitor_branch(args.branch)
        print(f"Branch Health Report for: {args.branch}")
        print(f"Health Score: {metrics.health_score:.1f}/100 ({metrics.risk_level})")
        print(f"Last Commit: {metrics.last_commit_days} days ago")
        print(f"Commits Behind: {metrics.commits_behind_main}")
        print(f"Conflicts: {'Yes' if metrics.conflicts_with_main else 'No'}")
        print(f"Open PR: {'Yes' if metrics.has_open_pr else 'No'}")
        if metrics.pr_age_days:
            print(f"PR Age: {metrics.pr_age_days} days")

        if metrics.recommendations:
            print("\nRecommendations:")
            for rec in metrics.recommendations:
                print(f"  - {rec}")

    elif args.watch:
        print(f"Monitoring branches every {args.watch} seconds... (Ctrl+C to stop)")
        try:
            while True:
                report = monitor.get_health_report()
                critical = report['health_summary']['critical']
                warning = report['health_summary']['warning']

                status = "✅" if critical == 0 and warning == 0 else "⚠️" if warning > 0 else "🚨"
                print(f"{status} {datetime.now().strftime('%H:%M:%S')} - {report['total_branches']} branches, "
                      f"Avg Score: {report['average_health_score']:.1f}, "
                      f"Critical: {critical}, Warning: {warning}")

                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")

    else:
        report = monitor.get_health_report()

        print("🏥 HEE Branch Health Report")
        print("=" * 40)
        print(f"Total Branches: {report['total_branches']}")
        print(f"Average Health Score: {report['average_health_score']:.1f}/100")

        health = report['health_summary']
        print(f"Health Distribution: Excellent: {health['excellent']}, Good: {health['good']}, "
              f"Warning: {health['warning']}, Critical: {health['critical']}")

        if report['recommendations']:
            print("\n📋 Global Recommendations:")
            for rec in report['recommendations']:
                print(f"  {rec}")

        print(f"\n📊 Branch Details:")
        for branch_data in report['branches']:
            status = "✅" if branch_data['risk_level'] in ['excellent', 'good'] else "⚠️" if branch_data['risk_level'] == 'warning' else "🚨"
            print(f"  {status} {branch_data['branch_name']}: {branch_data['health_score']:.1f} ({branch_data['risk_level']})")

        if args.save:
            monitor.save_report(report)
            print(f"\n💾 Report saved to: docs/BRANCH_HEALTH_REPORT.json")


if __name__ == '__main__':
    main()
