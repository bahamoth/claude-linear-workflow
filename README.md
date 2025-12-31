# Linear Workflow Plugin for Claude Code

A Claude Code plugin that enforces Linear issue-tracked development workflow with branch naming conventions, Conventional Commits validation, and automatic issue tracking.

## Features

- **Branch enforcement**: Blocks implementation without a Linear issue and related branch
- **Commit validation**: Enforces Conventional Commits format
- **Seamless Linear sync**: Works with existing issues or creates new ones on the fly-either way, Linear stays in sync
- **Consistent shared context with Linear issue tracking**: Logs progress to Linear issue comments - one source of truth across sessions and teammates

## Prerequisites

- [Claude Code](https://claude.com/claude-code) CLI
- [GitHub + Linear integration](https://linear.app/docs/github-integration) - enables PR auto-linking and issue status sync on merge
- Git repository

## Installation

```bash
# 1. Add marketplace
/plugin marketplace add bahamoth/claude-marketplace
# Or host your own marketplace - see https://code.claude.com/docs/en/plugin-marketplaces

# 2. Install plugin
/plugin install linear-workflow@bahamoth/claude-marketplace

# 3. Enable plugin
/plugin enable linear-workflow

# 4. Authenticate Linear MCP (opens browser for OAuth)
/mcp linear-mcp auth
```

## Configuration

Add your Linear team and project to `.claude/settings.json`:

```json
{
  "env": {
    "LINEAR_WORKFLOW_TEAM": "YourTeam",
    "LINEAR_WORKFLOW_PROJECT": "YourProject"
  }
}
```

If no config exists, the plugin will block implementation and guide you to set it up.

## Workflow Overview

```
Has Issue                    No Issue
    │                            │
    ▼                            ▼
Query via MCP          Plan → Create Issue in Linear
    │                            │
    └──────────┬─────────────────┘
               ▼
    Create branch (use gitBranchName)
               ▼
    Linear status: In Progress + start comment
               ▼
    Work (comment on decisions/blockers)
               ▼
    Create PR (Fixes {PREFIX}-XX)
               ▼
    Merge (rebase-ff) → Linear auto-Done
```

### 1. Starting Work

When you try to exit plan mode on `main`, the plugin blocks and guides you to:

1. Search Linear for existing issues
2. Create a new issue if needed
3. Create a branch using Linear's `gitBranchName`

### 2. Branch Naming

Use the `gitBranchName` field from the Linear issue:

```bash
git checkout -b <gitBranchName>
```

Branch format is configured in Linear: **Settings > Workspace > Integrations > Branch format**

### 3. Commit Messages

Follow Conventional Commits format:

```
type(scope): description

Refs ABC-123
```

Format: `type(scope): description` where type is any lowercase word (commonly `feat`, `fix`, `docs`, `refactor`, etc.)

### 4. Pull Requests

Include Linear magic words to auto-close issues:

```
Fixes ABC-123
```

## Hooks

| Hook                       | Trigger                     | Purpose                                     |
| -------------------------- | --------------------------- | ------------------------------------------- |
| `check_linear_env.py`      | `UserPromptSubmit`          | Early warning if env not configured         |
| `ensure_linear_branch.py`  | `Write`, `Edit`, `ExitPlanMode` | Enforce Linear branch before implementation |
| `validate_commit_msg.py`   | `Bash (git commit)`         | Validate Conventional Commits               |
| PreCompact prompt          | `PreCompact`                | Sync progress to Linear comments            |

## License

MIT
