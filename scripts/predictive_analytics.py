#!/usr/bin/env python3
"""
HEE Predictive Analytics Engine
Advanced conflict prediction and trend analysis for development workflow optimization.
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics


@dataclass
class PredictiveMetrics:
    """Metrics for predictive analytics."""
    branch_name: str
    prediction_date: str
    conflict_probability: float
    risk_level: str
    predicted_resolution_time: Optional[int]  # hours
    contributing_factors: List[str]
    prevention_recommendations: List[str]
    confidence_score: float


@dataclass
class HistoricalData:
    """Historical branch data for analysis."""
    branch_name: str
    created_date: str
    merged_date: Optional[str]
    conflict_count: int
    pr_age_days: int
    commits_count: int
    health_score_avg: float
    resolution_time_hours: Optional[int]


class PredictiveAnalytics:
    """Advanced analytics engine for conflict prediction and trend analysis."""

    def __init__(self, db_path: str = "docs/BRANCH_ANALYTICS.db"):
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self) -> None:
        """Initialize SQLite database for analytics storage."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS branch_history (
                    id INTEGER PRIMARY KEY,
                    branch_name TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    merged_date TEXT,
                    conflict_count INTEGER DEFAULT 0,
                    pr_age_days INTEGER DEFAULT 0,
                    commits_count INTEGER DEFAULT 0,
                    health_score_avg REAL DEFAULT 0,
                    resolution_time_hours INTEGER,
                    recorded_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS conflict_predictions (
                    id INTEGER PRIMARY KEY,
                    branch_name TEXT NOT NULL,
                    prediction_date TEXT NOT NULL,
                    conflict_probability REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    predicted_resolution_time INTEGER,
                    contributing_factors TEXT,  -- JSON
                    prevention_recommendations TEXT,  -- JSON
                    confidence_score REAL NOT NULL,
                    actual_conflict_occurred INTEGER DEFAULT 0,
                    recorded_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS health_trends (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    total_branches INTEGER,
                    avg_health_score REAL,
                    critical_branches INTEGER,
                    warning_branches INTEGER,
                    total_conflicts INTEGER,
                    recorded_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def store_branch_history(self, history: HistoricalData) -> None:
        """Store historical branch data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO branch_history
                (branch_name, created_date, merged_date, conflict_count,
                 pr_age_days, commits_count, health_score_avg, resolution_time_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                history.branch_name,
                history.created_date,
                history.merged_date,
                history.conflict_count,
                history.pr_age_days,
                history.commits_count,
                history.health_score_avg,
                history.resolution_time_hours
            ))

    def store_prediction(self, prediction: PredictiveMetrics) -> None:
        """Store conflict prediction."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO conflict_predictions
                (branch_name, prediction_date, conflict_probability, risk_level,
                 predicted_resolution_time, contributing_factors, prevention_recommendations,
                 confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction.branch_name,
                prediction.prediction_date,
                prediction.conflict_probability,
                prediction.risk_level,
                prediction.predicted_resolution_time,
                json.dumps(prediction.contributing_factors),
                json.dumps(prediction.prevention_recommendations),
                prediction.confidence_score
            ))

    def store_health_trend(self, date: str, total_branches: int, avg_health: float,
                          critical: int, warning: int, conflicts: int) -> None:
        """Store daily health trend data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO health_trends
                (date, total_branches, avg_health_score, critical_branches,
                 warning_branches, total_conflicts)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (date, total_branches, avg_health, critical, warning, conflicts))

    def analyze_historical_patterns(self) -> Dict[str, Any]:
        """Analyze historical data for predictive insights."""
        with sqlite3.connect(self.db_path) as conn:
            # Get branch success/failure patterns
            cursor = conn.execute('''
                SELECT
                    branch_name,
                    AVG(conflict_count) as avg_conflicts,
                    AVG(pr_age_days) as avg_age,
                    AVG(commits_count) as avg_commits,
                    AVG(health_score_avg) as avg_health,
                    COUNT(*) as total_branches
                FROM branch_history
                GROUP BY branch_name
                HAVING total_branches > 1
            ''')

            patterns = {}
            for row in cursor:
                patterns[row[0]] = {
                    'avg_conflicts': row[1],
                    'avg_age': row[2],
                    'avg_commits': row[3],
                    'avg_health': row[4],
                    'frequency': row[5]
                }

            # Get overall success rates
            cursor = conn.execute('''
                SELECT
                    AVG(conflict_count) as overall_conflicts,
                    AVG(CASE WHEN conflict_count > 0 THEN 1 ELSE 0 END) as conflict_rate,
                    AVG(resolution_time_hours) as avg_resolution_time,
                    COUNT(*) as total_samples
                FROM branch_history
                WHERE merged_date IS NOT NULL
            ''')

            overall_stats = cursor.fetchone()
            overall = {
                'avg_conflicts_per_branch': overall_stats[0] if overall_stats[0] else 0,
                'conflict_rate': overall_stats[1] if overall_stats[1] else 0,
                'avg_resolution_hours': overall_stats[2] if overall_stats[2] else 0,
                'total_historical_branches': overall_stats[3] if overall_stats[3] else 0
            }

            return {
                'patterns': patterns,
                'overall': overall
            }

    def predict_branch_conflicts(self, branch_name: str, current_health_score: float,
                               days_since_last_commit: int, commits_behind: int,
                               has_open_pr: bool) -> PredictiveMetrics:
        """Predict conflict probability for a branch."""

        # Analyze historical patterns
        historical = self.analyze_historical_patterns()
        overall = historical['overall']

        # Calculate base risk factors
        risk_factors = []

        # Health score factor
        if current_health_score < 40:
            risk_factors.append("low_health_score")
        elif current_health_score < 70:
            risk_factors.append("moderate_health_score")

        # Age factor
        if days_since_last_commit > 14:
            risk_factors.append("stale_branch")
        elif days_since_last_commit > 7:
            risk_factors.append("aging_branch")

        # Commit lag factor
        if commits_behind > 20:
            risk_factors.append("significantly_behind")
        elif commits_behind > 10:
            risk_factors.append("moderately_behind")

        # PR status factor
        if not has_open_pr:
            risk_factors.append("no_pr_tracking")

        # Calculate base probability
        base_probability = overall['conflict_rate']

        # Apply risk multipliers
        risk_multiplier = 1.0
        if "low_health_score" in risk_factors:
            risk_multiplier *= 2.5
        if "stale_branch" in risk_factors:
            risk_multiplier *= 2.0
        if "significantly_behind" in risk_factors:
            risk_multiplier *= 1.8
        if "no_pr_tracking" in risk_factors:
            risk_multiplier *= 1.5

        conflict_probability = min(0.95, base_probability * risk_multiplier)

        # Determine risk level
        if conflict_probability > 0.7:
            risk_level = "critical"
        elif conflict_probability > 0.4:
            risk_level = "high"
        elif conflict_probability > 0.2:
            risk_level = "moderate"
        else:
            risk_level = "low"

        # Predict resolution time
        predicted_resolution = None
        if conflict_probability > 0.3:
            # Estimate based on historical data
            avg_resolution = overall['avg_resolution_hours']
            if avg_resolution:
                # Adjust based on risk factors
                adjustment = len(risk_factors) * 2  # hours
                predicted_resolution = int(avg_resolution + adjustment)

        # Generate recommendations
        recommendations = []
        if "stale_branch" in risk_factors:
            recommendations.append("Rebase branch immediately to reduce conflict risk")
        if "significantly_behind" in risk_factors:
            recommendations.append("Merge main branch to reduce divergence")
        if "no_pr_tracking" in risk_factors:
            recommendations.append("Create PR for better tracking and automated conflict detection")
        if "low_health_score" in risk_factors:
            recommendations.append("Address health issues before they cause conflicts")

        if not recommendations:
            recommendations.append("Monitor branch closely for health changes")

        # Calculate confidence score
        historical_samples = overall['total_historical_branches']
        confidence = min(0.9, historical_samples / 50.0)  # Max confidence with 50+ samples

        return PredictiveMetrics(
            branch_name=branch_name,
            prediction_date=datetime.now().isoformat(),
            conflict_probability=round(conflict_probability, 3),
            risk_level=risk_level,
            predicted_resolution_time=predicted_resolution,
            contributing_factors=risk_factors,
            prevention_recommendations=recommendations,
            confidence_score=round(confidence, 2)
        )

    def analyze_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze health trends over time."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT date, total_branches, avg_health_score, critical_branches,
                       warning_branches, total_conflicts
                FROM health_trends
                WHERE date >= date('now', '-{} days')
                ORDER BY date
            '''.format(days))

            trend_data = []
            for row in cursor:
                trend_data.append({
                    'date': row[0],
                    'total_branches': row[1],
                    'avg_health_score': row[2],
                    'critical_branches': row[3],
                    'warning_branches': row[4],
                    'total_conflicts': row[5]
                })

            if not trend_data:
                return {'error': 'No trend data available'}

            # Calculate trend analysis
            health_scores = [d['avg_health_score'] for d in trend_data]
            critical_counts = [d['critical_branches'] for d in trend_data]

            analysis = {
                'period_days': days,
                'data_points': len(trend_data),
                'health_score_trend': self.calculate_trend(health_scores),
                'critical_branch_trend': self.calculate_trend(critical_counts),
                'average_health_score': statistics.mean(health_scores) if health_scores else 0,
                'average_critical_branches': statistics.mean(critical_counts) if critical_counts else 0,
                'health_score_volatility': statistics.stdev(health_scores) if len(health_scores) > 1 else 0,
                'trend_data': trend_data
            }

            return analysis

    def calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 2:
            return "insufficient_data"

        # Simple linear trend
        n = len(values)
        x = list(range(n))
        y = values

        slope = statistics.linear_regression(x, y)[0]

        if slope > 0.5:
            return "improving"
        elif slope < -0.5:
            return "declining"
        else:
            return "stable"

    def generate_insights_report(self) -> Dict[str, Any]:
        """Generate comprehensive insights report."""
        historical = self.analyze_historical_patterns()
        trends = self.analyze_trends()

        insights = {
            'generated_at': datetime.now().isoformat(),
            'historical_analysis': historical,
            'trend_analysis': trends,
            'key_insights': []
        }

        # Generate key insights
        overall = historical['overall']

        if overall['conflict_rate'] > 0.3:
            insights['key_insights'].append({
                'type': 'warning',
                'title': 'High Conflict Rate',
                'description': f"{overall['conflict_rate']:.1%} of branches experience conflicts",
                'recommendation': 'Implement proactive rebase policies and conflict prevention training'
            })

        if trends.get('health_score_trend') == 'declining':
            insights['key_insights'].append({
                'type': 'warning',
                'title': 'Declining Branch Health',
                'description': 'Average branch health scores are trending downward',
                'recommendation': 'Review branch management practices and implement health monitoring alerts'
            })

        if overall['avg_resolution_hours'] and overall['avg_resolution_hours'] > 24:
            insights['key_insights'].append({
                'type': 'info',
                'title': 'Slow Conflict Resolution',
                'description': f'Average conflict resolution takes {overall["avg_resolution_hours"]:.1f} hours',
                'recommendation': 'Consider implementing automated conflict resolution tools'
            })

        return insights


def main():
    """Command-line interface for predictive analytics."""
    import argparse

    parser = argparse.ArgumentParser(description='HEE Predictive Analytics Engine')
    parser.add_argument('--analyze', action='store_true', help='Generate insights report')
    parser.add_argument('--trends', type=int, default=30, help='Analyze trends for N days')
    parser.add_argument('--predict', help='Predict conflicts for specific branch')
    parser.add_argument('--health-score', type=float, help='Current health score for prediction')
    parser.add_argument('--days-since-commit', type=int, help='Days since last commit')
    parser.add_argument('--commits-behind', type=int, help='Commits behind main')
    parser.add_argument('--has-pr', action='store_true', help='Branch has open PR')

    args = parser.parse_args()

    analytics = PredictiveAnalytics()

    if args.analyze:
        insights = analytics.generate_insights_report()
        print("🔍 HEE Predictive Analytics Insights Report")
        print("=" * 50)
        print(f"Generated: {insights['generated_at']}")
        print()

        overall = insights['historical_analysis']['overall']
        print("📊 Historical Overview:")
        print(".1f")
        print(".1f")
        print(f"  Total Historical Branches: {overall['total_historical_branches']}")
        print()

        trends = insights['trend_analysis']
        if 'error' not in trends:
            print("📈 Trend Analysis:")
            print(f"  Health Score Trend: {trends['health_score_trend']}")
            print(".1f")
            print(".2f")
            print()

        print("💡 Key Insights:")
        for insight in insights['key_insights']:
            emoji = "⚠️" if insight['type'] == 'warning' else "ℹ️"
            print(f"  {emoji} {insight['title']}: {insight['description']}")
            print(f"     → {insight['recommendation']}")
            print()

    elif args.predict and args.health_score is not None:
        if args.days_since_commit is None or args.commits_behind is None:
            print("Error: --days-since-commit and --commits-behind required for prediction")
            return

        prediction = analytics.predict_branch_conflicts(
            args.predict,
            args.health_score,
            args.days_since_commit,
            args.commits_behind,
            args.has_pr
        )

        print(f"🔮 Conflict Prediction for: {prediction.branch_name}")
        print("=" * 40)
        print(".1%")
        print(f"Risk Level: {prediction.risk_level.upper()}")
        print(".1f")
        print(f"Confidence: {prediction.confidence_score:.1%}")
        print()

        if prediction.predicted_resolution_time:
            print(f"Predicted Resolution Time: {prediction.predicted_resolution_time} hours")
            print()

        print("Contributing Factors:")
        for factor in prediction.contributing_factors:
            print(f"  • {factor.replace('_', ' ').title()}")
        print()

        print("Prevention Recommendations:")
        for rec in prediction.prevention_recommendations:
            print(f"  • {rec}")
        print()

    elif args.trends:
        trends = analytics.analyze_trends(args.trends)
        if 'error' in trends:
            print(f"Error: {trends['error']}")
        else:
            print(f"📈 Health Trends Analysis ({args.trends} days)")
            print("=" * 40)
            print(f"Data Points: {trends['data_points']}")
            print(f"Health Score Trend: {trends['health_score_trend']}")
            print(".1f")
            print(f"Average Critical Branches: {trends['average_critical_branches']:.1f}")
            print(".2f")


if __name__ == '__main__':
    main()
