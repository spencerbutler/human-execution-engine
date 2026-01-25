#!/usr/bin/env python3
"""
HEE Performance Monitor
Enterprise-grade performance monitoring and optimization for HEE systems.
"""

import json
import os
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
import logging
from collections import deque


class PerformanceMonitor:
    """Comprehensive performance monitoring for HEE systems."""

    def __init__(self, log_file: str = "docs/PERFORMANCE_LOG.json"):
        self.log_file = log_file
        self.metrics_history = deque(maxlen=1000)  # Keep last 1000 measurements
        self.alerts = []
        self.performance_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0,
            'response_time_ms': 5000,
            'error_rate_percent': 5.0
        }

        # Initialize logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup performance logging."""
        logging.basicConfig(
            filename='docs/performance_monitor.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system performance metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024 ** 3)
            memory_total_gb = memory.total / (1024 ** 3)

            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024 ** 3)
            disk_total_gb = disk.total / (1024 ** 3)

            # Network metrics (basic)
            network = psutil.net_io_counters()
            bytes_sent_mb = network.bytes_sent / (1024 ** 2)
            bytes_recv_mb = network.bytes_recv / (1024 ** 2)

            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency_mhz': cpu_freq.current if cpu_freq else None
                },
                'memory': {
                    'percent': memory_percent,
                    'used_gb': round(memory_used_gb, 2),
                    'total_gb': round(memory_total_gb, 2),
                    'available_gb': round(memory.available / (1024 ** 3), 2)
                },
                'disk': {
                    'percent': disk_percent,
                    'used_gb': round(disk_used_gb, 2),
                    'total_gb': round(disk_total_gb, 2),
                    'free_gb': round(disk.free / (1024 ** 3), 2)
                },
                'network': {
                    'bytes_sent_mb': round(bytes_sent_mb, 2),
                    'bytes_recv_mb': round(bytes_recv_mb, 2)
                }
            }

            self.metrics_history.append(metrics)
            return metrics

        except Exception as e:
            logging.error(f"Error collecting system metrics: {e}")
            return {}

    def monitor_process_performance(self, process_name: str = "python") -> Dict[str, Any]:
        """Monitor specific process performance."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
                try:
                    if process_name.lower() in proc.info['name'].lower():
                        proc.cpu_percent()  # Call once to get initial value
                        time.sleep(0.1)  # Short delay for accurate measurement
                        cpu_percent = proc.cpu_percent()

                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu_percent': cpu_percent,
                            'memory_percent': proc.info['memory_percent'],
                            'cmdline': ' '.join(proc.info['cmdline'][:3]) if proc.info['cmdline'] else ''
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return {
                'timestamp': datetime.now().isoformat(),
                'process_name': process_name,
                'process_count': len(processes),
                'processes': processes,
                'total_cpu_percent': sum(p['cpu_percent'] for p in processes),
                'total_memory_percent': sum(p['memory_percent'] for p in processes)
            }

        except Exception as e:
            logging.error(f"Error monitoring process performance: {e}")
            return {}

    def monitor_response_times(self, endpoints: List[str] = None) -> Dict[str, Any]:
        """Monitor API endpoint response times."""
        if endpoints is None:
            endpoints = [
                'http://localhost:5000/api/health',
                'http://localhost:5000/api/config'
            ]

        import requests

        response_times = {}
        errors = []

        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(endpoint, timeout=10)
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

                response_times[endpoint] = {
                    'response_time_ms': round(response_time, 2),
                    'status_code': response.status_code,
                    'success': response.status_code < 400
                }

            except requests.RequestException as e:
                errors.append(f"{endpoint}: {str(e)}")
                response_times[endpoint] = {
                    'response_time_ms': None,
                    'status_code': None,
                    'success': False,
                    'error': str(e)
                }

        return {
            'timestamp': datetime.now().isoformat(),
            'response_times': response_times,
            'errors': errors,
            'average_response_time': self._calculate_average_response_time(response_times),
            'error_rate': len(errors) / len(endpoints) if endpoints else 0
        }

    def _calculate_average_response_time(self, response_times: Dict[str, Any]) -> Optional[float]:
        """Calculate average response time from successful requests."""
        successful_times = [
            data['response_time_ms']
            for data in response_times.values()
            if data.get('success') and data.get('response_time_ms') is not None
        ]

        return round(sum(successful_times) / len(successful_times), 2) if successful_times else None

    def check_performance_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for performance alerts based on thresholds."""
        alerts = []

        # CPU alerts
        if metrics.get('cpu', {}).get('percent', 0) > self.performance_thresholds['cpu_percent']:
            alerts.append({
                'level': 'warning',
                'type': 'cpu_usage',
                'message': f"High CPU usage: {metrics['cpu']['percent']:.1f}%",
                'threshold': self.performance_thresholds['cpu_percent'],
                'current': metrics['cpu']['percent']
            })

        # Memory alerts
        if metrics.get('memory', {}).get('percent', 0) > self.performance_thresholds['memory_percent']:
            alerts.append({
                'level': 'critical',
                'type': 'memory_usage',
                'message': f"High memory usage: {metrics['memory']['percent']:.1f}%",
                'threshold': self.performance_thresholds['memory_percent'],
                'current': metrics['memory']['percent']
            })

        # Disk alerts
        if metrics.get('disk', {}).get('percent', 0) > self.performance_thresholds['disk_usage_percent']:
            alerts.append({
                'level': 'critical',
                'type': 'disk_usage',
                'message': f"High disk usage: {metrics['disk']['percent']:.1f}%",
                'threshold': self.performance_thresholds['disk_usage_percent'],
                'current': metrics['disk']['percent']
            })

        self.alerts.extend(alerts)
        return alerts

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        if not self.metrics_history:
            return {'error': 'No performance data available'}

        # Calculate averages and trends
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 measurements

        cpu_percents = [m.get('cpu', {}).get('percent', 0) for m in recent_metrics]
        memory_percents = [m.get('memory', {}).get('percent', 0) for m in recent_metrics]
        disk_percents = [m.get('disk', {}).get('percent', 0) for m in recent_metrics]

        report = {
            'generated_at': datetime.now().isoformat(),
            'data_points': len(recent_metrics),
            'averages': {
                'cpu_percent': round(sum(cpu_percents) / len(cpu_percents), 1) if cpu_percents else 0,
                'memory_percent': round(sum(memory_percents) / len(memory_percents), 1) if memory_percents else 0,
                'disk_percent': round(sum(disk_percents) / len(disk_percents), 1) if disk_percents else 0
            },
            'trends': {
                'cpu_trend': self._calculate_trend(cpu_percents),
                'memory_trend': self._calculate_trend(memory_percents),
                'disk_trend': self._calculate_trend(disk_percents)
            },
            'alerts': self.alerts[-10:],  # Last 10 alerts
            'recommendations': self._generate_performance_recommendations()
        }

        return report

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate performance trend."""
        if len(values) < 2:
            return "insufficient_data"

        # Simple trend calculation
        first_half = sum(values[:len(values)//2]) / len(values[:len(values)//2])
        second_half = sum(values[len(values)//2:]) / len(values[len(values)//2:])

        diff = second_half - first_half

        if diff > 5:
            return "increasing"
        elif diff < -5:
            return "decreasing"
        else:
            return "stable"

    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []

        if not self.metrics_history:
            return recommendations

        recent = list(self.metrics_history)[-5:]

        # Memory optimization
        avg_memory = sum(m.get('memory', {}).get('percent', 0) for m in recent) / len(recent)
        if avg_memory > 80:
            recommendations.append("⚠️ High memory usage detected - consider optimizing data caching")
            recommendations.append("💡 Recommendation: Implement memory-efficient data structures")

        # CPU optimization
        avg_cpu = sum(m.get('cpu', {}).get('percent', 0) for m in recent) / len(recent)
        if avg_cpu > 70:
            recommendations.append("⚠️ High CPU usage detected - consider optimizing algorithms")
            recommendations.append("💡 Recommendation: Implement async processing for intensive operations")

        # Disk optimization
        avg_disk = sum(m.get('disk', {}).get('percent', 0) for m in recent) / len(recent)
        if avg_disk > 85:
            recommendations.append("🚨 Critical disk usage - implement data cleanup")
            recommendations.append("💡 Recommendation: Add automated log rotation and temp file cleanup")

        # General recommendations
        if len(self.alerts) > 5:
            recommendations.append("📊 Multiple performance alerts detected - review system configuration")

        if not recommendations:
            recommendations.append("✅ System performance is within normal parameters")

        return recommendations

    def start_continuous_monitoring(self, interval_seconds: int = 60) -> None:
        """Start continuous performance monitoring."""
        def monitoring_loop():
            while True:
                try:
                    # Collect system metrics
                    system_metrics = self.collect_system_metrics()

                    # Monitor HEE processes
                    process_metrics = self.monitor_process_performance("python")

                    # Monitor API response times
                    response_metrics = self.monitor_response_times()

                    # Check for alerts
                    alerts = self.check_performance_alerts(system_metrics)

                    # Log comprehensive metrics
                    self._log_comprehensive_metrics({
                        'system': system_metrics,
                        'processes': process_metrics,
                        'responses': response_metrics,
                        'alerts': alerts
                    })

                    time.sleep(interval_seconds)

                except Exception as e:
                    logging.error(f"Error in monitoring loop: {e}")
                    time.sleep(interval_seconds)

        # Start monitoring in background thread
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()

        logging.info(f"Continuous performance monitoring started (interval: {interval_seconds}s)")

    def _log_comprehensive_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log comprehensive performance metrics."""
        try:
            # Ensure log directory exists
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

            # Read existing logs
            existing_logs = []
            if os.path.exists(self.log_file):
                try:
                    with open(self.log_file, 'r') as f:
                        existing_logs = json.load(f)
                except (json.JSONDecodeError, IOError):
                    existing_logs = []

            # Add new metrics
            existing_logs.append({
                'timestamp': datetime.now().isoformat(),
                **metrics
            })

            # Keep only last 100 entries
            existing_logs = existing_logs[-100:]

            # Write back to file
            with open(self.log_file, 'w') as f:
                json.dump(existing_logs, f, indent=2)

        except Exception as e:
            logging.error(f"Error logging comprehensive metrics: {e}")


