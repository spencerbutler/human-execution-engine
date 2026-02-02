"""Plotly static HTML renderer for metrics visualization."""

import json
from typing import Dict, Any, List
from pathlib import Path

from ..lib.render.base import MetricsRenderer, RendererConfig, renderer_registry


class PlotlyStaticRenderer(MetricsRenderer):
    """Renderer that generates static HTML files with Plotly.js visualizations."""

    def __init__(self, config: RendererConfig):
        super().__init__(config)

    def get_supported_views(self) -> List[str]:
        """Return supported view names."""
        return ['overview', 'decisions', 'replay_health']

    def get_output_format(self) -> str:
        """Return output format."""
        return 'html'

    def render_overview_view(self, metrics_data: Dict[str, Any]) -> str:
        """Render overview dashboard with KPI strip and timeseries charts."""
        self.ensure_output_directory()

        metrics = metrics_data.get('metrics', {})
        timeseries_data = metrics.get('timeseries_data', {})

        # Generate HTML content
        html_content = self._generate_overview_html(metrics, timeseries_data)

        # Write to file
        output_file = self.config.output_path / "overview.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file)

    def render_decisions_view(self, metrics_data: Dict[str, Any]) -> str:
        """Render decisions table view."""
        self.ensure_output_directory()

        metrics = metrics_data.get('metrics', {})

        # Generate HTML content
        html_content = self._generate_decisions_html(metrics)

        # Write to file
        output_file = self.config.output_path / "decisions.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file)

    def render_replay_health_view(self, metrics_data: Dict[str, Any]) -> str:
        """Render replay health status view."""
        self.ensure_output_directory()

        metrics = metrics_data.get('metrics', {})

        # Generate HTML content
        html_content = self._generate_replay_health_html(metrics)

        # Write to file
        output_file = self.config.output_path / "replay_health.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file)

    def _generate_overview_html(self, metrics: Dict[str, Any], timeseries_data: Dict[str, Any]) -> str:
        """Generate HTML for overview dashboard."""
        build_info = self.get_build_info()

        # Prepare data for charts
        hourly_data = timeseries_data.get('hourly', [])
        timestamps = [d['timestamp'] for d in hourly_data]
        prompt_rates = [d['prompt_rate'] for d in hourly_data]
        override_rates = [d['override_rate'] for d in hourly_data]
        deny_rates = [d['deny_rate'] for d in hourly_data]

        # KPI values
        kpi_data = {
            'prompt_rate': metrics.get('prompt_rate', 0),
            'override_rate': metrics.get('override_rate', 0),
            'deny_rate': metrics.get('deny_rate', 0),
            'safety_incidents': metrics.get('safety_incidents', 0),
            'phase_day': metrics.get('phase_day', 1)
        }

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Smart Approval - Overview</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .kpi-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .kpi-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .kpi-label {{
            color: #666;
            margin-top: 5px;
        }}
        .chart-container {{
            margin-bottom: 30px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Smart Approval Dashboard - Overview</h1>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-value">{kpi_data['prompt_rate']:.1f}</div>
                <div class="kpi-label">Prompt Rate<br/>(per minute)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{kpi_data['override_rate']:.1f}</div>
                <div class="kpi-label">Override Rate<br/>(per minute)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{kpi_data['deny_rate']:.1f}</div>
                <div class="kpi-label">Deny Rate<br/>(per minute)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{kpi_data['safety_incidents']}</div>
                <div class="kpi-label">Safety Incidents</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{kpi_data['phase_day']}</div>
                <div class="kpi-label">Phase Day</div>
            </div>
        </div>

        <div class="chart-container">
            <h2>Rate Trends (Hourly)</h2>
            <div id="rates-chart"></div>
        </div>

        <div class="footer">
            <p>Generated: {build_info['build_timestamp']}<br/>
            Commit: {build_info['git_commit'][:8]}</p>
        </div>
    </div>

    <script>
        const timestamps = {json.dumps(timestamps)};
        const promptRates = {json.dumps(prompt_rates)};
        const overrideRates = {json.dumps(override_rates)};
        const denyRates = {json.dumps(deny_rates)};

        const trace1 = {{
            x: timestamps,
            y: promptRates,
            mode: 'lines+markers',
            name: 'Prompt Rate',
            line: {{color: '#007bff'}}
        }};

        const trace2 = {{
            x: timestamps,
            y: overrideRates,
            mode: 'lines+markers',
            name: 'Override Rate',
            line: {{color: '#28a745'}}
        }};

        const trace3 = {{
            x: timestamps,
            y: denyRates,
            mode: 'lines+markers',
            name: 'Deny Rate',
            line: {{color: '#dc3545'}}
        }};

        const layout = {{
            title: 'Processing Rates Over Time',
            xaxis: {{title: 'Time'}},
            yaxis: {{title: 'Rate (per minute)'}},
            margin: {{l: 50, r: 50, t: 50, b: 50}}
        }};

        Plotly.newPlot('rates-chart', [trace1, trace2, trace3], layout);
    </script>
</body>
</html>
"""

    def _generate_decisions_html(self, metrics: Dict[str, Any]) -> str:
        """Generate HTML for decisions table view."""
        build_info = self.get_build_info()

        recent_decisions = metrics.get('recent_decisions', [])
        deny_reasons = metrics.get('deny_reasons', {})

        # Prepare deny reasons data for chart
        reason_labels = list(deny_reasons.keys())
        reason_values = list(deny_reasons.values())

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Smart Approval - Decisions</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        .decisions-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}
        .decisions-table th,
        .decisions-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .decisions-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        .decision-approve {{ color: #28a745; font-weight: bold; }}
        .decision-deny {{ color: #dc3545; font-weight: bold; }}
        .decision-override {{ color: #ffc107; font-weight: bold; }}
        .chart-container {{
            margin-bottom: 30px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Smart Approval Dashboard - Decisions</h1>

        <div class="chart-container">
            <h2>Deny Reasons Distribution</h2>
            <div id="deny-reasons-chart"></div>
        </div>

        <h2>Recent Decisions</h2>
        <table class="decisions-table">
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Decision</th>
                    <th>Reason</th>
                    <th>Confidence</th>
                </tr>
            </thead>
            <tbody>
"""

        for decision in recent_decisions[:50]:  # Show last 50 decisions
            decision_class = f"decision-{decision.get('decision', 'unknown').lower()}"
            timestamp = decision.get('timestamp', '')[:19]  # Format timestamp
            confidence = f"{decision.get('confidence', 0):.2f}" if decision.get('confidence') else 'N/A'

            html_content += f"""
                <tr>
                    <td>{timestamp}</td>
                    <td class="{decision_class}">{decision.get('decision', 'unknown').title()}</td>
                    <td>{decision.get('reason', 'N/A')}</td>
                    <td>{confidence}</td>
                </tr>
"""

        html_content += f"""
            </tbody>
        </table>

        <div class="footer">
            <p>Generated: {build_info['build_timestamp']}<br/>
            Commit: {build_info['git_commit'][:8]}</p>
        </div>
    </div>

    <script>
        const reasonLabels = {json.dumps(reason_labels)};
        const reasonValues = {json.dumps(reason_values)};

        const data = [{{
            labels: reasonLabels,
            values: reasonValues,
            type: 'pie',
            textinfo: 'label+percent',
            insidetextorientation: 'radial'
        }}];

        const layout = {{
            title: 'Deny Reasons Breakdown',
            margin: {{l: 50, r: 50, t: 50, b: 50}}
        }};

        Plotly.newPlot('deny-reasons-chart', data, layout);
    </script>
</body>
</html>
"""

    def _generate_replay_health_html(self, metrics: Dict[str, Any]) -> str:
        """Generate HTML for replay health view."""
        build_info = self.get_build_info()

        # Mock replay health data - in real implementation, this would come from metrics
        replay_status = {
            'pass_rate': 0.95,
            'total_tests': 1000,
            'failed_tests': 50,
            'recent_failures': [
                {'timestamp': '2026-01-28T20:00:00', 'reason': 'Unexpected decision change'},
                {'timestamp': '2026-01-28T19:45:00', 'reason': 'Timeout exceeded'},
                {'timestamp': '2026-01-28T19:30:00', 'reason': 'Assertion failed'}
            ]
        }

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Smart Approval - Replay Health</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        .status-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .status-value {{
            font-size: 3em;
            font-weight: bold;
            color: #28a745;
        }}
        .status-label {{
            color: #666;
            margin-top: 10px;
        }}
        .failures-list {{
            margin-bottom: 30px;
        }}
        .failure-item {{
            padding: 10px;
            border-left: 4px solid #dc3545;
            background: #fff5f5;
            margin-bottom: 10px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Smart Approval Dashboard - Replay Health</h1>

        <div class="status-card">
            <div class="status-value">{replay_status['pass_rate']:.1%}</div>
            <div class="status-label">Replay Corpus Pass Rate</div>
            <div style="margin-top: 10px; color: #666;">
                {replay_status['total_tests'] - replay_status['failed_tests']}/{replay_status['total_tests']} tests passing
            </div>
        </div>

        <h2>Recent Test Failures</h2>
        <div class="failures-list">
"""

        for failure in replay_status['recent_failures']:
            html_content += f"""
            <div class="failure-item">
                <strong>{failure['timestamp']}</strong><br/>
                {failure['reason']}
            </div>
"""

        html_content += f"""
        </div>

        <div class="footer">
            <p>Generated: {build_info['build_timestamp']}<br/>
            Commit: {build_info['git_commit'][:8]}</p>
        </div>
    </div>
</body>
</html>
"""


# Register this renderer
renderer_registry.register('plotly_static', PlotlyStaticRenderer)
