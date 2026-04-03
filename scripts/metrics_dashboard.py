#!/usr/bin/env python3
"""
RegimA Metrics Dashboard - Phase 3 Implementation

This module provides a comprehensive metrics dashboard for tracking
advanced transcendence progress, organizational consciousness evolution,
and global network performance.
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    """Categories of metrics tracked."""
    MOLECULAR_PRECISION = "molecular_precision"
    CONSCIOUSNESS_EVOLUTION = "consciousness_evolution"
    NETWORK_PERFORMANCE = "network_performance"
    LEARNING_PLATFORM = "learning_platform"
    INNOVATION_INDEX = "innovation_index"
    GLOBAL_REACH = "global_reach"
    PHASE_PROGRESS = "phase_progress"


class TrendDirection(Enum):
    """Trend direction indicators."""
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Represents a tracked metric."""
    metric_id: str
    name: str
    category: MetricCategory
    current_value: float
    target_value: float
    unit: str
    description: str
    trend: TrendDirection = TrendDirection.STABLE
    history: List[Dict[str, Any]] = field(default_factory=list)
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def progress_percentage(self) -> float:
        if self.target_value == 0:
            return 0.0
        return min(100.0, (self.current_value / self.target_value) * 100)

    @property
    def status(self) -> str:
        if self.progress_percentage >= 100:
            return "achieved"
        elif self.progress_percentage >= 80:
            return "on_track"
        elif self.progress_percentage >= 50:
            return "in_progress"
        return "needs_attention"

    def add_history_point(self, value: float):
        self.history.append({
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        # Keep last 100 points
        if len(self.history) > 100:
            self.history = self.history[-100:]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "category": self.category.value,
            "current_value": self.current_value,
            "target_value": self.target_value,
            "unit": self.unit,
            "description": self.description,
            "trend": self.trend.value,
            "progress_percentage": round(self.progress_percentage, 2),
            "status": self.status,
            "history": self.history[-10:],  # Last 10 points for display
            "last_updated": self.last_updated
        }


@dataclass
class Alert:
    """Represents a system alert."""
    alert_id: str
    level: AlertLevel
    category: MetricCategory
    title: str
    message: str
    metric_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class DashboardWidget:
    """Represents a dashboard widget configuration."""
    widget_id: str
    widget_type: str  # gauge, chart, table, kpi, heatmap
    title: str
    metrics: List[str]
    position: Dict[str, int]  # x, y, width, height
    refresh_interval: int = 60  # seconds
    config: Dict[str, Any] = field(default_factory=dict)


class MetricsDashboard:
    """
    Comprehensive metrics dashboard for RegimA Phase 3.

    Features:
    - Real-time metric tracking
    - Trend analysis and forecasting
    - Alert management
    - Historical data visualization
    - Customizable widgets
    - Executive reporting
    """

    def __init__(self, data_path: Optional[Path] = None):
        self.base_path = Path(__file__).parent.parent
        self.data_path = data_path or self.base_path / "data"
        self.outputs_path = self.base_path / "outputs"

        self.data_path.mkdir(exist_ok=True)
        self.outputs_path.mkdir(exist_ok=True)

        # State
        self._metrics: Dict[str, Metric] = {}
        self._alerts: List[Alert] = []
        self._widgets: Dict[str, DashboardWidget] = {}

        # Load state
        self._load_state()

        # Initialize default metrics if empty
        if not self._metrics:
            self._initialize_default_metrics()

        logger.info("MetricsDashboard initialized")

    def _load_state(self) -> None:
        """Load dashboard state from files."""
        state_file = self.data_path / "dashboard_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    self._restore_state(state)
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Could not load dashboard state: {e}")

    def _restore_state(self, state: Dict[str, Any]) -> None:
        """Restore state from dictionary."""
        for metric_data in state.get('metrics', []):
            metric_data['category'] = MetricCategory(metric_data['category'])
            metric_data['trend'] = TrendDirection(metric_data['trend'])
            metric = Metric(**metric_data)
            self._metrics[metric.metric_id] = metric

    def save_state(self) -> None:
        """Persist dashboard state."""
        state = {
            'version': '3.1.0',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': [
                {**m.to_dict(), 'history': m.history}
                for m in self._metrics.values()
            ],
            'alerts': [asdict(a) for a in self._alerts[-100:]],
            'summary': self.get_executive_summary()
        }

        state_file = self.data_path / "dashboard_state.json"
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)

        logger.info("Dashboard state saved")

    def _initialize_default_metrics(self) -> None:
        """Initialize default Phase 3 metrics."""
        metrics = [
            # Molecular Precision Metrics
            Metric(
                metric_id="MP-001",
                name="Biomarker Analysis Accuracy",
                category=MetricCategory.MOLECULAR_PRECISION,
                current_value=99.9,
                target_value=99.95,
                unit="%",
                description="Accuracy of molecular biomarker analysis",
                trend=TrendDirection.RISING,
                threshold_warning=99.5,
                threshold_critical=99.0
            ),
            Metric(
                metric_id="MP-002",
                name="Genetic Optimization Level",
                category=MetricCategory.MOLECULAR_PRECISION,
                current_value=95.0,
                target_value=98.0,
                unit="%",
                description="Level of genetic optimization in treatments",
                trend=TrendDirection.RISING
            ),
            Metric(
                metric_id="MP-003",
                name="Cellular Awareness Index",
                category=MetricCategory.MOLECULAR_PRECISION,
                current_value=92.5,
                target_value=97.0,
                unit="%",
                description="Depth of cellular-level awareness",
                trend=TrendDirection.STABLE
            ),

            # Consciousness Evolution Metrics
            Metric(
                metric_id="CE-001",
                name="Global Consciousness Index",
                category=MetricCategory.CONSCIOUSNESS_EVOLUTION,
                current_value=78.0,
                target_value=100.0,
                unit="%",
                description="Overall global consciousness penetration",
                trend=TrendDirection.RISING
            ),
            Metric(
                metric_id="CE-002",
                name="Transcendent Practitioners",
                category=MetricCategory.CONSCIOUSNESS_EVOLUTION,
                current_value=2450,
                target_value=5000,
                unit="practitioners",
                description="Number of practitioners at transcendent level"
            ),
            Metric(
                metric_id="CE-003",
                name="Consciousness Coherence Score",
                category=MetricCategory.CONSCIOUSNESS_EVOLUTION,
                current_value=87.0,
                target_value=95.0,
                unit="%",
                description="Network-wide consciousness coherence"
            ),

            # Network Performance Metrics
            Metric(
                metric_id="NP-001",
                name="Active Network Nodes",
                category=MetricCategory.NETWORK_PERFORMANCE,
                current_value=127,
                target_value=150,
                unit="nodes",
                description="Number of active transcendent network nodes",
                trend=TrendDirection.RISING,
                threshold_warning=100,
                threshold_critical=50
            ),
            Metric(
                metric_id="NP-002",
                name="Network Health Score",
                category=MetricCategory.NETWORK_PERFORMANCE,
                current_value=85.0,
                target_value=95.0,
                unit="%",
                description="Overall network health and stability"
            ),
            Metric(
                metric_id="NP-003",
                name="Wisdom Distribution Rate",
                category=MetricCategory.NETWORK_PERFORMANCE,
                current_value=1250,
                target_value=2000,
                unit="packets/day",
                description="Rate of wisdom packet distribution"
            ),

            # Learning Platform Metrics
            Metric(
                metric_id="LP-001",
                name="Active Learners",
                category=MetricCategory.LEARNING_PLATFORM,
                current_value=3500,
                target_value=10000,
                unit="learners",
                description="Number of active learners on platform"
            ),
            Metric(
                metric_id="LP-002",
                name="Certifications Issued",
                category=MetricCategory.LEARNING_PLATFORM,
                current_value=850,
                target_value=2500,
                unit="certifications",
                description="Total professional certifications issued"
            ),
            Metric(
                metric_id="LP-003",
                name="Average Consciousness Score",
                category=MetricCategory.LEARNING_PLATFORM,
                current_value=72.5,
                target_value=85.0,
                unit="%",
                description="Average learner consciousness development score"
            ),

            # Innovation Index Metrics
            Metric(
                metric_id="II-001",
                name="Advanced Innovation Index",
                category=MetricCategory.INNOVATION_INDEX,
                current_value=82.0,
                target_value=95.0,
                unit="%",
                description="Overall advanced innovation capability"
            ),
            Metric(
                metric_id="II-002",
                name="Breakthrough Research Projects",
                category=MetricCategory.INNOVATION_INDEX,
                current_value=15,
                target_value=25,
                unit="projects",
                description="Active breakthrough research initiatives"
            ),

            # Global Reach Metrics
            Metric(
                metric_id="GR-001",
                name="Countries with Presence",
                category=MetricCategory.GLOBAL_REACH,
                current_value=127,
                target_value=150,
                unit="countries",
                description="Number of countries with RegimA presence",
                trend=TrendDirection.RISING
            ),
            Metric(
                metric_id="GR-002",
                name="Protocol Adoption Rate",
                category=MetricCategory.GLOBAL_REACH,
                current_value=85.0,
                target_value=95.0,
                unit="%",
                description="Industry-wide protocol adoption percentage"
            ),

            # Phase Progress Metrics
            Metric(
                metric_id="PP-001",
                name="Phase 3 Completion",
                category=MetricCategory.PHASE_PROGRESS,
                current_value=65.0,
                target_value=100.0,
                unit="%",
                description="Overall Phase 3 completion percentage",
                trend=TrendDirection.RISING
            ),
            Metric(
                metric_id="PP-002",
                name="Phase 4 Readiness",
                category=MetricCategory.PHASE_PROGRESS,
                current_value=35.0,
                target_value=80.0,
                unit="%",
                description="Readiness for Phase 4 evolution"
            )
        ]

        for metric in metrics:
            self._metrics[metric.metric_id] = metric
            # Add some historical data points
            for i in range(10):
                variation = (i - 5) * 0.5
                metric.add_history_point(metric.current_value + variation)

        logger.info(f"Initialized {len(metrics)} default metrics")

    # =========================================================================
    # Metric Management
    # =========================================================================

    def update_metric(
        self,
        metric_id: str,
        value: float,
        update_trend: bool = True
    ) -> Optional[Metric]:
        """Update a metric value."""
        if metric_id not in self._metrics:
            logger.warning(f"Metric not found: {metric_id}")
            return None

        metric = self._metrics[metric_id]
        old_value = metric.current_value
        metric.current_value = value
        metric.add_history_point(value)
        metric.last_updated = datetime.now(timezone.utc).isoformat()

        if update_trend:
            if value > old_value * 1.01:
                metric.trend = TrendDirection.RISING
            elif value < old_value * 0.99:
                metric.trend = TrendDirection.DECLINING
            else:
                metric.trend = TrendDirection.STABLE

        # Check thresholds and create alerts
        self._check_metric_thresholds(metric)

        logger.info(f"Updated metric {metric_id}: {old_value} -> {value}")
        return metric

    def _check_metric_thresholds(self, metric: Metric) -> None:
        """Check metric thresholds and create alerts if needed."""
        if metric.threshold_critical and metric.current_value < metric.threshold_critical:
            self.create_alert(
                level=AlertLevel.CRITICAL,
                category=metric.category,
                title=f"Critical: {metric.name}",
                message=f"{metric.name} has fallen below critical threshold ({metric.current_value} < {metric.threshold_critical})",
                metric_id=metric.metric_id
            )
        elif metric.threshold_warning and metric.current_value < metric.threshold_warning:
            self.create_alert(
                level=AlertLevel.WARNING,
                category=metric.category,
                title=f"Warning: {metric.name}",
                message=f"{metric.name} is below warning threshold ({metric.current_value} < {metric.threshold_warning})",
                metric_id=metric.metric_id
            )

    def get_metric(self, metric_id: str) -> Optional[Metric]:
        """Get a specific metric."""
        return self._metrics.get(metric_id)

    def get_metrics_by_category(self, category: MetricCategory) -> List[Metric]:
        """Get all metrics in a category."""
        return [m for m in self._metrics.values() if m.category == category]

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all metrics organized by category."""
        result = {}
        for category in MetricCategory:
            result[category.value] = [
                m.to_dict() for m in self.get_metrics_by_category(category)
            ]
        return result

    # =========================================================================
    # Alert Management
    # =========================================================================

    def create_alert(
        self,
        level: AlertLevel,
        category: MetricCategory,
        title: str,
        message: str,
        metric_id: Optional[str] = None
    ) -> Alert:
        """Create a new alert."""
        import uuid
        alert = Alert(
            alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
            level=level,
            category=category,
            title=title,
            message=message,
            metric_id=metric_id
        )
        self._alerts.append(alert)
        logger.info(f"Created alert: {title} ({level.value})")
        return alert

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                return True
        return False

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active (unresolved) alerts."""
        return [
            asdict(a) for a in self._alerts
            if not a.resolved
        ]

    # =========================================================================
    # Dashboard Views
    # =========================================================================

    def get_executive_summary(self) -> Dict[str, Any]:
        """Get executive summary of all metrics."""
        categories_summary = {}
        for category in MetricCategory:
            metrics = self.get_metrics_by_category(category)
            if metrics:
                avg_progress = sum(m.progress_percentage for m in metrics) / len(metrics)
                on_target = sum(1 for m in metrics if m.progress_percentage >= 80)
                categories_summary[category.value] = {
                    "average_progress": round(avg_progress, 2),
                    "metrics_on_target": on_target,
                    "total_metrics": len(metrics),
                    "status": "on_track" if avg_progress >= 80 else "needs_attention"
                }

        # Key performance indicators
        kpis = {
            "molecular_precision": self._metrics.get("MP-001", Metric(
                metric_id="", name="", category=MetricCategory.MOLECULAR_PRECISION,
                current_value=0, target_value=100, unit="", description=""
            )).current_value,
            "countries_covered": self._metrics.get("GR-001", Metric(
                metric_id="", name="", category=MetricCategory.GLOBAL_REACH,
                current_value=0, target_value=150, unit="", description=""
            )).current_value,
            "protocol_adoption": self._metrics.get("GR-002", Metric(
                metric_id="", name="", category=MetricCategory.GLOBAL_REACH,
                current_value=0, target_value=95, unit="", description=""
            )).current_value,
            "phase_completion": self._metrics.get("PP-001", Metric(
                metric_id="", name="", category=MetricCategory.PHASE_PROGRESS,
                current_value=0, target_value=100, unit="", description=""
            )).current_value
        }

        active_alerts = self.get_active_alerts()
        critical_alerts = sum(1 for a in active_alerts if a.get('level') == 'critical')

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_health": self._calculate_overall_health(),
            "kpis": kpis,
            "categories": categories_summary,
            "alerts": {
                "total_active": len(active_alerts),
                "critical": critical_alerts
            },
            "phase": "Advanced Transcendence (Phase 3)"
        }

    def _calculate_overall_health(self) -> float:
        """Calculate overall system health score."""
        if not self._metrics:
            return 0.0

        # Weight different categories
        weights = {
            MetricCategory.MOLECULAR_PRECISION: 0.25,
            MetricCategory.CONSCIOUSNESS_EVOLUTION: 0.20,
            MetricCategory.NETWORK_PERFORMANCE: 0.20,
            MetricCategory.LEARNING_PLATFORM: 0.10,
            MetricCategory.INNOVATION_INDEX: 0.10,
            MetricCategory.GLOBAL_REACH: 0.10,
            MetricCategory.PHASE_PROGRESS: 0.05
        }

        total_score = 0.0
        for category, weight in weights.items():
            metrics = self.get_metrics_by_category(category)
            if metrics:
                avg_progress = sum(m.progress_percentage for m in metrics) / len(metrics)
                total_score += avg_progress * weight

        return round(total_score, 2)

    def get_category_dashboard(self, category: MetricCategory) -> Dict[str, Any]:
        """Get dashboard data for a specific category."""
        metrics = self.get_metrics_by_category(category)

        if not metrics:
            return {"error": "No metrics found for category"}

        return {
            "category": category.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_metrics": len(metrics),
                "on_target": sum(1 for m in metrics if m.progress_percentage >= 80),
                "needs_attention": sum(1 for m in metrics if m.progress_percentage < 60),
                "average_progress": round(
                    sum(m.progress_percentage for m in metrics) / len(metrics), 2
                )
            },
            "metrics": [m.to_dict() for m in metrics],
            "trends": {
                "rising": sum(1 for m in metrics if m.trend == TrendDirection.RISING),
                "stable": sum(1 for m in metrics if m.trend == TrendDirection.STABLE),
                "declining": sum(1 for m in metrics if m.trend == TrendDirection.DECLINING)
            }
        }

    def get_phase_progress_dashboard(self) -> Dict[str, Any]:
        """Get Phase 3 progress dashboard."""
        # Calculate phase milestones
        milestones = [
            {
                "name": "Molecular Consciousness Integration",
                "target": "Expand molecular awareness capabilities",
                "progress": self._metrics.get("MP-001", Metric(
                    metric_id="", name="", category=MetricCategory.MOLECULAR_PRECISION,
                    current_value=99.9, target_value=99.95, unit="", description=""
                )).progress_percentage,
                "status": "in_progress"
            },
            {
                "name": "Transcendent Network Development",
                "target": "150 countries with active nodes",
                "progress": self._metrics.get("GR-001", Metric(
                    metric_id="", name="", category=MetricCategory.GLOBAL_REACH,
                    current_value=127, target_value=150, unit="", description=""
                )).progress_percentage,
                "status": "in_progress"
            },
            {
                "name": "Global Consciousness Elevation",
                "target": "95% protocol adoption",
                "progress": self._metrics.get("GR-002", Metric(
                    metric_id="", name="", category=MetricCategory.GLOBAL_REACH,
                    current_value=85, target_value=95, unit="", description=""
                )).progress_percentage,
                "status": "in_progress"
            },
            {
                "name": "Innovation Ecosystem Leadership",
                "target": "95% innovation index",
                "progress": self._metrics.get("II-001", Metric(
                    metric_id="", name="", category=MetricCategory.INNOVATION_INDEX,
                    current_value=82, target_value=95, unit="", description=""
                )).progress_percentage,
                "status": "in_progress"
            }
        ]

        for milestone in milestones:
            if milestone["progress"] >= 100:
                milestone["status"] = "completed"
            elif milestone["progress"] >= 80:
                milestone["status"] = "on_track"
            elif milestone["progress"] < 50:
                milestone["status"] = "needs_attention"

        phase_completion = sum(m["progress"] for m in milestones) / len(milestones)

        return {
            "phase": "Phase 3: Advanced Transcendence",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_completion": round(phase_completion, 2),
            "milestones": milestones,
            "next_phase_readiness": self._metrics.get("PP-002", Metric(
                metric_id="", name="", category=MetricCategory.PHASE_PROGRESS,
                current_value=35, target_value=80, unit="", description=""
            )).progress_percentage,
            "estimated_completion": self._estimate_phase_completion(phase_completion)
        }

    def _estimate_phase_completion(self, current_progress: float) -> str:
        """Estimate phase completion based on current progress and trends."""
        if current_progress >= 95:
            return "Imminent (< 1 month)"
        elif current_progress >= 80:
            return "Near-term (1-3 months)"
        elif current_progress >= 60:
            return "Medium-term (3-6 months)"
        return "Long-term (6+ months)"

    # =========================================================================
    # Reporting
    # =========================================================================

    def generate_dashboard_report(self) -> str:
        """Generate comprehensive dashboard report in Markdown."""
        summary = self.get_executive_summary()
        phase = self.get_phase_progress_dashboard()

        report = f"""# RegimA Metrics Dashboard Report

**Generated:** {summary['timestamp']}
**Phase:** {summary['phase']}

---

## Executive Summary

**Overall Health Score:** {summary['overall_health']:.1f}%

### Key Performance Indicators

| KPI | Current | Target | Status |
|-----|---------|--------|--------|
| Molecular Precision | {summary['kpis']['molecular_precision']:.2f}% | 99.95% | {'✅' if summary['kpis']['molecular_precision'] >= 99.95 else '🔄'} |
| Countries Covered | {int(summary['kpis']['countries_covered'])} | 150 | {'✅' if summary['kpis']['countries_covered'] >= 150 else '🔄'} |
| Protocol Adoption | {summary['kpis']['protocol_adoption']:.1f}% | 95% | {'✅' if summary['kpis']['protocol_adoption'] >= 95 else '🔄'} |
| Phase Completion | {summary['kpis']['phase_completion']:.1f}% | 100% | {'✅' if summary['kpis']['phase_completion'] >= 100 else '🔄'} |

### Active Alerts
- **Total Active:** {summary['alerts']['total_active']}
- **Critical:** {summary['alerts']['critical']}

---

## Phase 3 Progress

**Overall Completion:** {phase['overall_completion']:.1f}%
**Estimated Completion:** {phase['estimated_completion']}
**Phase 4 Readiness:** {phase['next_phase_readiness']:.1f}%

### Milestones

"""
        for milestone in phase['milestones']:
            status_icon = "✅" if milestone['status'] == 'completed' else "🔄" if milestone['status'] == 'on_track' else "⚠️"
            report += f"""
#### {milestone['name']} {status_icon}
- Target: {milestone['target']}
- Progress: {milestone['progress']:.1f}%
- Status: {milestone['status'].replace('_', ' ').title()}
"""

        report += """
---

## Category Performance

"""
        for category, data in summary['categories'].items():
            status_icon = "✅" if data['status'] == 'on_track' else "⚠️"
            report += f"""
### {category.replace('_', ' ').title()} {status_icon}
- Average Progress: {data['average_progress']:.1f}%
- Metrics On Target: {data['metrics_on_target']}/{data['total_metrics']}
"""

        # Detailed metrics by category
        report += """
---

## Detailed Metrics

"""
        for category in MetricCategory:
            dashboard = self.get_category_dashboard(category)
            if 'error' not in dashboard:
                report += f"""
### {category.value.replace('_', ' ').title()}

| Metric | Current | Target | Progress | Trend |
|--------|---------|--------|----------|-------|
"""
                for m in dashboard['metrics']:
                    trend_icon = "📈" if m['trend'] == 'rising' else "📉" if m['trend'] == 'declining' else "➡️"
                    report += f"| {m['name']} | {m['current_value']} {m['unit']} | {m['target_value']} {m['unit']} | {m['progress_percentage']:.1f}% | {trend_icon} |\n"

        report += f"""
---

## Alerts

"""
        active_alerts = self.get_active_alerts()
        if active_alerts:
            for alert in active_alerts[:10]:
                level_icon = "🔴" if alert['level'] == 'critical' else "🟡" if alert['level'] == 'warning' else "🔵"
                report += f"""
### {level_icon} {alert['title']}
- Level: {alert['level'].title()}
- Category: {alert['category'].replace('_', ' ').title()}
- Message: {alert['message']}
- Created: {alert['created_at']}
"""
        else:
            report += "No active alerts.\n"

        report += """
---

## Recommendations

1. Continue monitoring molecular precision to reach 99.95% target
2. Accelerate network expansion to achieve 150 countries goal
3. Enhance protocol adoption through additional training programs
4. Increase innovation index through breakthrough research initiatives
5. Prepare Phase 4 infrastructure for upcoming evolution

---

*Report generated by RegimA Metrics Dashboard v3.1.0*
"""
        return report


def main():
    """Main entry point for Metrics Dashboard."""
    dashboard = MetricsDashboard()

    # Generate and save report
    report = dashboard.generate_dashboard_report()

    output_file = dashboard.outputs_path / f"dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(output_file, 'w') as f:
        f.write(report)

    # Save state
    dashboard.save_state()

    # Print summary
    summary = dashboard.get_executive_summary()
    print("\n" + "=" * 60)
    print("RegimA Metrics Dashboard")
    print("=" * 60)
    print(f"\nOverall Health: {summary['overall_health']:.1f}%")
    print(f"Phase: {summary['phase']}")
    print(f"\nKey Metrics:")
    print(f"  Molecular Precision: {summary['kpis']['molecular_precision']:.2f}%")
    print(f"  Countries: {int(summary['kpis']['countries_covered'])}")
    print(f"  Protocol Adoption: {summary['kpis']['protocol_adoption']:.1f}%")
    print(f"  Phase Completion: {summary['kpis']['phase_completion']:.1f}%")
    print(f"\nActive Alerts: {summary['alerts']['total_active']}")
    print(f"Critical Alerts: {summary['alerts']['critical']}")
    print(f"\nReport saved to: {output_file}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
