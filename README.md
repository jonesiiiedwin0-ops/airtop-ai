# Airtop AI Cursor Plugin

A Cursor plugin for building Airtop AI browser automation integrations. It gives agents concise guidance for Airtop sessions, windows, page queries, natural-language interactions, authentication handoffs, and reliable cleanup.

## What is included

- `.cursor-plugin/plugin.json` - plugin manifest.
- `rules/airtop-api.mdc` - always-on Airtop API implementation guardrails.
- `skills/airtop-api-integration/SKILL.md` - workflow for adding or changing Airtop integrations.
- `agents/airtop-automation-architect.md` - specialist agent prompt for designing Airtop browser workflows.
- `scripts/validate-plugin.mjs` - zero-dependency scaffold validator.

## Install locally

Clone or copy this directory into Cursor's local plugin directory:

```bash
mkdir -p ~/.cursor/plugins/local
cp -R . ~/.cursor/plugins/local/airtop-ai
```

Then restart Cursor or reload plugins from Cursor settings.

## Validate

```bash
npm run validate
```

The validator checks the manifest, safe component paths, frontmatter, and expected plugin files.

## Airtop development notes

- Store credentials in environment variables such as `AIRTOP_API_KEY`; never hardcode API keys.
- Prefer the official Airtop TypeScript or Python SDK when a project already uses one.
- Use page queries for extraction and question answering, and include JSON schemas when downstream code needs structured output.
- Perform natural-language page interactions sequentially and wait after navigation, reloads, animations, or dynamic content changes.
- Always terminate sessions or document why a session must remain open.
