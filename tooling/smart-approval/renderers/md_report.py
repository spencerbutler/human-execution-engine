"""Markdown report renderer for metrics data."""

import json
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from ..lib.render.base import MetricsRenderer, RendererConfig, renderer_registry


class MarkdownReportRenderer(MetricsRenderer):
    """Renderer that generates markdown reports."""

    def __init__(self, config: RendererConfig):
        super().__init__(config)

    def get_supported_views(self) -> List[str]:
        """Return supported view names."""
        return ['overview', 'decisions', 'replay_health']

    def get_output_format(self) -> str:
        """Return output format."""
        return 'md'

    def render_overview_view(self, metrics_data: Dict[str, Any]) -> str:
        """Render overview as markdown report."""
        self.ensure_output_directory()

        metrics = metrics_data.get('metrics', {})
        build_info = self.get_build_info()

        # Generate markdown content
        content = f"""# Smart Approval Dashboard - Overview Report

**Generated:** {build_info['build_timestamp']}
**Commit:** `{build_info['git_commit'][:8]}`

## Key Performance Indicators

| Metric | Value | Unit | Description |
|--------|-------|------|-------------|
| Prompt Rate | {metrics.get('prompt_rate', 0):.1f} | per minute | Rate of prompts processed per minute |
| Override Rate | {metrics.get('override_rate', 0):.1f} | per minute | Rate of human overrides per minute |
| Deny Rate | {metrics.get('deny_rate', 0):.1f} | per minute | Rate of denied requests per minute |
| Safety Incidents | {metrics.get('safety_incidents', 0)} | count | Number of safety incidents recorded |
| Phase Day | {metrics.get('phase_day', 1)} | day | Current phase day |

## Trends Analysis

### Rate Trends (Last Hour)
"""

        # Add timeseries data
        timeseries_data = metrics.get('timeseries_data', {}).get('hourly', [])
        if timeseries_data:
            content += "\n| Timestamp | Prompt Rate | Override Rate | Deny Rate |\n"
            content += "|-----------|-------------|---------------|-----------|\n"

            for point in timeseries_data[-10:]:  # Last 10 data points
                timestamp = point['timestamp'][:19]  # Format timestamp
                content += f"| {timestamp} | {point['prompt_rate']:.1f} | {point['override_rate']:.1f} | {point['deny_rate']:.1f} |\n"

        content += "\n## Safety Summary\n\n"
        safety_aggregates = metrics.get('aggregates', {}).get('safety', {})
        if safety_aggregates.get('incident_types'):
            content += "### Incident Types\n\n"
            for incident_type, count in safety_aggregates['incident_types'].items():
                content += f"- **{incident_type}:** {count} incidents\n"

        # Write to file
        output_file = self.config.output_path / "overview.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_file)

    def render_decisions_view(self, metrics_data: Dict[str, Any]) -> str:
        """Render decisions analysis as markdown report."""
        self.ensure_output_directory()

        metrics = metrics_data.get('metrics', {})
        build_info = self.get_build_info()

        # Generate markdown content
        content = f"""# Smart Approval Dashboard - Decisions Report

**Generated:** {build_info['build_timestamp']}
**Commit:** `{build_info['git_commit'][:8]}`

## Decision Summary

"""

        decision_aggregates = metrics.get('aggregates', {}).get('decisions', {})

        if decision_aggregates.get('decision_breakdown'):
            content += "### Decision Breakdown\n\n"
            for decision_type, count in decision_aggregates['decision_breakdown'].items():
                content += f"- **{decision_type.title()}:** {count} decisions\n"

        if decision_aggregates.get('avg_confidence'):
            content += f"\n**Average Confidence:** {decision_aggregates['avg_confidence']:.2%}\n\n"

        # Deny reasons
        deny_reasons = metrics.get('deny_reasons', {})
        if deny_reasons:
            content += "## Deny Reasons Analysis\n\n"
            content += "| Reason | Count | Percentage |\n"
            content += "|--------|-------|------------|\n"

            total_denies = sum(deny_reasons.values())
            for reason, count in sorted(deny_reasons.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_denies * 100) if total_denies > 0 else 0
                content += f"| {reason} | {count} | {percentage:.1f}% |\n"

        # Recent decisions
        recent_decisions = metrics.get('recent_decisions', [])
        if recent_decisions:
            content += "\n## Recent Decisions\n\n"
            content += "| Timestamp | Decision | Reason | Confidence |\n"
            content += "|-----------|----------|--------|------------|\n"

            for decision in recent_decisions[:20]:  # Last 20 decisions
                timestamp = decision.get('timestamp', '')[:19]
                decision_type = decision.get('decision', 'unknown').title()
                reason = decision.get('reason', 'N/A')
                confidence = f"{decision.get('confidence', 0):.2f}" if decision.get('confidence') else 'N/A'
                content += f"| {timestamp} | {decision_type} | {reason} | {confidence} |\n"

        # Write to file
        output_file = self.config.output_path / "decisions.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_file)

    def render_replay_health_view(self, metrics_data: Dict[str, Any]) -> str:
        """Render replay health status as markdown report."""
        self.ensure_output_directory()

        build_info = self.get_build_info()

        # Mock replay health data
        replay_status = {
            'pass_rate': 0.95,
            'total_tests': 1000,
            'passed_tests': 950,
            'failed_tests': 50,
            'recent_failures': [
                {
                    'timestamp': '2026-01-28T20:00:00Z',
                    'test_id': 'test_123',
                    'reason': 'Unexpected decision change',
                    'severity': 'medium'
                },
                {
                    'timestamp': '2026-01-28T19:45:00Z',
                    'test_id': 'test_456',
                    'reason': 'Timeout exceeded',
                    'severity': 'low'
                },
                {
                    'timestamp': '2026-01-28T19:30:00Z',
                    'test_id': 'test_789',
                    'reason': 'Assertion failed',
                    'severity': 'high'
                }
            ]
        }

        # Generate markdown content
        content = f"""# Smart Approval Dashboard - Replay Health Report

**Generated:** {build_info['build_timestamp']}
**Commit:** `{build_info['git_commit'][:8]}`

## Test Corpus Status

- **Pass Rate:** {replay_status['pass_rate']:.1%}
- **Total Tests:** {replay_status['total_tests']}
- **Passed:** {replay_status['passed_tests']}
- **Failed:** {replay_status['failed_tests']}

## Recent Test Failures

| Timestamp | Test ID | Reason | Severity |
|-----------|---------|--------|----------|
"""

        for failure in replay_status['recent_failures']:
            content += f"| {failure['timestamp'][:19]} | {failure['test_id']} | {failure['reason']} | {failure['severity']} |\n"

        content += "\n## Health Assessment\n\n"

        if replay_status['pass_rate'] >= 0.95:
            content += "✅ **Status: Healthy** - Test pass rate is excellent.\n"
        elif replay_status['pass_rate'] >= 0.90:
            content += "⚠️ **Status: Warning** - Test pass rate needs attention.\n"
        else:
            content += "❌ **Status: Critical** - Test pass rate requires immediate action.\n"

        # Write to file
        output_file = self.config.output_path / "replay_health.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_file)


# Register this renderer
renderer_registry.register('markdown_report', MarkdownReportRenderer)