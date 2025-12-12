#!/usr/bin/env python3
"""
PreToolUse Hook: Validate Conventional Commits format.
Runs before: Bash (git commit)

Validates that commit messages follow Conventional Commits format:
- type(scope): description
- type: description

Exit codes (Claude Code convention):
- 0 + JSON permissionDecision: "deny" → Block with structured feedback
- 0 + no JSON → Allow
"""
import json
import re
import sys

# Pattern: type(optional-scope)?!?: message
# Conventional Commits spec allows any type (lowercase alphanumeric)
PATTERN = re.compile(
    r"^[a-z]+"  # type (any lowercase word)
    r"(\([^)]+\))?"  # optional (scope)
    r"!?"  # optional ! for breaking
    r": "  # colon + space
    r".+"  # message (non-empty)
    r"$"
)


def extract_commit_message(command: str) -> str | None:
    """Extract commit message from git commit command."""
    # Handle HEREDOC: git commit -m "$(cat <<'EOF' ... EOF)"
    heredoc_match = re.search(r"\$\(cat <<['\"]?EOF['\"]?\n(.+?)\nEOF", command, re.DOTALL)
    if heredoc_match:
        return heredoc_match.group(1).split("\n")[0].strip()

    # Handle: git commit -m "message"
    match = re.search(r'-m\s+"([^"]+)"', command)
    if match:
        return match.group(1).split("\n")[0].strip()

    # Handle: git commit -m 'message'
    match = re.search(r"-m\s+'([^']+)'", command)
    if match:
        return match.group(1).split("\n")[0].strip()

    return None


def block_with_guidance(message: str, reason: str) -> None:
    """Block commit with format guidance."""
    guidance = f"""Invalid commit message format.

**Your message**: {message}
**Issue**: {reason}

**Conventional Commits format**:
```
type(scope): description

[optional body]

[optional footer(s)]
```

**Examples**:
- feat: add new feature
- fix(video): resolve decoder crash
- feat(timeline)!: breaking API change
- docs: update README

**With Linear reference**:
```
feat(video): add WebCodecs decoder

Refs PREFIX-XX
```
"""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": guidance,
        }
    }
    print(json.dumps(output))
    sys.exit(0)


def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    command = hook_input.get("tool_input", {}).get("command", "")

    # Only check git commit commands with -m flag
    if "git commit" not in command or "-m" not in command:
        sys.exit(0)

    # Extract commit message
    message = extract_commit_message(command)
    if not message:
        sys.exit(0)  # Can't parse, let it through

    # Skip merge commits
    if message.startswith("Merge "):
        sys.exit(0)

    # Validate format
    if not PATTERN.match(message):
        # Determine specific issue
        if not re.match(r"^[a-z]+", message):
            reason = "Must start with a lowercase type (e.g., feat, fix, docs)"
        elif ": " not in message:
            reason = "Missing ': ' (colon followed by space) after type/scope"
        elif message.split(": ", 1)[1].strip() == "":
            reason = "Empty description after ': '"
        else:
            reason = "Invalid format"

        block_with_guidance(message, reason)

    # Valid format - allow
    sys.exit(0)


if __name__ == "__main__":
    main()
