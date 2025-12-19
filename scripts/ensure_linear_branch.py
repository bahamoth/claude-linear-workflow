#!/usr/bin/env python3
"""
PreToolUse Hook: Ensure Linear branch before file modifications.
Runs before: Write, Edit tools

Optimized for performance with session state caching.
First invocation per session checks branch; subsequent calls fast-exit.

Exit codes:
- 0 + JSON permissionDecision: "deny" -> Block with guidance
- 0 + no JSON or "allow" -> Allow
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_session_state_path(cwd: str, session_id: str) -> Path:
    """Get session state file path."""
    return Path(cwd) / ".claude" / f"linear-session-{session_id}.json"


def load_session_state(state_path: Path) -> dict | None:
    """Load existing session state if valid."""
    if not state_path.exists():
        return None
    try:
        with open(state_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_session_state(state_path: Path, state: dict) -> None:
    """Save session state."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, "w") as f:
        json.dump(state, f)


def get_current_branch() -> str:
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return ""


def has_issue_id(branch: str) -> bool:
    """Check if branch contains Linear issue ID pattern."""
    return bool(re.search(r"[a-z]+-\d+", branch, re.IGNORECASE))


def block_with_reason(reason: str) -> None:
    """Output JSON to block with structured feedback."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(output))
    sys.exit(0)


def main() -> None:
    # Parse input
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    session_id = hook_input.get("session_id", "unknown")
    cwd = hook_input.get("cwd", "")

    if not cwd:
        sys.exit(0)

    # OPTIMIZATION 1: Check session state (fastest path)
    state_path = get_session_state_path(cwd, session_id)
    state = load_session_state(state_path)
    if state and state.get("checked"):
        # Already checked this session -> fast exit
        sys.exit(0)

    # OPTIMIZATION 2: Check Linear config (skip if not configured)
    team = os.environ.get("LINEAR_WORKFLOW_TEAM")
    if not team:
        # Linear workflow not configured -> allow silently
        # Save state to avoid checking again
        save_session_state(
            state_path,
            {
                "checked": True,
                "linear_configured": False,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        sys.exit(0)

    # OPTIMIZATION 3: Check branch (only if Linear configured)
    branch = get_current_branch()

    if has_issue_id(branch):
        # On issue branch -> save state and allow
        issue_match = re.search(r"([a-z]+-\d+)", branch, re.IGNORECASE)
        save_session_state(
            state_path,
            {
                "checked": True,
                "linear_configured": True,
                "branch": branch,
                "issue_id": issue_match.group(1).upper() if issue_match else None,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        sys.exit(0)

    # BLOCK: On main/master without issue branch
    if branch in ["main", "master"]:
        block_with_reason(
            "Cannot modify files on main branch without a Linear issue.\n\n"
            "Before making changes:\n"
            "1. Search Linear for existing issues matching your work\n"
            "2. Create a new issue if needed\n"
            "3. Create a branch using gitBranchName from the issue\n"
            "4. Then proceed with your changes\n\n"
            "Use linear-workflow skill for guidance."
        )

    # Other branches without issue ID - warn but allow
    save_session_state(
        state_path,
        {
            "checked": True,
            "linear_configured": True,
            "branch": branch,
            "issue_id": None,
            "warning": "Branch has no Linear issue ID",
            "checked_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
