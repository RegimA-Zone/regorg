# RegimA Zone — Slack Workspace Directory

A browsable directory of the RegimA Zone Slack workspace, including team members and channels.

## Files

| File | Description |
|------|-------------|
| `workspace_directory.json` | Source-of-truth JSON data for members, channels, and workspace metadata |
| `index.html` | Interactive visual directory (open in any browser) |

## Viewing the Directory

Open `index.html` directly in your browser — it loads `workspace_directory.json` via `fetch()`, so it works from a local file server:

```bash
# From the repo root
cd slack
python -m http.server 8080
# Then open http://localhost:8080
```

## Managing the Directory

Use `scripts/slack_directory.py` to query or regenerate the directory:

```bash
# Print a summary of the workspace to stdout and write outputs/slack_directory_summary.json
python scripts/slack_directory.py
```

The script exposes the `SlackDirectoryManager` class for programmatic use:

```python
from scripts.slack_directory import SlackDirectoryManager

manager = SlackDirectoryManager()
manager.load()

# Search members
results = manager.search_members("research")

# Filter by department
team = manager.filter_by_department("Research & Innovation")

# Get summary dict
summary = manager.generate_summary()
```

## Data Schema

### `workspace`
```json
{
  "name": "RegimA Zone",
  "domain": "regima-zone",
  "description": "...",
  "member_count": 24,
  "channel_count": 18,
  "created_at": "2024-01-15"
}
```

### `members[]`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique member ID (`U001`, …) |
| `name` | string | Full display name |
| `display_name` | string | Slack handle (no `@`) |
| `title` | string | Job title |
| `department` | string | Department name |
| `email` | string | Work email |
| `avatar_color` | string | Hex colour used in the UI avatar |
| `avatar_initials` | string | Two-letter initials for the avatar |
| `status` | string | `active` \| `inactive` |
| `is_admin` | boolean | Workspace admin flag |
| `channels` | string[] | List of channel IDs the member belongs to |

### `channels[]`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique channel ID (`C001`, …) |
| `name` | string | Channel name (no `#`) |
| `topic` | string | Current channel topic |
| `purpose` | string | Channel purpose |
| `member_count` | number | Number of members |
| `is_private` | boolean | Whether the channel is private |
| `category` | string | Organisational category |
