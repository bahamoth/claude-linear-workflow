# Linear Workflow Plugin for Claude Code

A Claude Code plugin that enforces Linear issue-driven development workflow with branch naming conventions, Conventional Commits validation, and automatic issue tracking.

## Features

- **Branch enforcement**: Blocks implementation on `main`/`master` without a Linear issue
- **Commit validation**: Enforces Conventional Commits format
- **Workflow guidance**: Auto-activates skill when working with Linear issues
- **Progress tracking**: Records file modifications for session summaries

## Prerequisites

- [Claude Code](https://claude.com/claude-code) CLI
- [Linear MCP](https://github.com/jerhadf/linear-mcp) configured in Claude Code
- Git repository

## Installation

```bash
# Add marketplace
/plugin marketplace add bahamoth/claude-linear-workflow

# Install plugin
/plugin install linear-workflow@bahamoth/claude-linear-workflow
```

## Configuration

Add your Linear team and project to `.claude/settings.json`:

```json
{
  "linearConfig": {
    "team": "YourTeam",
    "project": "YourProject"
  }
}
```

If no config exists, Claude will interactively query Linear to help you set it up.

## Workflow

```
Plan Mode → Create/Find Issue → Create Branch → Work → PR → Merge
```

### 1. Starting Work

When you try to exit plan mode on `main`, the plugin blocks and guides you to:

1. Search Linear for existing issues
2. Create a new issue if needed
3. Create a branch using Linear's `gitBranchName`

### 2. Branch Naming

Use Linear's suggested branch name:
```
{user}/{prefix}-{id}-{description}
```

Example: `bahamoth/abc-123-add-auth-feature`

### 3. Commit Messages

Follow Conventional Commits format:
```
feat(scope): add new feature

Refs ABC-123
```

Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`, `revert`

### 4. Pull Requests

Include Linear magic words to auto-close issues:
```
Fixes ABC-123
```

## Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| `pre_implement_check.py` | `ExitPlanMode` | Enforce Linear branch before implementation |
| `validate_commit_msg.py` | `Bash (git commit)` | Validate Conventional Commits |
| `record_progress.py` | `Write`, `Edit` | Track file changes |

## License

MIT
