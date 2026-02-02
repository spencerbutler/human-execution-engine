#!/usr/bin/env python3
"""
Metrics Collector for Smart Approval Workflow
Logs prompt_rate, override_rate, deny_rate, false_positive_reports.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

class ApprovalMetricsCollector:
    """Collects and reports metrics on smart approval workflow performance"""

    def __init__(self, transcript_path=None, metrics_path=None):
        self.transcript_path = Path(transcript_path or "var/smart-approval/transcript.jsonl")
        self.metrics_path = Path(metrics_path or "var/smart-approval/metrics.json")
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)

    def collect_daily_metrics(self, days_back=1):
        """Collect metrics for the last N days"""
        since = datetime.utcnow() - timedelta(days=days_back)

        decisions = []
        if self.transcript_path.exists():
            with open(self.transcript_path, 'r') as f:
                for line in f:
                    if line.strip():
                        decision = json.loads(line)
                        decision_time = datetime.fromisoformat(decision["decision_details"]["timestamp"].replace('Z', '+00:00'))
                        if decision_time >= since:
                            decisions.append(decision)

        if not decisions:
            return {"error": "No decisions found in time range"}

        # Calculate metrics
        total_decisions = len(decisions)
        auto_approved = sum(1 for d in decisions if not d.get("requires_approval", True))
        required_approval = total_decisions - auto_approved
        overrides_applied = sum(1 for d in decisions if d.get("override_applied", False))

        # Breakdown by reason
        reasons = defaultdict(int)
        for d in decisions:
            reasons[d.get("reason", "unknown")] += 1

        # Calculate rates
        prompt_rate = required_approval / total_decisions if total_decisions > 0 else 0
        override_rate = overrides_applied / total_decisions if total_decisions > 0 else 0
        approval_rate = auto_approved / total_decisions if total_decisions > 0 else 0

        metrics = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "period_days": days_back,
            "total_decisions": total_decisions,
            "auto_approved": auto_approved,
            "required_approval": required_approval,
            "overrides_applied": overrides_applied,
            "rates": {
                "approval_rate": round(approval_rate, 3),
                "prompt_rate": round(prompt_rate, 3),
                "override_rate": round(override_rate, 3)
            },
            "reasons_breakdown": dict(reasons),
            "alerts": []
        }

        # Generate alerts
        if prompt_rate > 0.8:
            metrics["alerts"].append({
                "level": "warning",
                "message": f"High prompt rate: {prompt_rate:.1%} of commands require approval",
                "threshold": 0.8
            })

        if override_rate > 0.1:
            metrics["alerts"].append({
                "level": "info",
                "message": f"Override usage: {override_rate:.1%} of decisions use overrides",
                "threshold": 0.1
            })

        # Save metrics
        with open(self.metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)

        return metrics

    def get_summary_report(self):
        """Generate human-readable summary report"""
        try:
            with open(self.metrics_path, 'r') as f:
                metrics = json.load(f)

            report = f"""
Smart Approval Metrics Report
=============================

Period: Last {metrics.get('period_days', 'N/A')} days
Total Decisions: {metrics.get('total_decisions', 0)}

Approval Rates:
- Auto-approved: {metrics.get('rates', {}).get('approval_rate', 0):.1%}
- Required prompts: {metrics.get('rates', {}).get('prompt_rate', 0):.1%}
- Override usage: {metrics.get('rates', {}).get('override_rate', 0):.1%}

Top Decision Reasons:
"""

            reasons = metrics.get('reasons_breakdown', {})
            sorted_reasons = sorted(reasons.items(), key=lambda x: x[1], reverse=True)

            for reason, count in sorted_reasons[:5]:
                percentage = count / metrics.get('total_decisions', 1) * 100
                report += f"- {reason}: {count} ({percentage:.1%})\n"

            alerts = metrics.get('alerts', [])
            if alerts:
                report += "\nAlerts:\n"
                for alert in alerts:
                    report += f"- {alert['level'].upper()}: {alert['message']}\n"
            else:
                report += "\nNo alerts triggered.\n"

            return report

        except FileNotFoundError:
            return "No metrics file found. Run collect_daily_metrics() first."
        except Exception as e:
            return f"Error generating report: {e}"

def main():
    collector = ApprovalMetricsCollector()
    metrics = collector.collect_daily_metrics(days_back=1)

    print("Daily Metrics Collected:")
    print(json.dumps(metrics, indent=2))

    print("\nSummary Report:")
    print(collector.get_summary_report())

if __name__ == "__main__":
    main()
