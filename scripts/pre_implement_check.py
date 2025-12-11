#!/usr/bin/env python3
"""
Hook: Pre-implementation check for Linear workflow compliance.
Runs before: ExitPlanMode

Ensures work is on a feature branch with Linear issue ID before implementation.
Blocks implementation on main/master branch.

Exit codes (Claude Code convention):
- 0 + JSON permissionDecision: "deny" → Block with structured feedback
- 0 + no JSON or permissionDecision: "allow" → Allow
"""
import json
import re
import subprocess
import sys


def get_current_branch() -> str:
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def has_issue_id(branch: str) -> bool:
    """Check if branch name contains a Linear issue ID pattern (e.g., abc-7, PROJ-123)."""
    # Universal pattern: any alphabetic prefix followed by dash and number
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
    branch = get_current_branch()

    # Allow if branch has issue ID
    if has_issue_id(branch):
        sys.exit(0)

    # Block if on main/master
    if branch in ["main", "master"]:
        block_with_reason(
            "Cannot start implementation on main branch.\n\n"
            "Before implementing:\n"
            "1. Search Linear for similar issues matching your plan\n"
            "2. If similar issue exists → ask user which to use\n"
            "3. If no match → create new issue from plan\n"
            "4. Create branch using gitBranchName from issue\n"
            "5. Then exit plan mode to start implementation\n\n"
            "Use linear-workflow skill for guidance."
        )

    # Other branches without issue ID - allow
    sys.exit(0)


if __name__ == "__main__":
    main()
