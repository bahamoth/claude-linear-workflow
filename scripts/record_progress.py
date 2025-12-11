#!/usr/bin/env python3
"""
PostToolUse Hook: Record file modifications to local progress file.

Triggered after: Write, Edit tools
Output: .claude/progress/{session_id}.jsonl
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Invalid input, skip silently
        sys.exit(0)

    session_id = hook_input.get("session_id", "unknown")
    tool_name = hook_input.get("tool_name")
    tool_input = hook_input.get("tool_input", {})
    cwd = hook_input.get("cwd", "")

    if not cwd:
        sys.exit(0)

    # Extract file path and convert to relative
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    if file_path.startswith(cwd):
        file_path = file_path[len(cwd) :].lstrip("/")

    # Skip progress files themselves to avoid recursion
    if ".claude/progress/" in file_path or file_path.startswith(".claude/progress"):
        sys.exit(0)

    # Create progress directory
    progress_dir = Path(cwd) / ".claude" / "progress"
    progress_dir.mkdir(parents=True, exist_ok=True)

    # Build record
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "file": file_path,
    }

    # Append to session progress file
    progress_file = progress_dir / f"{session_id}.jsonl"
    with open(progress_file, "a") as f:
        f.write(json.dumps(record) + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
