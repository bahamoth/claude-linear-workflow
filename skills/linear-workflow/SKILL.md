---
name: linear-workflow
description: Linear issue-tracked development workflow. Auto-activates when starting work on issues, creating branches, changing status, writing comments, or creating PRs.
---

# Linear-Tracked Development Workflow

## Configuration

This skill requires Linear MCP to be configured. On first use:

1. **Check environment variables** in `.claude/settings.json`:

   - If `LINEAR_WORKFLOW_TEAM` and `LINEAR_WORKFLOW_PROJECT` exist → use them
   - If not → hook blocks implementation and guides you to set them up

2. **Get issue prefix** dynamically:
   ```bash
   mcp__linear__list_issues(team: "{LINEAR_WORKFLOW_TEAM}", limit: 1)
   # Extract prefix from identifier (e.g., "ABC-34" → "ABC")
   ```

### Example settings.json

```json
{
  "env": {
    "LINEAR_WORKFLOW_TEAM": "YourTeam",
    "LINEAR_WORKFLOW_PROJECT": "YourProject"
  }
}
```

> **Note**: `issuePrefix` is auto-detected from Linear, no manual config needed.

---

## Auto-Activation Triggers

- Starting code implementation
- Mentioning a Linear issue ({PREFIX}-XX)
- After planning, before implementation
- Creating a PR

## Hook Enforcement

A `PreToolUse` hook on `ExitPlanMode` enforces this workflow:

- **Blocks** implementation on `main`/`master` branch
- **Allows** if branch contains issue ID pattern (e.g., `abc-7`)

If blocked, you must:

1. Search Linear for similar issues matching your plan
2. If similar issue exists → ask user which to use
3. If no match → create new issue from plan
4. Create branch using `gitBranchName` from issue
5. Then exit plan mode again

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

---

## 1. Check or Create Issue

### Case A: Starting with Existing Issue

```bash
# Query issue via MCP
mcp__linear__get_issue(id: "{PREFIX}-XX")
```

- Use `gitBranchName` field as branch name
- Check Acceptance Criteria in issue description

### Case B: Starting without Issue

After planning, before implementation, create Linear issue using this template:

```bash
mcp__linear__create_issue(
  title: "Concise work title",
  description: "<issue description template below>",
  team: "{LINEAR_WORKFLOW_TEAM}",
  project: "{LINEAR_WORKFLOW_PROJECT}"
)
```

### Issue Description Template

```markdown
## Objective

[One sentence describing what this work achieves]

## Background

- [Why this work is needed]
- [Context or constraints]
- [Related prior work or decisions]

## Implementation Approach

- [High-level approach or strategy]
- [Key technical decisions]
- [Files/components to modify]

## Acceptance Criteria

- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]
```

**Guidelines:**

- **Objective**: Single sentence, action-oriented (e.g., "Add logging infrastructure for LLM debugging")
- **Background**: 2-4 bullet points explaining why, not how
- **Implementation Approach**: Technical strategy, not step-by-step instructions
- **Acceptance Criteria**: Checkboxes, testable conditions for "done"

---

## 2. Create Branch

Use Linear's `gitBranchName` field as-is:

```bash
git checkout -b {user}/{prefix}-XX-short-description
```

Pattern: `{user}/{issue-id}-{short-description}`

---

## 3. Update Status + Start Comment

```bash
# Update status
mcp__linear__update_issue(id: "{PREFIX}-XX", state: "In Progress")

# Start comment
mcp__linear__create_comment(
  issueId: "{PREFIX}-XX",
  body: "## Started\n\n- Branch: `{user}/{prefix}-XX-...`\n- Implementing ..."
)
```

---

## 4. Comments During Work

Write comments for major decisions, progress updates, or blockers.

**Language**: English only (for global team collaboration)

### Progress Update

```markdown
## Progress Update

- Completed: [what was done]
- In Progress: [current work]
- Next: [upcoming tasks]
```

### Technical Decision

```markdown
## Decision: [title]

**Context**: [why this decision was needed]

**Options considered**:

1. [Option A] - pros/cons
2. [Option B] - pros/cons

**Chosen**: [option] because [reason]
```

### Blocked

```markdown
## Blocked

**Issue**: [description]
**Waiting on**: [dependency/person]
**Workaround**: [if any]
```

---

## 5. Commit Rules

Conventional Commits + Linear reference:

```bash
git commit -m "feat(scope): implement feature

Refs {PREFIX}-XX"
```

### Commit Types

**SemVer-relevant (required for versioning):**

| Type   | Usage       | SemVer Impact |
| ------ | ----------- | ------------- |
| `feat` | New feature | MINOR bump    |
| `fix`  | Bug fix     | PATCH bump    |
| !      | Breaking change (e.g., feat!:) | MAJOR bump |

**Other common types:**

`docs`, `refactor`, `test`, `chore`, `style`, `perf`, `ci`, `build`, `revert`, or any lowercase word that fits the change.

### Linear Reference Keywords

- `Refs {PREFIX}-XX`: Link only (no status change)
- `Closes {PREFIX}-XX`: Auto-close issue on PR merge

---

## 6. Create PR

### PR Title

Conventional Commit format:

```
feat(linear): add workflow skills
```

### PR Body

```markdown
## Summary

- [Change 1]
- [Change 2]

## Test Plan

- [ ] Test item 1
- [ ] Test item 2

Fixes {PREFIX}-XX
```

### PR Creation Command

```bash
gh pr create --title "feat(scope): description" --body "$(cat <<'EOF'
## Summary
- ...

## Test Plan
- [ ] ...

Fixes {PREFIX}-XX

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## 7. Merge

GitHub standard method (rebase-ff):

```bash
# After PR approval
gh pr merge --rebase
```

Linear detects `Fixes {PREFIX}-XX` → auto-closes issue as Done

---

## Linear Magic Words Reference

| Keyword                                    | Effect                      |
| ------------------------------------------ | --------------------------- |
| `closes`, `fixes`, `resolves`, `completes` | Close issue on PR merge     |
| `refs`, `part of`, `related to`            | Link only, no status change |

---

## Checklist

### When Starting Work

- [ ] Check if issue exists (create if not)
- [ ] Create branch using `gitBranchName`
- [ ] Status → In Progress
- [ ] Write start comment

### During Work

- [ ] Comment on major decisions/blockers
- [ ] Follow Conventional Commits
- [ ] Include `Refs {PREFIX}-XX` in commits

### On Completion

- [ ] Create PR (include `Fixes {PREFIX}-XX`)
- [ ] Request code review
- [ ] Merge (rebase-ff)
- [ ] Verify Linear auto-Done
