#!/usr/bin/env python3
"""
HEE Monitoring Dashboard
Web interface for real-time branch health monitoring and analytics.
"""

import json
import os
import sys
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extras.observability.branch_health.branch_health_monitor import BranchHealthMonitor


app = Flask(__name__)
monitor = BranchHealthMonitor()


@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/health')
def get_health_data():
    """API endpoint for health data."""
    try:
        report = monitor.get_health_report()
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/branch/<branch_name>')
def get_branch_data(branch_name):
    """API endpoint for specific branch data."""
    try:
        metrics = monitor.monitor_branch(branch_name)
        return jsonify(metrics.__dict__)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """API endpoint for configuration management."""
    if request.method == 'POST':
        try:
            config_data = request.get_json()
            monitor.thresholds.max_age_days = config_data.get('max_age_days', 7)
            monitor.thresholds.max_commits_behind = config_data.get('max_commits_behind', 10)
            monitor.thresholds.critical_score = config_data.get('critical_score', 30.0)
            monitor.thresholds.warning_score = config_data.get('warning_score', 60.0)
            monitor.thresholds.excellent_score = config_data.get('excellent_score', 90.0)
            monitor.save_config()
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({
            'max_age_days': monitor.thresholds.max_age_days,
            'max_commits_behind': monitor.thresholds.max_commits_behind,
            'critical_score': monitor.thresholds.critical_score,
            'warning_score': monitor.thresholds.warning_score,
            'excellent_score': monitor.thresholds.excellent_score
        })


@app.route('/api/alerts')
def get_alerts():
    """API endpoint for active alerts."""
    try:
        report = monitor.get_health_report()
        alerts = []

        for branch in report['branches']:
            if branch['risk_level'] in ['critical', 'warning']:
                alerts.append({
                    'branch': branch['branch_name'],
                    'severity': branch['risk_level'],
                    'score': branch['health_score'],
                    'issues': branch['recommendations']
                })

        return jsonify({
            'alerts': alerts,
            'total': len(alerts),
            'critical': len([a for a in alerts if a['severity'] == 'critical']),
            'warning': len([a for a in alerts if a['severity'] == 'warning'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('web/templates', exist_ok=True)

    # Run the dashboard
    app.run(debug=True, host='0.0.0.0', port=5000)
