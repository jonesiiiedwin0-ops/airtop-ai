# Winston AI

Winston AI is a Cursor plugin for turning broad goals into practical 1-year execution outlines. It helps teams create quarterly plans with measurable outcomes, explicit assumptions, risks, decision gates, and follow-up checkpoints.

## Components

| Component | Path | Purpose |
| --- | --- | --- |
| Rule | `rules/winston-planning.mdc` | Sets planning standards for yearly outlines and roadmap work. |
| Skill | `skills/one-year-outline/SKILL.md` | Provides a reusable workflow for creating 12-month plans. |
| Command | `commands/one-year-outline.md` | Gives users a direct prompt for generating a 1-year outline. |
| Agent | `agents/winston-ai-strategist.md` | Defines a dedicated strategy-planning persona. |

## Installation

For local use, copy this plugin folder to:

```text
~/.cursor/plugins/local/winston-ai/
```

This repository also mirrors the same plugin under `plugins/winston-ai/` so the scaffold can be reviewed, versioned, and submitted.

## Usage

Ask Cursor to use Winston AI for a broad goal:

```text
Use Winston AI to create a 1-year outline for launching our customer education program.
```

Or invoke the included command prompt:

```text
/one-year-outline
```

## 1-Year Official Plugin Outline

This is the initial 12-month outline for taking Winston AI from scaffold to a durable official plugin.

### Quarter 1: Foundation and validation

- Ship the first local plugin scaffold with manifest, README, rule, skill, command, and strategist agent.
- Validate all component metadata, frontmatter, and relative paths.
- Define the first target user profile: operators, founders, product leads, and engineering leads who need practical yearly plans.
- Collect example prompts and expected outputs for company, product, engineering, and personal operating plans.
- Success metrics:
  - Plugin loads locally without path or metadata errors.
  - At least four high-quality example outlines are documented.
  - The planning skill produces consistent quarterly structure.

### Quarter 2: Workflow depth

- Add examples for strategy reviews, roadmap refreshes, product launches, fundraising plans, and operational turnarounds.
- Expand the skill with variants for startup, enterprise, nonprofit, and individual planning contexts.
- Add optional review checklists for assumptions, dependencies, risks, and measurable outcomes.
- Evaluate whether a lightweight hook is useful for validating generated planning documents.
- Success metrics:
  - Users can create first-pass outlines without follow-up clarification for common scenarios.
  - Review checklists catch missing metrics, owners, and decision gates.
  - No unnecessary hooks or MCP servers are added without a real workflow need.

### Quarter 3: Ecosystem integration

- Document how Winston AI should consult relevant installed plugins, docs, and MCP tools when a plan depends on a specific platform.
- Add guidance for technology-specific planning without forcing irrelevant integrations.
- Introduce more domain examples, such as AI products, data platforms, support operations, and developer tools.
- Prepare marketplace-facing docs, screenshots, and release notes.
- Success metrics:
  - The plugin clearly explains when to use external context.
  - Generated plans cite dependencies and platform constraints when relevant.
  - Marketplace submission materials are complete.

### Quarter 4: Official readiness

- Harden the plugin through repeated validation, real planning examples, and user feedback.
- Finalize the official plugin positioning, README, changelog, and contribution notes.
- Add only the components that have proven value in repeated use.
- Prepare a stable `1.0.0` release candidate.
- Success metrics:
  - All metadata and component paths pass validation.
  - Documentation is concise, current, and complete.
  - The plugin has a clear scope and avoids unrelated automation.

## Quality Gates

Run the local validator from the repository root:

```bash
node scripts/validate-plugin.mjs plugins/winston-ai
```

Manual checks:

- `.cursor-plugin/plugin.json` exists and contains `name: "winston-ai"`.
- Every manifest path is relative and points to an existing file.
- Rule, skill, command, and agent files include YAML frontmatter.
- The skill frontmatter name matches its directory: `one-year-outline`.
- The plugin does not include hooks or MCP servers without a concrete need.

## Scope

Winston AI is intentionally focused on strategic planning and execution outlines. It should use relevant installed plugins or MCP tools when a user goal depends on a specific platform, but it should not attempt to invoke every installed plugin indiscriminately.
