#!/usr/bin/env python3
"""
Hook: Check Linear workflow environment configuration.
Runs on: UserPromptSubmit, PreToolUse (Write|Edit|ExitPlanMode)

Validates LINEAR_WORKFLOW_TEAM and LINEAR_WORKFLOW_PROJECT are configured.
Uses session caching to warn only once per session.

Exit codes:
- 0: Always allow (this is advisory, not blocking)

Output:
- Prints warning message if env vars are missing (once per session)
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_session_state_path(cwd: str, session_id: str) -> Path:
    """Get session state file path for env check."""
    return Path(cwd) / ".claude" / f"linear-env-warned-{session_id}.json"


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


def check_linear_config() -> tuple[bool, list[str]]:
    """Check if Linear workflow environment variables are configured."""
    missing = []
    if not os.environ.get("LINEAR_WORKFLOW_TEAM"):
        missing.append("LINEAR_WORKFLOW_TEAM")
    if not os.environ.get("LINEAR_WORKFLOW_PROJECT"):
        missing.append("LINEAR_WORKFLOW_PROJECT")
    return len(missing) == 0, missing


def main() -> None:
    # Parse input for session info
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        hook_input = {}

    session_id = hook_input.get("session_id", "unknown")
    cwd = hook_input.get("cwd", os.getcwd())

    # Check if already warned this session
    state_path = get_session_state_path(cwd, session_id)
    state = load_session_state(state_path)
    if state and state.get("warned"):
        # Already warned this session -> skip
        sys.exit(0)

    configured, missing = check_linear_config()

    if not configured:
        warning_message = (
            "⚠️ Linear workflow environment not configured.\n\n"
            f"Missing: {', '.join(missing)}\n\n"
            "To enable Linear-tracked development, add to .claude/settings.json:\n"
            '{\n'
            '  "env": {\n'
            '    "LINEAR_WORKFLOW_TEAM": "YourTeam",\n'
            '    "LINEAR_WORKFLOW_PROJECT": "YourProject"\n'
            '  }\n'
            '}\n\n'
            "Use Linear MCP to find your team/project:\n"
            "  mcp__linear__list_teams()\n"
            "  mcp__linear__list_projects(teamId: ...)"
        )
        output = {
            "systemMessage": warning_message,
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "linearWorkflowWarning": True,
                "missingVars": missing,
            }
        }
        print(json.dumps(output))

        # Save state to avoid warning again this session
        save_session_state(
            state_path,
            {
                "warned": True,
                "missing": missing,
                "warned_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    # Always exit 0 - this is advisory, not blocking
    sys.exit(0)


if __name__ == "__main__":
    main()
