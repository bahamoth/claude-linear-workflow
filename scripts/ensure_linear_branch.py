#!/usr/bin/env python3
"""
PreToolUse Hook: Ensure Linear branch before file modifications.
Runs before: Write, Edit, ExitPlanMode

Blocks work on main/master branch when Linear workflow is configured.
Uses session caching to avoid repeated checks.

Note: Environment variable warning is handled by check_linear_env.py

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


def has_issue_id(branch: str) -> str | None:
    """Extract Linear issue ID from branch name, or None if not found."""
    match = re.search(r"([a-z]+-\d+)", branch, re.IGNORECASE)
    return match.group(1).upper() if match else None


def load_cache(cwd: str, session_id: str) -> dict | None:
    """Load session cache."""
    cache_path = Path(cwd) / ".claude" / f"linear-session-{session_id}.json"
    if not cache_path.exists():
        return None
    try:
        with open(cache_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_cache(cwd: str, session_id: str, branch: str, **kwargs) -> None:
    """Save session cache and exit."""
    cache_path = Path(cwd) / ".claude" / f"linear-session-{session_id}.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    state = {
        "checked": True,
        "branch": branch,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        **kwargs,
    }
    with open(cache_path, "w") as f:
        json.dump(state, f)


def block(reason: str) -> None:
    """Block with structured feedback and exit."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
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

    # Get current branch
    branch = get_current_branch()

    # Fast exit if cached for this branch
    cache = load_cache(cwd, session_id)
    if cache and cache.get("checked") and cache.get("branch") == branch:
        sys.exit(0)

    # Skip if Linear not configured
    if not os.environ.get("LINEAR_WORKFLOW_TEAM"):
        save_cache(cwd, session_id, branch, linear_configured=False)
        sys.exit(0)

    # Block main/master without issue ID
    issue_id = has_issue_id(branch)
    if branch in ["main", "master"] and not issue_id:
        block(
            "Cannot modify files on main branch without a Linear issue.\n\n"
            "REQUIRED: Call Skill(skill: 'linear-workflow') to proceed.\n\n"
            "The skill will guide you through:\n"
            "1. Searching/creating Linear issue\n"
            "2. Creating branch with gitBranchName\n"
            "3. Then proceed with your changes"
        )

    # Allow and cache
    save_cache(cwd, session_id, branch, linear_configured=True, issue_id=issue_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
