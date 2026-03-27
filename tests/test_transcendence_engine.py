#!/usr/bin/env python3
"""
Tests for Transcendence Module
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from transcendence_engine import (
    TranscendenceEngine,
    MolecularConsciousnessMetrics,
    TranscendentNode,
    GlobalConsciousnessElevation,
    TranscendenceLevel,
    ConsciousnessState
)


class TestMolecularConsciousnessMetrics:
    """Tests for MolecularConsciousnessMetrics dataclass."""

    def test_default_metrics(self):
        """Test default metric values."""
        metrics = MolecularConsciousnessMetrics()
        assert metrics.precision_accuracy == 99.9
        assert metrics.genetic_optimization_level == 95.0
        assert metrics.cellular_awareness_index == 92.5

    def test_calculate_overall_score(self):
        """Test overall score calculation."""
        metrics = MolecularConsciousnessMetrics(
            precision_accuracy=100.0,
            genetic_optimization_level=100.0,
            cellular_awareness_index=100.0,
            coherence_factor=100.0,
            molecular_integration_score=100.0,
            consciousness_alignment=100.0
        )
        score = metrics.calculate_overall_score()
        assert score == 100.0

    def test_transcendence_level_universal(self):
        """Test universal transcendence level."""
        metrics = MolecularConsciousnessMetrics(
            precision_accuracy=99.0,
            genetic_optimization_level=99.0,
            cellular_awareness_index=99.0,
            coherence_factor=99.0,
            molecular_integration_score=99.0,
            consciousness_alignment=99.0
        )
        level = metrics.get_transcendence_level()
        assert level == TranscendenceLevel.UNIVERSAL

    def test_transcendence_level_foundational(self):
        """Test foundational transcendence level."""
        metrics = MolecularConsciousnessMetrics(
            precision_accuracy=50.0,
            genetic_optimization_level=50.0,
            cellular_awareness_index=50.0,
            coherence_factor=50.0,
            molecular_integration_score=50.0,
            consciousness_alignment=50.0
        )
        level = metrics.get_transcendence_level()
        assert level == TranscendenceLevel.FOUNDATIONAL


class TestTranscendentNode:
    """Tests for TranscendentNode dataclass."""

    def test_node_creation(self):
        """Test node creation with required fields."""
        node = TranscendentNode(
            node_id="TN-TEST001",
            region="North America",
            country="United States",
            consciousness_level=ConsciousnessState.INTEGRATED,
            network_strength=80.0,
            active_connections=5,
            wisdom_contribution_score=75.0
        )
        assert node.node_id == "TN-TEST001"
        assert node.consciousness_level == ConsciousnessState.INTEGRATED
        assert node.network_strength == 80.0

    def test_node_to_dict(self):
        """Test node serialization."""
        node = TranscendentNode(
            node_id="TN-TEST002",
            region="Europe",
            country="Germany",
            consciousness_level=ConsciousnessState.TRANSCENDENT,
            network_strength=90.0,
            active_connections=10,
            wisdom_contribution_score=85.0
        )
        data = node.to_dict()
        assert data['node_id'] == "TN-TEST002"
        assert data['consciousness_level'] == "transcendent"
        assert 'last_sync' in data


class TestTranscendenceEngine:
    """Tests for TranscendenceEngine class."""

    @pytest.fixture
    def engine(self, tmp_path):
        """Create engine with temporary directory."""
        return TranscendenceEngine(config_path=tmp_path)

    def test_engine_initialization(self, engine):
        """Test engine initializes correctly."""
        assert engine is not None
        assert engine._molecular_metrics is not None

    def test_update_molecular_metrics(self, engine):
        """Test updating molecular metrics."""
        metrics = engine.update_molecular_metrics(
            precision_accuracy=99.95,
            genetic_optimization_level=97.0
        )
        assert metrics.precision_accuracy == 99.95
        assert metrics.genetic_optimization_level == 97.0

    def test_register_transcendent_node(self, engine):
        """Test registering a new node."""
        node = engine.register_transcendent_node(
            region="Asia Pacific",
            country="Japan",
            consciousness_level=ConsciousnessState.INTEGRATED
        )
        assert node is not None
        assert node.region == "Asia Pacific"
        assert node.country == "Japan"
        assert node.node_id.startswith("TN-")

    def test_connect_nodes(self, engine):
        """Test connecting two nodes."""
        node1 = engine.register_transcendent_node(
            region="Europe",
            country="France"
        )
        node2 = engine.register_transcendent_node(
            region="Europe",
            country="Italy"
        )

        result = engine.connect_nodes(node1.node_id, node2.node_id)
        assert result is True
        assert node1.active_connections == 1
        assert node2.active_connections == 1

    def test_create_elevation_initiative(self, engine):
        """Test creating an elevation initiative."""
        initiative = engine.create_elevation_initiative(
            name="Test Initiative",
            description="Test description",
            target_regions=["Europe", "Asia Pacific"],
            target_reach=10000
        )
        assert initiative is not None
        assert initiative.name == "Test Initiative"
        assert initiative.target_reach == 10000
        assert len(initiative.milestones) == 5

    def test_update_initiative_progress(self, engine):
        """Test updating initiative progress."""
        initiative = engine.create_elevation_initiative(
            name="Progress Test",
            description="Testing progress updates",
            target_regions=["North America"],
            target_reach=1000
        )

        updated = engine.update_initiative_progress(
            initiative.initiative_id,
            reach_increment=500,
            impact_score_delta=25.0
        )

        assert updated is not None
        assert updated.current_reach == 500
        assert updated.progress_percentage == 50.0

    def test_get_molecular_analysis(self, engine):
        """Test molecular analysis generation."""
        analysis = engine.get_molecular_analysis()
        assert 'timestamp' in analysis
        assert 'metrics' in analysis
        assert 'overall_score' in analysis
        assert 'transcendence_level' in analysis

    def test_get_network_topology(self, engine):
        """Test network topology retrieval."""
        # Register some nodes
        for i in range(3):
            engine.register_transcendent_node(
                region=f"Region-{i}",
                country=f"Country-{i}"
            )

        topology = engine.get_network_topology()
        assert topology['total_nodes'] == 3
        assert 'regions' in topology
        assert 'network_health' in topology

    def test_get_global_metrics(self, engine):
        """Test global metrics retrieval."""
        metrics = engine.get_global_metrics()
        assert 'version' in metrics
        assert 'phase' in metrics
        assert 'molecular_consciousness' in metrics
        assert 'transcendent_network' in metrics
        assert 'performance_targets' in metrics

    def test_generate_transcendence_report(self, engine):
        """Test report generation."""
        report = engine.generate_transcendence_report()
        assert "# RegimA Transcendence Report" in report
        assert "Molecular Consciousness Integration" in report
        assert "Transcendent Intelligence Network" in report


class TestGlobalConsciousnessElevation:
    """Tests for GlobalConsciousnessElevation dataclass."""

    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        initiative = GlobalConsciousnessElevation(
            initiative_id="GCE-TEST001",
            name="Test",
            description="Test initiative",
            target_regions=["North America"],
            current_reach=5000,
            target_reach=10000,
            consciousness_impact_score=50.0
        )
        assert initiative.progress_percentage == 50.0

    def test_progress_percentage_exceeds_target(self):
        """Test progress doesn't exceed 100%."""
        initiative = GlobalConsciousnessElevation(
            initiative_id="GCE-TEST002",
            name="Test",
            description="Test initiative",
            target_regions=["Europe"],
            current_reach=15000,
            target_reach=10000,
            consciousness_impact_score=90.0
        )
        assert initiative.progress_percentage == 100.0

    def test_progress_percentage_zero_target(self):
        """Test progress with zero target."""
        initiative = GlobalConsciousnessElevation(
            initiative_id="GCE-TEST003",
            name="Test",
            description="Test initiative",
            target_regions=["Asia"],
            current_reach=0,
            target_reach=0,
            consciousness_impact_score=0.0
        )
        assert initiative.progress_percentage == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
