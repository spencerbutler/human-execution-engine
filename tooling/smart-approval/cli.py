#!/usr/bin/env python3
"""CLI tool for building smart approval metrics dashboards."""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add the lib directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from lib.ingest import DataIngestor
from lib.transform import MetricsAggregator
from lib.render.base import RendererConfig, renderer_registry


def build_dashboard_bundle(
    data_path: str,
    output_path: str,
    renderer_name: str = "plotly_static",
    views: Optional[list] = None
) -> Dict[str, Any]:
    """Build a complete dashboard bundle from metrics data.

    Args:
        data_path: Path to directory containing transcript and metrics files
        output_path: Path where dashboard files should be written
        renderer_name: Name of renderer to use
        views: List of views to generate (default: all supported views)

    Returns:
        Dictionary with build results and metadata
    """
    print(f"Building dashboard bundle from: {data_path}")
    print(f"Output path: {output_path}")
    print(f"Using renderer: {renderer_name}")

    # Step 1: Ingest data
    print("Step 1: Ingesting data...")
    ingestor = DataIngestor(data_path)
    ingested_data = ingestor.ingest_all_data()
    print(f"  - Processed {len(ingested_data['transcripts'])} transcripts")
    print(f"  - Extracted {len(ingested_data['events'])} events")

    # Step 2: Transform data
    print("Step 2: Transforming data...")
    aggregator = MetricsAggregator()
    processed_data = aggregator.process_ingested_data(ingested_data)
    print("  - Computed metrics and aggregations")

    # Step 3: Render views
    print("Step 3: Rendering views...")

    # Get renderer
    config = RendererConfig(output_path)
    renderer = renderer_registry.get_renderer(renderer_name, config)

    if not renderer:
        available = renderer_registry.list_available_renderers()
        raise ValueError(f"Renderer '{renderer_name}' not found. Available: {available}")

    # Determine which views to render
    supported_views = renderer.get_supported_views()
    if views is None:
        views_to_render = supported_views
    else:
        views_to_render = [v for v in views if v in supported_views]
        if not views_to_render:
            raise ValueError(f"None of the requested views {views} are supported by {renderer_name}")

    print(f"  - Rendering views: {views_to_render}")

    # Render each view
    rendered_files = {}
    for view in views_to_render:
        print(f"    - Rendering {view} view...")
        if view == "overview":
            output_file = renderer.render_overview_view(processed_data)
        elif view == "decisions":
            output_file = renderer.render_decisions_view(processed_data)
        elif view == "replay_health":
            output_file = renderer.render_replay_health_view(processed_data)
        else:
            print(f"      Warning: Unknown view '{view}', skipping")
            continue

        rendered_files[view] = output_file
        print(f"      -> {output_file}")

    # Step 4: Generate additional artifacts
    print("Step 4: Generating additional artifacts...")

    output_dir = Path(output_path)

    # Generate metrics JSON bundle
    metrics_bundle = _generate_metrics_bundle(processed_data, output_dir)
    print(f"  - Metrics bundle: {metrics_bundle}")

    # Generate alerts JSON bundle
    alerts_bundle = _generate_alerts_bundle(processed_data, output_dir)
    print(f"  - Alerts bundle: {alerts_bundle}")

    # Generate index HTML if overview exists
    if "overview" in rendered_files:
        index_file = _generate_index_html(output_dir, rendered_files)
        print(f"  - Index file: {index_file}")

    print("Dashboard bundle build complete!")

    return {
        'build_info': processed_data.get('ingestion_info', {}),
        'rendered_files': rendered_files,
        'artifacts': {
            'metrics_bundle': metrics_bundle,
            'alerts_bundle': alerts_bundle,
            'index_file': index_file if "overview" in rendered_files else None
        },
        'renderer': renderer_name,
        'views': views_to_render
    }


def _generate_metrics_bundle(processed_data: Dict[str, Any], output_dir: Path) -> str:
    """Generate metrics JSON bundle."""
    metrics_file = output_dir / "data" / "metrics.json"
    metrics_file.parent.mkdir(parents=True, exist_ok=True)

    # Extract the metrics data
    metrics_data = processed_data.get('metrics', {})

    # Add build metadata
    bundle = {
        'version': '1.0',
        'generated_at': processed_data.get('ingestion_info', {}).get('timestamp'),
        'data': metrics_data
    }

    import json
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(bundle, f, indent=2, default=str)

    return str(metrics_file)


