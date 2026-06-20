# Winston AI

Winston AI is the official Airtop AI orchestration plugin for creating governed
execution outlines across the installed plugin ecosystem.

## Purpose

Winston AI turns the available installed plugins into a staged execution plan.
Every outline produced by the plugin must include every installed plugin at
least once, which keeps platform operators from accidentally excluding a
capability during planning.

## Official metadata

- Plugin ID: `winston-ai`
- Display name: `Winston AI`
- Entrypoint: `airtop_ai.plugins.winston_ai:WinstonAIPlugin`
- Status: `official`
- Version: `0.1.0`

## 1-year outline

The official Winston AI outline is expressed as four ordered stages:

1. **Foundation** - publish the official manifest, define plugin contracts, and
   establish validation that every installed plugin is represented.
2. **Integration** - map each installed plugin into Winston AI workflows and
   expose cross-plugin execution reports.
3. **Automation** - convert repeatable cross-plugin workflows into governed
   automations with approval gates and audit summaries.
4. **Optimization** - measure plugin coverage, tune workflow routing, and
   prepare promotion criteria for the next official release.

## Example

```python
from airtop_ai.plugins import WinstonAIPlugin

plugin = WinstonAIPlugin()
plan = plugin.build_one_year_outline([
    "data-importer",
    "workflow-runner",
    "notification-hub",
])

assert plan.uses_all_installed_plugins
```
