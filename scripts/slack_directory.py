#!/usr/bin/env python3
"""
RegimA Slack Workspace Directory Manager

This script provides utilities for managing and generating the RegimA Zone
Slack workspace directory, including member listings, channel catalogues,
and HTML report generation.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class WorkspaceMember:
    """Represents a Slack workspace member."""
    id: str
    name: str
    display_name: str
    title: str
    department: str
    email: str
    avatar_color: str = "#4A154B"
    avatar_initials: str = ""
    status: str = "active"
    is_admin: bool = False
    phone: str = ""
    pronouns: str = ""
    channels: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.avatar_initials and self.name:
            parts = self.name.split()
            self.avatar_initials = "".join(p[0].upper() for p in parts[:2])

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkspaceChannel:
    """Represents a Slack workspace channel."""
    id: str
    name: str
    topic: str
    purpose: str
    member_count: int
    is_private: bool = False
    category: str = "General"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkspaceInfo:
    """High-level workspace metadata."""
    name: str
    domain: str
    description: str
    icon: str = ""
    member_count: int = 0
    channel_count: int = 0
    created_at: str = ""


class SlackDirectoryManager:
    """Manages the RegimA Slack workspace directory."""

    def __init__(self, data_path: Optional[Path] = None):
        self.base_path = Path(__file__).parent.parent
        self.slack_dir = self.base_path / "slack"
        self.data_path = data_path or (self.slack_dir / "workspace_directory.json")
        self._data: Dict[str, Any] = {}
        self._members: List[WorkspaceMember] = []
        self._channels: List[WorkspaceChannel] = []
        self._workspace: Optional[WorkspaceInfo] = None

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(self) -> bool:
        """Load directory data from the JSON file."""
        try:
            with open(self.data_path, "r", encoding="utf-8") as fh:
                self._data = json.load(fh)
            self._parse()
            logger.info("Loaded %d members and %d channels from %s",
                        len(self._members), len(self._channels), self.data_path)
            return True
        except FileNotFoundError:
            logger.error("Directory file not found: %s", self.data_path)
            return False
        except json.JSONDecodeError as exc:
            logger.error("Invalid JSON in %s: %s", self.data_path, exc)
            return False

    def _parse(self) -> None:
        """Parse raw JSON data into typed objects."""
        ws = self._data.get("workspace", {})
        self._workspace = WorkspaceInfo(
            name=ws.get("name", ""),
            domain=ws.get("domain", ""),
            description=ws.get("description", ""),
            icon=ws.get("icon", ""),
            member_count=ws.get("member_count", 0),
            channel_count=ws.get("channel_count", 0),
            created_at=ws.get("created_at", ""),
        )

        self._members = []
        for m in self._data.get("members", []):
            self._members.append(WorkspaceMember(
                id=m.get("id", ""),
                name=m.get("name", ""),
                display_name=m.get("display_name", ""),
                title=m.get("title", ""),
                department=m.get("department", ""),
                email=m.get("email", ""),
                avatar_color=m.get("avatar_color", "#4A154B"),
                avatar_initials=m.get("avatar_initials", ""),
                status=m.get("status", "active"),
                is_admin=m.get("is_admin", False),
                phone=m.get("phone", ""),
                pronouns=m.get("pronouns", ""),
                channels=m.get("channels", []),
            ))

        self._channels = []
        for ch in self._data.get("channels", []):
            self._channels.append(WorkspaceChannel(
                id=ch.get("id", ""),
                name=ch.get("name", ""),
                topic=ch.get("topic", ""),
                purpose=ch.get("purpose", ""),
                member_count=ch.get("member_count", 0),
                is_private=ch.get("is_private", False),
                category=ch.get("category", "General"),
            ))

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def members(self) -> List[WorkspaceMember]:
        return list(self._members)

    @property
    def channels(self) -> List[WorkspaceChannel]:
        return list(self._channels)

    @property
    def workspace(self) -> Optional[WorkspaceInfo]:
        return self._workspace

    def get_member(self, member_id: str) -> Optional[WorkspaceMember]:
        """Look up a member by ID."""
        return next((m for m in self._members if m.id == member_id), None)

    def get_channel(self, channel_id: str) -> Optional[WorkspaceChannel]:
        """Look up a channel by ID."""
        return next((ch for ch in self._channels if ch.id == channel_id), None)

    def search_members(self, query: str) -> List[WorkspaceMember]:
        """Search members by name, display name, title, or department."""
        q = query.lower()
        return [
            m for m in self._members
            if q in m.name.lower()
            or q in m.display_name.lower()
            or q in m.title.lower()
            or q in m.department.lower()
        ]

    def filter_by_department(self, department: str) -> List[WorkspaceMember]:
        """Return members belonging to the given department."""
        return [m for m in self._members if m.department == department]

    def get_departments(self) -> List[str]:
        """Return sorted list of distinct departments."""
        return sorted({m.department for m in self._members})

    def get_public_channels(self) -> List[WorkspaceChannel]:
        """Return only public channels."""
        return [ch for ch in self._channels if not ch.is_private]

    def get_channels_by_category(self, category: str) -> List[WorkspaceChannel]:
        """Return channels filtered by category."""
        return [ch for ch in self._channels if ch.category == category]

    def get_member_channels(self, member_id: str) -> List[WorkspaceChannel]:
        """Return all channels a given member belongs to."""
        member = self.get_member(member_id)
        if not member:
            return []
        return [ch for ch in self._channels if ch.id in member.channels]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: Optional[Path] = None) -> bool:
        """Persist the current state back to JSON."""
        target = path or self.data_path
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            payload = dict(self._data)
            payload["members"]  = [m.to_dict() for m in self._members]
            payload["channels"] = [ch.to_dict() for ch in self._channels]
            if self._workspace:
                payload["workspace"]["member_count"]  = len(self._members)
                payload["workspace"]["channel_count"] = len(self._channels)
            with open(target, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, ensure_ascii=False)
            logger.info("Saved directory to %s", target)
            return True
        except OSError as exc:
            logger.error("Failed to save directory: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def generate_summary(self) -> Dict[str, Any]:
        """Return a summary dict suitable for reports or dashboards."""
        depts = self.get_departments()
        dept_counts = {d: len(self.filter_by_department(d)) for d in depts}
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "workspace": {
                "name":         self._workspace.name if self._workspace else "",
                "domain":       self._workspace.domain if self._workspace else "",
                "description":  self._workspace.description if self._workspace else "",
            },
            "totals": {
                "members":          len(self._members),
                "channels":         len(self._channels),
                "public_channels":  len(self.get_public_channels()),
                "private_channels": len(self._channels) - len(self.get_public_channels()),
                "departments":      len(depts),
                "admins":           sum(1 for m in self._members if m.is_admin),
            },
            "departments": dept_counts,
        }

    def print_summary(self) -> None:
        """Print a human-readable directory summary to stdout."""
        summary = self.generate_summary()
        ws = summary["workspace"]
        totals = summary["totals"]
        print("\n" + "=" * 60)
        print(f"  {ws['name']} — Slack Workspace Directory")
        print(f"  {ws['description']}")
        print("=" * 60)
        print(f"  Members  : {totals['members']}")
        print(f"  Channels : {totals['channels']} "
              f"({totals['public_channels']} public, {totals['private_channels']} private)")
        print(f"  Departments: {totals['departments']}")
        print()
        print("  Members by Department:")
        for dept, count in summary["departments"].items():
            print(f"    {dept:<30} {count}")
        print()
        print("  Members:")
        for m in self._members:
            admin_tag = " [Admin]" if m.is_admin else ""
            print(f"    @{m.display_name:<25} {m.name:<25} {m.title}{admin_tag}")
        print()
        print("  Channels:")
        for ch in self._channels:
            priv = " [private]" if ch.is_private else ""
            print(f"    #{ch.name:<30} {ch.member_count:>3} members  {ch.category}{priv}")
        print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    manager = SlackDirectoryManager()
    if not manager.load():
        logger.error("Could not load workspace directory. Exiting.")
        return
    manager.print_summary()
    summary = manager.generate_summary()
    output_path = manager.base_path / "outputs" / "slack_directory_summary.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    logger.info("Summary written to %s", output_path)


if __name__ == "__main__":
    main()
