# Claude Linear Workflow Plugin

## Development Notes

### Hook Auto-Loading
- When working in this directory, `hooks/hooks.json` is **automatically loaded as project hooks**
- Disabling the plugin via `enabledPlugins` does NOT stop hooks (they're project hooks, not plugin hooks)
- Ignore UserPromptSubmit/PreToolUse hook messages during development

### Environment Variable Warnings
- Warnings about missing LINEAR_WORKFLOW_TEAM, LINEAR_WORKFLOW_PROJECT may appear
- Safe to ignore when developing this plugin itself

## Plugin Structure

### Hook Loading
- `hooks` field in `plugin.json` is **NOT required** (default path `hooks/hooks.json` auto-loads)
- Official plugins (e.g., security-guidance) use the same pattern

### Trigger Design
- `ExitPlanMode`: Validates Linear issue/branch when exiting Plan Mode
- `Write|Edit`: Validates branch on file modifications (session-cached for performance)
- `Bash`: Validates commit message format
- `PreCompact`: Syncs progress to Linear

## Testing

Test the plugin in another project:
```bash
# Verify plugin is enabled
claude /plugins

# Set environment variables (.claude/settings.json)
{
  "env": {
    "LINEAR_WORKFLOW_TEAM": "YourTeam",
    "LINEAR_WORKFLOW_PROJECT": "YourProject"
  }
}
```
