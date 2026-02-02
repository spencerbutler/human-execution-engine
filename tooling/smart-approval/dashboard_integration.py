#!/usr/bin/env python3
"""
Dashboard Integration for Smart Approval Metrics
Surfaces daily metrics and alerts in monitoring dashboard.
"""

import json
from pathlib import Path
from datetime import datetime

class SmartApprovalDashboard:
    """Dashboard integration for smart approval workflow metrics"""

    def __init__(self, metrics_path=None):
        self.metrics_path = Path(metrics_path or "var/smart-approval/metrics.json")

    def get_dashboard_data(self):
        """Get metrics data formatted for dashboard consumption"""
        try:
            if not self.metrics_path.exists():
                return self._get_empty_dashboard_data()

            with open(self.metrics_path, 'r') as f:
                metrics = json.load(f)

            return {
                "smart_approval": {
                    "last_updated": metrics.get("timestamp"),
                    "period_days": metrics.get("period_days"),
                    "total_decisions": metrics.get("total_decisions", 0),
                    "approval_rate": metrics.get("rates", {}).get("approval_rate", 0),
                    "prompt_rate": metrics.get("rates", {}).get("prompt_rate", 0),
                    "override_rate": metrics.get("rates", {}).get("override_rate", 0),
                    "alerts": metrics.get("alerts", []),
                    "top_reasons": self._get_top_reasons(metrics),
                    "status": self._calculate_status(metrics)
                }
            }

        except Exception as e:
            return {
                "smart_approval": {
                    "error": f"Failed to load metrics: {e}",
                    "status": "error"
                }
            }

    def _get_empty_dashboard_data(self):
        """Return empty dashboard data for new deployments"""
        return {
            "smart_approval": {
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "period_days": 0,
                "total_decisions": 0,
                "approval_rate": 0,
                "prompt_rate": 0,
                "override_rate": 0,
                "alerts": [],
                "top_reasons": [],
                "status": "initializing"
            }
        }

    def _get_top_reasons(self, metrics):
        """Extract top decision reasons for dashboard"""
        reasons = metrics.get("reasons_breakdown", {})
        sorted_reasons = sorted(reasons.items(), key=lambda x: x[1], reverse=True)

        return [
            {
                "reason": reason,
                "count": count,
                "percentage": round(count / metrics.get("total_decisions", 1) * 100, 1)
            }
            for reason, count in sorted_reasons[:5]
        ]

    def _calculate_status(self, metrics):
        """Calculate overall system status"""
        alerts = metrics.get("alerts", [])

        if any(alert["level"] == "error" for alert in alerts):
            return "error"
        elif any(alert["level"] == "warning" for alert in alerts):
            return "warning"
        elif metrics.get("total_decisions", 0) == 0:
            return "initializing"
        else:
            return "healthy"

    def generate_dashboard_html(self):
        """Generate HTML snippet for dashboard integration"""
        data = self.get_dashboard_data()
        sa_data = data.get("smart_approval", {})

        html = f"""
        <div class="smart-approval-dashboard">
            <h3>Smart Approval Workflow</h3>
            <div class="status-bar">
                <span class="status {sa_data.get('status', 'unknown')}">
                    Status: {sa_data.get('status', 'unknown').title()}
                </span>
                <span class="last-updated">
                    Updated: {sa_data.get('last_updated', 'Never')}
                </span>
            </div>

            <div class="metrics-grid">
                <div class="metric">
                    <div class="value">{sa_data.get('total_decisions', 0)}</div>
                    <div class="label">Total Decisions</div>
                </div>
                <div class="metric">
                    <div class="value">{sa_data.get('approval_rate', 0):.1%}</div>
                    <div class="label">Auto-Approved</div>
                </div>
                <div class="metric">
                    <div class="value">{sa_data.get('prompt_rate', 0):.1%}</div>
                    <div class="label">Manual Prompts</div>
                </div>
                <div class="metric">
                    <div class="value">{sa_data.get('override_rate', 0):.1%}</div>
                    <div class="label">Overrides Used</div>
                </div>
            </div>

            <div class="alerts">
                {"".join(f'<div class="alert {alert["level"]}">{alert["message"]}</div>' for alert in sa_data.get('alerts', []))}
            </div>
        </div>
        """

        return html

def main():
    """CLI interface for dashboard data"""
    dashboard = SmartApprovalDashboard()
    data = dashboard.get_dashboard_data()

    print("Smart Approval Dashboard Data:")
    print(json.dumps(data, indent=2))

    print("\nHTML Snippet:")
    print(dashboard.generate_dashboard_html())

if __name__ == "__main__":
    main()
