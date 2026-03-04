#!/usr/bin/env python3
"""
Tests for the Slack Workspace Directory Manager
"""

import json
import pytest
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from slack_directory import (
    SlackDirectoryManager,
    WorkspaceMember,
    WorkspaceChannel,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_data() -> dict:
    return {
        "workspace": {
            "name": "Test Workspace",
            "domain": "test-ws",
            "description": "A test workspace",
            "icon": "",
            "member_count": 2,
            "channel_count": 2,
            "created_at": "2024-01-01",
        },
        "departments": ["Engineering", "Design"],
        "channels": [
            {
                "id": "C001",
                "name": "general",
                "topic": "General discussion",
                "purpose": "For everyone",
                "member_count": 2,
                "is_private": False,
                "category": "General",
            },
            {
                "id": "C002",
                "name": "leadership",
                "topic": "Leadership only",
                "purpose": "Private leadership channel",
                "member_count": 1,
                "is_private": True,
                "category": "Leadership",
            },
        ],
        "members": [
            {
                "id": "U001",
                "name": "Alice Smith",
                "display_name": "alice.smith",
                "title": "Lead Engineer",
                "department": "Engineering",
                "email": "alice@example.com",
                "avatar_color": "#4A154B",
                "avatar_initials": "AS",
                "status": "active",
                "is_admin": True,
                "phone": "",
                "pronouns": "she/her",
                "channels": ["C001", "C002"],
            },
            {
                "id": "U002",
                "name": "Bob Jones",
                "display_name": "bob.jones",
                "title": "Senior Designer",
                "department": "Design",
                "email": "bob@example.com",
                "avatar_color": "#0F9D58",
                "avatar_initials": "BJ",
                "status": "active",
                "is_admin": False,
                "phone": "",
                "pronouns": "he/him",
                "channels": ["C001"],
            },
        ],
    }


@pytest.fixture
def data_file(sample_data, tmp_path) -> Path:
    """Write sample data to a temp JSON file and return its path."""
    path = tmp_path / "workspace_directory.json"
    path.write_text(json.dumps(sample_data), encoding="utf-8")
    return path


@pytest.fixture
def manager(data_file) -> SlackDirectoryManager:
    m = SlackDirectoryManager(data_path=data_file)
    assert m.load()
    return m


# ---------------------------------------------------------------------------
# WorkspaceMember
# ---------------------------------------------------------------------------

class TestWorkspaceMember:
    def test_avatar_initials_auto(self):
        m = WorkspaceMember(
            id="U999", name="Jane Doe", display_name="jane.doe",
            title="Tester", department="QA", email="j@example.com",
        )
        assert m.avatar_initials == "JD"

    def test_avatar_initials_explicit(self):
        m = WorkspaceMember(
            id="U999", name="Jane Doe", display_name="jane.doe",
            title="Tester", department="QA", email="j@example.com",
            avatar_initials="XX",
        )
        assert m.avatar_initials == "XX"

    def test_to_dict_contains_required_keys(self):
        m = WorkspaceMember(
            id="U001", name="Alice", display_name="alice",
            title="Dev", department="Eng", email="a@a.com",
        )
        d = m.to_dict()
        for key in ("id", "name", "display_name", "title", "department", "email"):
            assert key in d


# ---------------------------------------------------------------------------
# WorkspaceChannel
# ---------------------------------------------------------------------------

class TestWorkspaceChannel:
    def test_defaults(self):
        ch = WorkspaceChannel(
            id="C999", name="random", topic="Random chat",
            purpose="Just random", member_count=5,
        )
        assert not ch.is_private
        assert ch.category == "General"

    def test_to_dict(self):
        ch = WorkspaceChannel(
            id="C001", name="general", topic="t", purpose="p",
            member_count=10, is_private=False, category="General",
        )
        d = ch.to_dict()
        assert d["name"] == "general"
        assert d["member_count"] == 10


# ---------------------------------------------------------------------------
# SlackDirectoryManager — loading
# ---------------------------------------------------------------------------

class TestSlackDirectoryManagerLoad:
    def test_load_success(self, manager):
        assert len(manager.members) == 2
        assert len(manager.channels) == 2

    def test_load_missing_file(self, tmp_path):
        m = SlackDirectoryManager(data_path=tmp_path / "nonexistent.json")
        assert not m.load()

    def test_load_invalid_json(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json")
        m = SlackDirectoryManager(data_path=bad)
        assert not m.load()

    def test_workspace_meta(self, manager):
        assert manager.workspace is not None
        assert manager.workspace.name == "Test Workspace"
        assert manager.workspace.domain == "test-ws"


# ---------------------------------------------------------------------------
# SlackDirectoryManager — queries
# ---------------------------------------------------------------------------

class TestSlackDirectoryManagerQueries:
    def test_get_member_found(self, manager):
        m = manager.get_member("U001")
        assert m is not None
        assert m.name == "Alice Smith"

    def test_get_member_not_found(self, manager):
        assert manager.get_member("UXXX") is None

    def test_get_channel_found(self, manager):
        ch = manager.get_channel("C001")
        assert ch is not None
        assert ch.name == "general"

    def test_get_channel_not_found(self, manager):
        assert manager.get_channel("CXXX") is None

    def test_search_members_by_name(self, manager):
        results = manager.search_members("alice")
        assert len(results) == 1
        assert results[0].id == "U001"

    def test_search_members_by_title(self, manager):
        results = manager.search_members("designer")
        assert len(results) == 1
        assert results[0].id == "U002"

    def test_search_members_empty_query(self, manager):
        results = manager.search_members("")
        assert len(results) == 2

    def test_search_members_no_match(self, manager):
        assert manager.search_members("zzznomatch") == []

    def test_filter_by_department(self, manager):
        eng = manager.filter_by_department("Engineering")
        assert len(eng) == 1
        assert eng[0].name == "Alice Smith"

    def test_filter_by_department_no_match(self, manager):
        assert manager.filter_by_department("HR") == []

    def test_get_departments(self, manager):
        depts = manager.get_departments()
        assert "Engineering" in depts
        assert "Design" in depts

    def test_get_public_channels(self, manager):
        public = manager.get_public_channels()
        assert all(not ch.is_private for ch in public)
        assert len(public) == 1

    def test_get_channels_by_category(self, manager):
        leadership = manager.get_channels_by_category("Leadership")
        assert len(leadership) == 1
        assert leadership[0].name == "leadership"

    def test_get_member_channels(self, manager):
        channels = manager.get_member_channels("U001")
        assert len(channels) == 2

    def test_get_member_channels_unknown(self, manager):
        assert manager.get_member_channels("UXXX") == []


# ---------------------------------------------------------------------------
# SlackDirectoryManager — summary
# ---------------------------------------------------------------------------

class TestSlackDirectoryManagerSummary:
    def test_summary_totals(self, manager):
        summary = manager.generate_summary()
        assert summary["totals"]["members"] == 2
        assert summary["totals"]["channels"] == 2
        assert summary["totals"]["public_channels"] == 1
        assert summary["totals"]["private_channels"] == 1
        assert summary["totals"]["admins"] == 1

    def test_summary_departments(self, manager):
        summary = manager.generate_summary()
        assert summary["departments"]["Engineering"] == 1
        assert summary["departments"]["Design"] == 1

    def test_summary_has_generated_at(self, manager):
        summary = manager.generate_summary()
        assert "generated_at" in summary

    def test_print_summary_no_error(self, manager, capsys):
        manager.print_summary()
        captured = capsys.readouterr()
        assert "Test Workspace" in captured.out
        assert "Alice Smith" in captured.out


# ---------------------------------------------------------------------------
# SlackDirectoryManager — persistence
# ---------------------------------------------------------------------------

class TestSlackDirectoryManagerSave:
    def test_save_and_reload(self, manager, tmp_path):
        out = tmp_path / "saved.json"
        assert manager.save(out)
        m2 = SlackDirectoryManager(data_path=out)
        assert m2.load()
        assert len(m2.members) == 2
        assert len(m2.channels) == 2

    def test_save_updates_counts(self, manager, tmp_path):
        out = tmp_path / "saved.json"
        manager.save(out)
        with open(out) as fh:
            data = json.load(fh)
        assert data["workspace"]["member_count"] == 2
        assert data["workspace"]["channel_count"] == 2


# ---------------------------------------------------------------------------
# Integration — real data file
# ---------------------------------------------------------------------------

class TestRealDataFile:
    def test_real_file_loads(self):
        real_path = Path(__file__).parent.parent / "slack" / "workspace_directory.json"
        if not real_path.exists():
            pytest.skip("workspace_directory.json not present")
        m = SlackDirectoryManager(data_path=real_path)
        assert m.load()
        assert len(m.members) > 0
        assert len(m.channels) > 0

    def test_real_file_has_required_fields(self):
        real_path = Path(__file__).parent.parent / "slack" / "workspace_directory.json"
        if not real_path.exists():
            pytest.skip("workspace_directory.json not present")
        m = SlackDirectoryManager(data_path=real_path)
        m.load()
        for member in m.members:
            assert member.id
            assert member.name
            assert member.display_name
            assert member.department
