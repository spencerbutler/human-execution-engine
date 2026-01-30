"""JSON API bundle renderer for metrics data."""

import json
from typing import Dict, Any, List
from pathlib import Path

from ..lib.render.base import MetricsRenderer, RendererConfig, renderer_registry


class JsonBundleRenderer(MetricsRenderer):
    """Renderer that generates JSON bundles for API consumption."""

    def __init__(self, config: RendererConfig):
        super().__init__(config)

    def get_supported_views(self) -> List[str]:
        """Return supported view names."""
        return ['overview', 'decisions', 'replay_health']

    def get_output_format(self) -> str:
        """Return output format."""
        return 'json'

    def render_overview_view(self, metrics_data: Dict[str, Any]) -> str:
        """Render overview data as JSON."""
        self.ensure_output_directory()

        metrics = metrics_data.get('metrics', {})
        build_info = self.get_build_info()

        # Structure overview data
        overview_data = {
            'view': 'overview',
            'build_info': build_info,
            'kpis': {
                'prompt_rate': {
                    'value': metrics.get('prompt_rate', 0),
                    'unit': 'per_minute',
                    'description': 'Rate of prompts processed per minute'
                },
                'override_rate': {
                    'value': metrics.get('override_rate', 0),
                    'unit': 'per_minute',
                    'description': 'Rate of human overrides per minute'
                },
                'deny_rate': {
                    'value': metrics.get('deny_rate', 0),
                    'unit': 'per_minute',
                    'description': 'Rate of denied requests per minute'
                },
                'safety_incidents': {
                    'value': metrics.get('safety_incidents', 0),
                    'unit': 'count',
                    'description': 'Number of safety incidents recorded'
                },
                'phase_day': {
                    'value': metrics.get('phase_day', 1),
                    'unit': 'day',
                    'description': 'Current phase day'
                }
            },
            'timeseries': metrics.get('timeseries_data', {})
        }

        # Write to file
        output_file = self.config.output_path / "overview.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(overview_data, f, indent=2, default=str)

        return str(output_file)

    def render_decisions_view(self, metrics_data: Dict[str, Any]) -> str:
        """Render decisions data as JSON."""
        self.ensure_output_directory()

        metrics = metrics_data.get('metrics', {})
        build_info = self.get_build_info()

        # Structure decisions data
        decisions_data = {
            'view': 'decisions',
            'build_info': build_info,
            'deny_reasons_breakdown': metrics.get('deny_reasons', {}),
            'recent_decisions': metrics.get('recent_decisions', []),
            'decision_summary': metrics.get('aggregates', {}).get('decisions', {})
        }

        # Write to file
        output_file = self.config.output_path / "decisions.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(decisions_data, f, indent=2, default=str)

        return str(output_file)

    def render_replay_health_view(self, metrics_data: Dict[str, Any]) -> str:
        """Render replay health data as JSON."""
        self.ensure_output_directory()

        build_info = self.get_build_info()

        # Mock replay health data - in real implementation, this would come from metrics
        replay_data = {
            'view': 'replay_health',
            'build_info': build_info,
            'status': {
                'pass_rate': 0.95,
                'total_tests': 1000,
                'passed_tests': 950,
                'failed_tests': 50,
                'last_run_timestamp': build_info['build_timestamp']
            },
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

        # Write to file
        output_file = self.config.output_path / "replay_health.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(replay_data, f, indent=2, default=str)

        return str(output_file)


# Register this renderer
renderer_registry.register('json_bundle', JsonBundleRenderer)