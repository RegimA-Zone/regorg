#!/usr/bin/env python3
"""
Tests for Transcendent Learning Platform
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from transcendent_learning import (
    TranscendentLearningPlatform,
    LearningModule,
    LearnerProfile,
    Certification,
    LearningPath,
    LearningDomain,
    CompetencyLevel,
    CertificationType
)


class TestLearningModule:
    """Tests for LearningModule dataclass."""

    def test_module_creation(self):
        """Test module creation with required fields."""
        module = LearningModule(
            module_id="TEST-101",
            title="Test Module",
            domain=LearningDomain.ZONE_CONCEPT,
            description="A test module"
        )
        assert module.module_id == "TEST-101"
        assert module.domain == LearningDomain.ZONE_CONCEPT
        assert module.duration_hours == 2.0  # Default

    def test_module_to_dict(self):
        """Test module serialization."""
        module = LearningModule(
            module_id="TEST-102",
            title="Test Module 2",
            domain=LearningDomain.MOLECULAR_PRECISION,
            description="Another test module",
            competency_points=200
        )
        data = module.to_dict()
        assert data['module_id'] == "TEST-102"
        assert data['domain'] == "molecular_precision"
        assert data['competency_points'] == 200


class TestLearnerProfile:
    """Tests for LearnerProfile dataclass."""

    def test_learner_creation(self):
        """Test learner profile creation."""
        learner = LearnerProfile(
            learner_id="LRN-TEST001",
            name="Test User",
            email="test@example.com",
            region="North America",
            country="United States"
        )
        assert learner.learner_id == "LRN-TEST001"
        assert learner.current_level == CompetencyLevel.NOVICE
        assert learner.total_competency_points == 0

    def test_learner_to_dict(self):
        """Test learner serialization."""
        learner = LearnerProfile(
            learner_id="LRN-TEST002",
            name="Test User 2",
            email="test2@example.com",
            region="Europe",
            country="Germany",
            current_level=CompetencyLevel.SPECIALIST
        )
        data = learner.to_dict()
        assert data['learner_id'] == "LRN-TEST002"
        assert data['current_level'] == "specialist"


class TestCertification:
    """Tests for Certification dataclass."""

    def test_certification_creation(self):
        """Test certification creation."""
        cert = Certification(
            cert_id="CERT-TEST001",
            cert_type=CertificationType.ZONE_CONCEPT_PRACTITIONER,
            learner_id="LRN-001",
            learner_name="Test User",
            issued_at="2026-01-01T00:00:00Z",
            expires_at="2028-01-01T00:00:00Z",
            verification_hash="abc123"
        )
        assert cert.cert_type == CertificationType.ZONE_CONCEPT_PRACTITIONER
        assert cert.valid is True

    def test_certification_verification(self):
        """Test certification verification."""
        # Create cert with proper hash
        import hashlib
        cert_id = "CERT-TEST002"
        learner_id = "LRN-002"
        issued_at = "2026-01-01T00:00:00Z"

        expected_hash = hashlib.sha256(
            f"{cert_id}{learner_id}{issued_at}".encode()
        ).hexdigest()[:16]

        cert = Certification(
            cert_id=cert_id,
            cert_type=CertificationType.MOLECULAR_SPECIALIST,
            learner_id=learner_id,
            learner_name="Test User",
            issued_at=issued_at,
            expires_at="2028-01-01T00:00:00Z",
            verification_hash=expected_hash
        )
        assert cert.verify() is True


class TestTranscendentLearningPlatform:
    """Tests for TranscendentLearningPlatform class."""

    @pytest.fixture
    def platform(self, tmp_path):
        """Create platform with temporary directory."""
        return TranscendentLearningPlatform(data_path=tmp_path)

    def test_platform_initialization(self, platform):
        """Test platform initializes with default modules."""
        assert platform is not None
        assert len(platform._modules) > 0
        assert len(platform._learning_paths) > 0

    def test_register_learner(self, platform):
        """Test learner registration."""
        learner = platform.register_learner(
            name="Test User",
            email="test@example.com",
            region="Asia Pacific",
            country="Japan"
        )
        assert learner is not None
        assert learner.name == "Test User"
        assert learner.learner_id.startswith("LRN-")

    def test_enroll_in_module(self, platform):
        """Test module enrollment."""
        learner = platform.register_learner(
            name="Test Enrollee",
            email="enrollee@example.com",
            region="Europe",
            country="France"
        )

        # Enroll in a foundational module (no prerequisites)
        result = platform.enroll_in_module(learner.learner_id, "ZC-101")
        assert result is True
        assert "ZC-101" in learner.in_progress_modules

    def test_complete_module(self, platform):
        """Test module completion."""
        learner = platform.register_learner(
            name="Test Completer",
            email="completer@example.com",
            region="North America",
            country="Canada"
        )

        platform.enroll_in_module(learner.learner_id, "ZC-101")
        result = platform.complete_module(
            learner.learner_id,
            "ZC-101",
            score=92.0,
            consciousness_score=85.0
        )

        assert result['success'] is True
        assert result['points_earned'] > 0
        assert "ZC-101" in learner.completed_modules
        assert "ZC-101" not in learner.in_progress_modules

    def test_prerequisite_enforcement(self, platform):
        """Test that prerequisites are enforced."""
        learner = platform.register_learner(
            name="Test Prereq",
            email="prereq@example.com",
            region="South America",
            country="Brazil"
        )

        # Try to enroll in advanced module without prerequisites
        result = platform.enroll_in_module(learner.learner_id, "ZC-201")
        assert result is False

    def test_issue_certification(self, platform):
        """Test certification issuance."""
        learner = platform.register_learner(
            name="Test Certified",
            email="certified@example.com",
            region="Europe",
            country="UK"
        )

        # Complete required modules
        platform.enroll_in_module(learner.learner_id, "ZC-101")
        platform.complete_module(learner.learner_id, "ZC-101", 90.0, 85.0)

        cert = platform.issue_certification(
            learner.learner_id,
            CertificationType.ZONE_CONCEPT_PRACTITIONER,
            final_score=90.0,
            consciousness_score=85.0
        )

        assert cert is not None
        assert cert.cert_type == CertificationType.ZONE_CONCEPT_PRACTITIONER
        assert cert.learner_name == "Test Certified"

    def test_verify_certification(self, platform):
        """Test certification verification."""
        learner = platform.register_learner(
            name="Test Verify",
            email="verify@example.com",
            region="Middle East",
            country="UAE"
        )

        cert = platform.issue_certification(
            learner.learner_id,
            CertificationType.CONSCIOUSNESS_GUIDE,
            final_score=88.0,
            consciousness_score=90.0
        )

        result = platform.verify_certification(cert.cert_id)
        assert result['valid'] is True
        assert result['verification_status'] == "VERIFIED"

    def test_get_learner_progress(self, platform):
        """Test learner progress retrieval."""
        learner = platform.register_learner(
            name="Test Progress",
            email="progress@example.com",
            region="Africa",
            country="South Africa"
        )

        platform.enroll_in_module(learner.learner_id, "ZC-101")
        platform.complete_module(learner.learner_id, "ZC-101", 85.0, 80.0)

        progress = platform.get_learner_progress(learner.learner_id)
        assert 'summary' in progress
        assert progress['summary']['total_modules_completed'] == 1

    def test_set_learning_path(self, platform):
        """Test setting learning path."""
        learner = platform.register_learner(
            name="Test Path",
            email="path@example.com",
            region="Asia Pacific",
            country="Australia"
        )

        result = platform.set_learning_path(learner.learner_id, "PATH-ZCP")
        assert result is True
        assert learner.learning_path == "PATH-ZCP"

    def test_get_platform_statistics(self, platform):
        """Test platform statistics retrieval."""
        # Register some learners
        for i in range(3):
            platform.register_learner(
                name=f"Stat User {i}",
                email=f"stat{i}@example.com",
                region="Europe",
                country="Germany"
            )

        stats = platform.get_platform_statistics()
        assert stats['learners']['total'] == 3
        assert 'modules' in stats
        assert 'certifications' in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
