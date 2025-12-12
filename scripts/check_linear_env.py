#!/usr/bin/env python3
"""
Hook: Check Linear workflow environment on skill activation.
Runs on: UserPromptSubmit (first user message)

Validates LINEAR_WORKFLOW_TEAM and LINEAR_WORKFLOW_PROJECT are configured
before the workflow begins, providing early feedback.

Exit codes:
- 0: Always allow (this is advisory, not blocking)

Output:
- Prints warning message if env vars are missing
"""
import json
import os
import sys


def check_linear_config() -> tuple[bool, list[str]]:
    """Check if Linear workflow environment variables are configured."""
    missing = []
    if not os.environ.get("LINEAR_WORKFLOW_TEAM"):
        missing.append("LINEAR_WORKFLOW_TEAM")
    if not os.environ.get("LINEAR_WORKFLOW_PROJECT"):
        missing.append("LINEAR_WORKFLOW_PROJECT")
    return len(missing) == 0, missing


def main() -> None:
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
                "hookEventName": "UserPromptSubmit",
                "linearWorkflowWarning": True,
                "missingVars": missing,
            }
        }
        print(json.dumps(output))

    # Always exit 0 - this is advisory, not blocking
    sys.exit(0)


if __name__ == "__main__":
    main()