def main():
    """Command-line interface for performance monitoring."""
    import argparse

    parser = argparse.ArgumentParser(description='HEE Performance Monitor')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--report', action='store_true', help='Generate performance report')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
    parser.add_argument('--processes', help='Monitor specific process name')
    parser.add_argument('--endpoints', nargs='+', help='Monitor specific API endpoints')

    args = parser.parse_args()

    monitor = PerformanceMonitor()

    if args.monitor:
        print(f"🚀 Starting continuous performance monitoring (interval: {args.interval}s)")
        print("Press Ctrl+C to stop...")
        monitor.start_continuous_monitoring(args.interval)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")

    elif args.report:
        report = monitor.generate_performance_report()

        if 'error' in report:
            print(f"❌ Error: {report['error']}")
            return

        print("📊 HEE Performance Report")
        print("=" * 40)
        print(f"Generated: {report['generated_at']}")
        print(f"Data Points: {report['data_points']}")
        print()

        print("📈 Average Metrics:")
        avg = report['averages']
        print(f"  CPU Usage: {avg['cpu_percent']:.1f}%")
        print(f"  Memory Usage: {avg['memory_percent']:.1f}%")
        print(f"  Disk Usage: {avg['disk_percent']:.1f}%")
        print()

        print("📊 Trends:")
        trends = report['trends']
        print(f"  CPU: {trends['cpu_trend']}")
        print(f"  Memory: {trends['memory_trend']}")
        print(f"  Disk: {trends['disk_trend']}")
        print()

        if report['recommendations']:
            print("💡 Performance Recommendations:")
            for rec in report['recommendations']:
                print(f"  {rec}")
            print()

    elif args.processes:
        metrics = monitor.monitor_process_performance(args.processes)
        print(f"🔍 Process Monitoring: {args.processes}")
        print("=" * 40)
        print(f"Found {metrics['process_count']} processes")
        print(f"Total CPU: {metrics['total_cpu_percent']:.1f}%")
        print(f"Total Memory: {metrics['total_memory_percent']:.1f}%")

        for proc in metrics['processes'][:5]:  # Show first 5
            print(f"  PID {proc['pid']}: {proc['cpu_percent']:.1f}% CPU, {proc['memory_percent']:.1f}% MEM")

    else:
        # Quick system check
        metrics = monitor.collect_system_metrics()
        alerts = monitor.check_performance_alerts(metrics)

        print("🖥️  System Performance Snapshot")
        print("=" * 40)

        if metrics.get('cpu'):
            print(f"CPU: {metrics['cpu']['percent']:.1f}% ({metrics['cpu']['count']} cores)")

        if metrics.get('memory'):
            print(f"Memory: {metrics['memory']['used_gb']:.1f}GB / {metrics['memory']['total_gb']:.1f}GB ({metrics['memory']['percent']:.1f}%)")

        if metrics.get('disk'):
            print(f"Disk: {metrics['disk']['used_gb']:.1f}GB / {metrics['disk']['total_gb']:.1f}GB ({metrics['disk']['percent']:.1f}%)")

        if alerts:
            print(f"\n⚠️  {len(alerts)} Performance Alerts:")
            for alert in alerts:
                print(f"  {alert['level'].upper()}: {alert['message']}")
        else:
            print("\n✅ System performance is within normal parameters")


if __name__ == '__main__':
    main()
