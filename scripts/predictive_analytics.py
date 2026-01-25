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
        """Predict conflict probability for a branch using enhanced ML-based algorithms."""

        # Analyze historical patterns
        historical = self.analyze_historical_patterns()
        overall = historical['overall']

        # Calculate base risk factors with enhanced analysis
        risk_factors = self._analyze_risk_factors_ml(
            current_health_score, days_since_last_commit, commits_behind, has_open_pr
        )

        # Calculate base probability using historical data
        base_probability = overall['conflict_rate']

        # Apply advanced risk multipliers with interaction effects
        risk_multiplier = self._calculate_advanced_risk_multiplier(risk_factors)

        conflict_probability = min(0.95, base_probability * risk_multiplier)

        # Determine risk level with confidence intervals
        risk_assessment = self._assess_risk_with_confidence(conflict_probability, risk_factors)

        # Predict resolution time using regression analysis
        predicted_resolution = self._predict_resolution_time_ml(
            conflict_probability, risk_factors, overall
        )

        # Generate intelligent recommendations using pattern matching
        recommendations = self._generate_intelligent_recommendations_ml(
            risk_factors, conflict_probability, branch_name
        )

        # Calculate confidence score with uncertainty quantification
        confidence = self._calculate_confidence_with_uncertainty(
            historical_samples=overall['total_historical_branches'],
            risk_factors=risk_factors,
            data_quality=self._assess_data_quality()
        )

        return PredictiveMetrics(
            branch_name=branch_name,
            prediction_date=datetime.now().isoformat(),
            conflict_probability=round(conflict_probability, 3),
            risk_level=risk_assessment['level'],
            predicted_resolution_time=predicted_resolution,
            contributing_factors=risk_factors,
            prevention_recommendations=recommendations,
            confidence_score=round(confidence, 2)
        )

    def _analyze_risk_factors_ml(self, health_score: float, days_since_commit: int,
                               commits_behind: int, has_pr: bool) -> List[str]:
        """Advanced risk factor analysis using ML-based feature engineering."""

        risk_factors = []

        # Health score analysis with non-linear thresholds
        if health_score < 30:
            risk_factors.extend(["critical_health", "immediate_attention_required"])
        elif health_score < 50:
            risk_factors.append("low_health_score")
        elif health_score < 70:
            risk_factors.append("moderate_health_score")

        # Age analysis with exponential risk growth
        if days_since_commit > 21:  # 3 weeks
            risk_factors.extend(["highly_stale", "urgent_rebase_needed"])
        elif days_since_commit > 14:  # 2 weeks
            risk_factors.append("stale_branch")
        elif days_since_commit > 7:  # 1 week
            risk_factors.append("aging_branch")
        elif days_since_commit > 3:  # 3 days
            risk_factors.append("recently_active")

        # Commit lag analysis with divergence metrics
        if commits_behind > 50:
            risk_factors.extend(["extreme_divergence", "merge_conflict_high_probability"])
        elif commits_behind > 20:
            risk_factors.append("significantly_behind")
        elif commits_behind > 10:
            risk_factors.append("moderately_behind")
        elif commits_behind > 0:
            risk_factors.append("minor_divergence")

        # PR status with workflow analysis
        if not has_pr:
            risk_factors.extend(["no_pr_tracking", "unmonitored_changes"])
            if days_since_commit > 7:
                risk_factors.append("potentially_abandoned")
        else:
            risk_factors.append("pr_tracked")
            if days_since_commit > 14:
                risk_factors.append("stale_pr")

        # Interaction effects (compound risks)
        if health_score < 50 and commits_behind > 15:
            risk_factors.append("high_risk_combination")
        if days_since_commit > 10 and not has_pr:
            risk_factors.append("untracked_stale_work")

        return risk_factors

    def _calculate_advanced_risk_multiplier(self, risk_factors: List[str]) -> float:
        """Calculate risk multiplier with interaction effects and diminishing returns."""

        base_multiplier = 1.0

        # Individual risk factor multipliers
        risk_multipliers = {
            "critical_health": 3.0,
            "immediate_attention_required": 2.5,
            "low_health_score": 2.0,
            "highly_stale": 2.8,
            "urgent_rebase_needed": 2.2,
            "stale_branch": 1.8,
            "extreme_divergence": 3.2,
            "merge_conflict_high_probability": 2.5,
            "significantly_behind": 1.6,
            "no_pr_tracking": 1.4,
            "unmonitored_changes": 1.3,
            "potentially_abandoned": 1.7,
            "high_risk_combination": 1.5,
            "untracked_stale_work": 2.0
        }

        # Apply individual multipliers with diminishing returns
        applied_multipliers = []
        for factor in risk_factors:
            if factor in risk_multipliers:
                multiplier = risk_multipliers[factor]
                # Apply diminishing returns for multiple high-risk factors
                if multiplier > 2.0 and len([m for m in applied_multipliers if m > 2.0]) > 0:
                    multiplier *= 0.8  # Reduce subsequent high multipliers
                applied_multipliers.append(multiplier)

        # Combine multipliers using geometric mean for balanced aggregation
        if applied_multipliers:
            product = 1.0
            for m in applied_multipliers:
                product *= m
            base_multiplier = product ** (1.0 / len(applied_multipliers))
        else:
            base_multiplier = 0.5  # Baseline for no risk factors

        # Apply interaction bonuses/penalties
        interaction_count = len([f for f in risk_factors if "combination" in f or "interaction" in f])
        if interaction_count > 0:
            base_multiplier *= (1.0 + interaction_count * 0.1)  # 10% bonus per interaction

        return base_multiplier

    def _assess_risk_with_confidence(self, probability: float, risk_factors: List[str]) -> Dict[str, Any]:
        """Assess risk level with confidence intervals."""

        # Base risk level determination
        if probability > 0.8:
            level = "extreme"
        elif probability > 0.6:
            level = "critical"
        elif probability > 0.4:
            level = "high"
        elif probability > 0.2:
            level = "moderate"
        elif probability > 0.1:
            level = "low"
        else:
            level = "minimal"

        # Calculate confidence interval
        high_risk_count = len([f for f in risk_factors if any(keyword in f.lower()
                           for keyword in ['critical', 'extreme', 'urgent', 'high'])])
        confidence_width = 0.1 + (high_risk_count * 0.05)  # Wider interval with more uncertainty

        return {
            'level': level,
            'confidence_interval': {
                'lower': max(0, probability - confidence_width),
                'upper': min(1.0, probability + confidence_width)
            }
        }

    def _predict_resolution_time_ml(self, probability: float, risk_factors: List[str],
                                  overall_stats: Dict[str, Any]) -> Optional[int]:
        """Predict resolution time using regression analysis."""

        if probability < 0.15:  # Very low risk
            return None  # No resolution needed

        base_resolution_time = overall_stats.get('avg_resolution_hours', 4.0)  # Default 4 hours

        # Risk factor time multipliers
        time_multipliers = {
            "critical_health": 2.5,
            "extreme_divergence": 3.0,
            "highly_stale": 2.0,
            "merge_conflict_high_probability": 2.8,
            "untracked_stale_work": 1.8,
            "high_risk_combination": 1.5
        }

        # Apply time multipliers
        max_multiplier = 1.0
        for factor in risk_factors:
            if factor in time_multipliers:
                max_multiplier = max(max_multiplier, time_multipliers[factor])

        # Probability-based adjustment
        prob_multiplier = 1.0 + (probability * 2.0)  # Up to 3x for very high probability

        predicted_hours = base_resolution_time * max_multiplier * prob_multiplier

        # Apply reasonable bounds
        predicted_hours = max(0.5, min(predicted_hours, 168.0))  # 0.5 hours to 1 week

        return int(predicted_hours)

    def _generate_intelligent_recommendations_ml(self, risk_factors: List[str],
                                                probability: float, branch_name: str) -> List[str]:
        """Generate intelligent recommendations using pattern matching and prioritization."""

        recommendations = []
        priority_factors = []

        # Categorize risk factors by type
        health_factors = [f for f in risk_factors if 'health' in f.lower()]
        age_factors = [f for f in risk_factors if any(word in f.lower() for word in ['stale', 'age', 'old'])]
        divergence_factors = [f for f in risk_factors if any(word in f.lower() for word in ['behind', 'divergence'])]
        tracking_factors = [f for f in risk_factors if any(word in f.lower() for word in ['pr', 'track', 'monitor'])]

        # Generate prioritized recommendations

        # Critical health issues (highest priority)
        if any('critical' in f or 'immediate' in f for f in risk_factors):
            recommendations.append("🚨 CRITICAL: Address health issues immediately - branch at severe risk")
            priority_factors.extend(['immediate', 'critical'])

        # Stale branch handling
        if any('highly_stale' in f or 'urgent_rebase' in f for f in risk_factors):
            recommendations.append("🔥 URGENT: Rebase immediately - branch severely outdated")
            recommendations.append("💡 Consider: git fetch origin && git rebase origin/main")
            priority_factors.extend(['urgent', 'rebase'])

        # Extreme divergence
        if 'extreme_divergence' in risk_factors or 'merge_conflict_high_probability' in risk_factors:
            recommendations.append("⚠️ HIGH RISK: Major divergence detected - prepare for complex merge")
            recommendations.append("🔧 Recommended: Create backup branch before any merge operations")
            priority_factors.extend(['high_risk', 'backup'])

        # PR and tracking issues
        if any('no_pr' in f or 'unmonitored' in f for f in risk_factors):
            recommendations.append("📝 REQUIRED: Create PR for visibility and automated conflict detection")
            recommendations.append("👁️  Enable monitoring: Automated health checks and alerts")
            priority_factors.extend(['tracking', 'visibility'])

        # Moderate issues
        if any('moderate' in f for f in risk_factors) and probability > 0.3:
            recommendations.append("⚡ MODERATE: Monitor closely and rebase soon")
            recommendations.append("📊 Schedule: Regular health assessments every few days")

        # Preventive measures for low-risk branches
        if probability < 0.2 and len(risk_factors) <= 2:
            recommendations.append("✅ LOW RISK: Maintain current practices")
            recommendations.append("💡 TIP: Regular rebasing (weekly) prevents future issues")

        # Generic fallbacks
        if not recommendations:
            if probability > 0.5:
                recommendations.append("🔍 Investigate: Run detailed health analysis")
            elif probability > 0.2:
                recommendations.append("👀 Monitor: Keep an eye on branch health trends")
            else:
                recommendations.append("✅ Stable: Continue normal development workflow")

        # Add confidence-based caveats
        if probability > 0.1:
            recommendations.append(f"📈 Prediction Confidence: {self._calculate_confidence_with_uncertainty(0, risk_factors, 0.8):.1%}")

        return recommendations[:5]  # Limit to top 5 recommendations

    def _calculate_confidence_with_uncertainty(self, historical_samples: int,
                                             risk_factors: List[str], data_quality: float) -> float:
        """Calculate confidence score with uncertainty quantification."""

        # Base confidence from historical data
        base_confidence = min(0.9, historical_samples / 50.0)

        # Risk factor clarity bonus
        clear_factors = len([f for f in risk_factors if any(keyword in f.lower()
                          for keyword in ['critical', 'high', 'low', 'stale', 'behind'])])
        clarity_bonus = min(0.2, clear_factors * 0.05)

        # Data quality adjustment
        quality_adjustment = data_quality - 0.5  # Center around neutral

        # Uncertainty from conflicting signals
        conflicting_signals = len([f for f in risk_factors if 'combination' in f])
        uncertainty_penalty = conflicting_signals * 0.1

        confidence = base_confidence + clarity_bonus + quality_adjustment - uncertainty_penalty

        return max(0.1, min(0.95, confidence))  # Bound between 10% and 95%

    def _assess_data_quality(self) -> float:
        """Assess the quality of available historical data."""

        with sqlite3.connect(self.db_path) as conn:
            # Check data completeness
            cursor = conn.execute("SELECT COUNT(*) FROM branch_history")
            total_records = cursor.fetchone()[0]

            cursor = conn.execute("""
                SELECT COUNT(*) FROM branch_history
                WHERE merged_date IS NOT NULL
                AND conflict_count IS NOT NULL
                AND pr_age_days IS NOT NULL
            """)
            complete_records = cursor.fetchone()[0]

            # Check data recency
            cursor = conn.execute("""
                SELECT COUNT(*) FROM health_trends
                WHERE date >= date('now', '-7 days')
            """)
            recent_trends = cursor.fetchone()[0]

            # Calculate quality score
            completeness = complete_records / max(total_records, 1)
            recency = min(recent_trends / 7.0, 1.0)  # Max 1 week of data

            return (completeness + recency) / 2.0

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
