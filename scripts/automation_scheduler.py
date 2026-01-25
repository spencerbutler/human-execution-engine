#!/usr/bin/env python3
"""
HEE Automation Scheduler
Automated maintenance and monitoring tasks for continuous workflow optimization.
"""

import json
import os
import time
import schedule
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
import threading
import signal
import sys


class AutomationScheduler:
    """Scheduler for automated HEE maintenance and monitoring tasks."""

    def __init__(self, config_file: str = "docs/AUTOMATION_CONFIG.json"):
        self.config_file = config_file
        self.running = False
        self.jobs = []
        self.load_config()

        # Initialize monitoring components
        self.health_monitor = None
        self.predictive_analytics = None
        self._load_components()

    def load_config(self) -> None:
        """Load automation configuration."""
        default_config = {
            'health_monitoring': {
                'enabled': True,
                'interval_minutes': 30,
                'alert_thresholds': {
                    'critical_branches': 2,
                    'warning_branches': 5,
                    'health_score_drop': 10.0
                }
            },
            'predictive_analytics': {
                'enabled': True,
                'interval_hours': 6,
                'trend_analysis_days': 7
            },
            'maintenance_tasks': {
                'enabled': True,
                'stale_branch_cleanup_days': 90,
                'health_report_generation': 'daily'
            },
            'notifications': {
                'enabled': True,
                'email_enabled': False,
                'slack_webhook': None,
                'alert_levels': ['critical', 'warning']
            }
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config = {**default_config, **loaded_config}
            except (json.JSONDecodeError, IOError):
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()

    def save_config(self) -> None:
        """Save current configuration."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _load_components(self) -> None:
        """Load monitoring components dynamically."""
        try:
            # Import here to avoid circular dependencies
            from scripts.branch_health_monitor import BranchHealthMonitor
            from scripts.predictive_analytics import PredictiveAnalytics

            self.health_monitor = BranchHealthMonitor()
            self.predictive_analytics = PredictiveAnalytics()
        except ImportError as e:
            print(f"Warning: Could not load monitoring components: {e}")

    def schedule_health_monitoring(self) -> None:
        """Schedule regular health monitoring."""
        if not self.config['health_monitoring']['enabled'] or not self.health_monitor:
            return

        interval = self.config['health_monitoring']['interval_minutes']

        def health_check_job():
            try:
                report = self.health_monitor.get_health_report()
                self._process_health_alerts(report)

                # Store trend data
                today = datetime.now().date().isoformat()
                health_summary = report['health_summary']
                self.predictive_analytics.store_health_trend(
                    today,
                    report['total_branches'],
                    report['average_health_score'],
                    health_summary['critical'],
                    health_summary['warning'],
                    0  # TODO: Track actual conflicts
                )

                print(f"✅ Health monitoring completed at {datetime.now()}")
            except Exception as e:
                print(f"❌ Health monitoring failed: {e}")

        schedule.every(interval).minutes.do(health_check_job)
        self.jobs.append(('health_monitoring', health_check_job))

    def schedule_predictive_analytics(self) -> None:
        """Schedule predictive analytics updates."""
        if not self.config['predictive_analytics']['enabled'] or not self.predictive_analytics:
            return

        interval = self.config['predictive_analytics']['interval_hours']

        def analytics_job():
            try:
                # Generate predictions for all branches
                branches = self.health_monitor.get_all_branches()
                for branch_name in branches:
                    metrics = self.health_monitor.monitor_branch(branch_name)
                    prediction = self.predictive_analytics.predict_branch_conflicts(
                        branch_name,
                        metrics.health_score,
                        metrics.last_commit_days,
                        metrics.commits_behind_main,
                        metrics.has_open_pr
                    )
                    self.predictive_analytics.store_prediction(prediction)

                print(f"✅ Predictive analytics updated at {datetime.now()}")
            except Exception as e:
                print(f"❌ Predictive analytics failed: {e}")

        schedule.every(interval).hours.do(analytics_job)
        self.jobs.append(('predictive_analytics', analytics_job))

    def schedule_maintenance_tasks(self) -> None:
        """Schedule automated maintenance tasks."""
        if not self.config['maintenance_tasks']['enabled']:
            return

        # Daily health report generation
        if self.config['maintenance_tasks']['health_report_generation'] == 'daily':
            def daily_report_job():
                try:
                    report = self.health_monitor.get_health_report()
                    report_file = f"docs/health_reports/daily_{datetime.now().date().isoformat()}.json"
                    os.makedirs(os.path.dirname(report_file), exist_ok=True)
                    with open(report_file, 'w') as f:
                        json.dump(report, f, indent=2)
                    print(f"✅ Daily health report generated: {report_file}")
                except Exception as e:
                    print(f"❌ Daily report generation failed: {e}")

            schedule.every().day.at("06:00").do(daily_report_job)
            self.jobs.append(('daily_reports', daily_report_job))

        # Stale branch cleanup
        cleanup_days = self.config['maintenance_tasks']['stale_branch_cleanup_days']
        if cleanup_days > 0:
            def cleanup_job():
                try:
                    branches = self.health_monitor.get_all_branches()
                    cutoff_date = datetime.now() - timedelta(days=cleanup_days)
                    stale_branches = []

                    for branch in branches:
                        metrics = self.health_monitor.monitor_branch(branch)
                        if metrics.last_commit_days > cleanup_days:
                            stale_branches.append(branch)

                    if stale_branches:
                        print(f"⚠️ Found {len(stale_branches)} stale branches older than {cleanup_days} days:")
                        for branch in stale_branches:
                            print(f"  - {branch}")
                        print("Manual cleanup recommended (automated deletion disabled for safety)")
                    else:
                        print("✅ No stale branches found")

                except Exception as e:
                    print(f"❌ Stale branch cleanup check failed: {e}")

            schedule.every(7).days.do(cleanup_job)  # Weekly check
            self.jobs.append(('stale_cleanup', cleanup_job))

    def _process_health_alerts(self, report: Dict[str, Any]) -> None:
        """Process health monitoring alerts."""
        if not self.config['notifications']['enabled']:
            return

        alerts = []
        health_summary = report['health_summary']
        thresholds = self.config['health_monitoring']['alert_thresholds']

        # Check critical branches
        if health_summary['critical'] >= thresholds['critical_branches']:
            alerts.append({
                'level': 'critical',
                'message': f"{health_summary['critical']} branches in critical health",
                'details': f"Threshold: {thresholds['critical_branches']} critical branches"
            })

        # Check warning branches
        if health_summary['warning'] >= thresholds['warning_branches']:
            alerts.append({
                'level': 'warning',
                'message': f"{health_summary['warning']} branches in warning health",
                'details': f"Threshold: {thresholds['warning_branches']} warning branches"
            })

        # Check health score drops (would need historical comparison)
        if report['average_health_score'] < 50.0:  # Simple threshold for now
            alerts.append({
                'level': 'warning',
                'message': f"Low average health score: {report['average_health_score']:.1f}/100",
                'details': "Average branch health below acceptable threshold"
            })

        # Send notifications
        for alert in alerts:
            if alert['level'] in self.config['notifications']['alert_levels']:
                self._send_notification(alert)

    def _send_notification(self, alert: Dict[str, Any]) -> None:
        """Send notification for alert."""
        message = f"🚨 HEE Alert ({alert['level'].upper()}): {alert['message']}"

        print(message)  # Console output

        # TODO: Implement actual notification methods
        # - Email notifications
        # - Slack webhooks
        # - SMS alerts
        # - Internal dashboard alerts

    def start_scheduler(self) -> None:
        """Start the automation scheduler."""
        print("🤖 HEE Automation Scheduler Starting...")
        print("=" * 50)

        # Schedule all jobs
        self.schedule_health_monitoring()
        self.schedule_predictive_analytics()
        self.schedule_maintenance_tasks()

        print(f"📅 Scheduled {len(self.jobs)} automation tasks:")
        for job_name, job_func in self.jobs:
            print(f"  ✅ {job_name}")

        self.running = True

        # Handle graceful shutdown
        def signal_handler(signum, frame):
            print("\n🛑 Received shutdown signal, stopping scheduler...")
            self.stop_scheduler()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        print("🚀 Scheduler running... (Press Ctrl+C to stop)")
        print()

        # Run initial jobs
        self._run_initial_jobs()

        # Main scheduling loop
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def _run_initial_jobs(self) -> None:
        """Run initial job executions."""
        print("🔄 Running initial job executions...")

        # Run health check immediately
        if self.health_monitor:
            try:
                report = self.health_monitor.get_health_report()
                print("✅ Initial health check completed")
                self._process_health_alerts(report)
            except Exception as e:
                print(f"❌ Initial health check failed: {e}")

        # Run analytics update
        if self.predictive_analytics:
            try:
                # Generate predictions for current branches
                branches = self.health_monitor.get_all_branches()
                predictions_count = 0
                for branch_name in branches:
                    metrics = self.health_monitor.monitor_branch(branch_name)
                    prediction = self.predictive_analytics.predict_branch_conflicts(
                        branch_name,
                        metrics.health_score,
                        metrics.last_commit_days,
                        metrics.commits_behind_main,
                        metrics.has_open_pr
                    )
                    self.predictive_analytics.store_prediction(prediction)
                    predictions_count += 1

                print(f"✅ Initial analytics updated ({predictions_count} predictions)")
            except Exception as e:
                print(f"❌ Initial analytics update failed: {e}")

        print()

    def stop_scheduler(self) -> None:
        """Stop the automation scheduler."""
        print("🛑 Stopping HEE Automation Scheduler...")
        self.running = False
        schedule.clear()
        print("✅ Scheduler stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        return {
            'running': self.running,
            'jobs_scheduled': len(self.jobs),
            'next_run_times': {
                job_name: "N/A" for job_name, _ in self.jobs  # TODO: Get actual next run times
            },
            'config': self.config,
            'last_health_check': datetime.now().isoformat()  # TODO: Track actual times
        }


def main():
    """Command-line interface for automation scheduler."""
    import argparse

    parser = argparse.ArgumentParser(description='HEE Automation Scheduler')
    parser.add_argument('--start', action='store_true', help='Start the automation scheduler')
    parser.add_argument('--status', action='store_true', help='Show scheduler status')
    parser.add_argument('--stop', action='store_true', help='Stop the automation scheduler')
    parser.add_argument('--run-once', action='store_true', help='Run all jobs once and exit')

    args = parser.parse_args()

    scheduler = AutomationScheduler()

    if args.start:
        scheduler.start_scheduler()
    elif args.status:
        status = scheduler.get_status()
        print("📊 HEE Automation Scheduler Status")
        print("=" * 40)
        print(f"Running: {'Yes' if status['running'] else 'No'}")
        print(f"Jobs Scheduled: {status['jobs_scheduled']}")
        print(f"Health Monitoring: {'Enabled' if status['config']['health_monitoring']['enabled'] else 'Disabled'}")
        print(f"Predictive Analytics: {'Enabled' if status['config']['predictive_analytics']['enabled'] else 'Disabled'}")
        print(f"Maintenance Tasks: {'Enabled' if status['config']['maintenance_tasks']['enabled'] else 'Disabled'}")
        print(f"Notifications: {'Enabled' if status['config']['notifications']['enabled'] else 'Disabled'}")
    elif args.run_once:
        print("🔄 Running all automation jobs once...")
        scheduler._run_initial_jobs()
        print("✅ All jobs completed")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