def _generate_alerts_bundle(processed_data: Dict[str, Any], output_dir: Path) -> str:
    """Generate alerts JSON bundle."""
    alerts_file = output_dir / "data" / "alerts.json"
    alerts_file.parent.mkdir(parents=True, exist_ok=True)

    # Generate mock alerts based on metrics (in real implementation, this would be more sophisticated)
    metrics = processed_data.get('metrics', {})
    alerts = []

    # Safety incident alert
    if metrics.get('safety_incidents', 0) > 0:
        alerts.append({
            'id': 'safety_incidents',
            'level': 'warning',
            'title': 'Safety Incidents Detected',
            'message': f"{metrics['safety_incidents']} safety incidents recorded",
            'timestamp': metrics.get('timestamp')
        })

    # High deny rate alert
    deny_rate = metrics.get('deny_rate', 0)
    if deny_rate > 1.0:  # More than 1 denial per minute
        alerts.append({
            'id': 'high_deny_rate',
            'level': 'info',
            'title': 'High Denial Rate',
            'message': f"Deny rate is {deny_rate:.1f} per minute",
            'timestamp': metrics.get('timestamp')
        })

    bundle = {
        'version': '1.0',
        'generated_at': processed_data.get('ingestion_info', {}).get('timestamp'),
        'alerts': alerts
    }

    import json
    with open(alerts_file, 'w', encoding='utf-8') as f:
        json.dump(bundle, f, indent=2, default=str)

    return str(alerts_file)


def _generate_index_html(output_dir: Path, rendered_files: Dict[str, str]) -> str:
    """Generate main index.html that links to all views."""
    index_file = output_dir / "index.html"

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Smart Approval Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .dashboard-container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            padding: 40px;
            text-align: center;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 40px;
            font-size: 1.1em;
        }}
        .nav-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .nav-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 25px;
            text-decoration: none;
            color: #333;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }}
        .nav-card:hover {{
            background: #007bff;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,123,255,0.3);
        }}
        .nav-card h3 {{
            margin: 0 0 10px 0;
            font-size: 1.3em;
        }}
        .nav-card p {{
            margin: 0;
            opacity: 0.8;
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
    <div class="dashboard-container">
        <h1>Smart Approval Dashboard</h1>
        <p class="subtitle">Extensible metrics visualization for smart approval systems</p>

        <div class="nav-grid">
            <a href="overview.html" class="nav-card">
                <h3>📊 Overview</h3>
                <p>KPI metrics and rate trends</p>
            </a>
            <a href="decisions.html" class="nav-card">
                <h3>⚖️ Decisions</h3>
                <p>Decision analysis and deny reasons</p>
            </a>
            <a href="replay_health.html" class="nav-card">
                <h3>🔄 Replay Health</h3>
                <p>Test corpus status and failures</p>
            </a>
        </div>

        <div class="footer">
            <p>Dashboard bundle generated with smart-approval CLI</p>
        </div>
    </div>
</body>
</html>"""

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return str(index_file)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Build smart approval metrics dashboards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/data /path/to/output
  %(prog)s /path/to/data /path/to/output --renderer plotly_static --views overview decisions
  %(prog)s /path/to/data /path/to/output --renderer json_bundle
        """
    )

    parser.add_argument(
        'data_path',
        help='Path to directory containing transcript and metrics files'
    )

    parser.add_argument(
        'output_path',
        help='Path where dashboard files should be written'
    )

    parser.add_argument(
        '--renderer',
        default='plotly_static',
        choices=renderer_registry.list_available_renderers(),
        help='Renderer to use for generating visualizations (default: plotly_static)'
    )

    parser.add_argument(
        '--views',
        nargs='+',
        help='Specific views to generate (default: all supported views)'
    )

    parser.add_argument(
        '--list-renderers',
        action='store_true',
        help='List available renderers and exit'
    )

    args = parser.parse_args()

    # Handle list renderers option
    if args.list_renderers:
        print("Available renderers:")
        for renderer_name in renderer_registry.list_available_renderers():
            info = renderer_registry.get_renderer_info(renderer_name)
            if info:
                print(f"  - {renderer_name}: {info.get('supported_views', [])} views ({info.get('output_format', 'unknown')} format)")
            else:
                print(f"  - {renderer_name}")
        return

    # Validate paths
    data_path = Path(args.data_path)
    if not data_path.exists():
        print(f"Error: Data path does not exist: {data_path}")
        sys.exit(1)

    output_path = Path(args.output_path)

    try:
        # Build the dashboard bundle
        result = build_dashboard_bundle(
            str(data_path),
            str(output_path),
            args.renderer,
            args.views
        )

        print("\nBuild Summary:")
        print(f"  Renderer: {result['renderer']}")
        print(f"  Views generated: {', '.join(result['views'])}")
        print(f"  Files created: {len(result['rendered_files']) + len(result['artifacts'])}")

        # Print file locations
        print("\nGenerated files:")
        for view, file_path in result['rendered_files'].items():
            print(f"  - {view}: {file_path}")

        for artifact_name, file_path in result['artifacts'].items():
            if file_path:
                print(f"  - {artifact_name}: {file_path}")

        print("\n✅ Dashboard bundle build successful!")
        print(f"Open {output_path}/index.html in your browser to view the dashboard.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
