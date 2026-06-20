# Winston AI MCP Server

Official Winston AI server for the Model Context Protocol (MCP). It provides deterministic planning, prioritization, and launch-execution workflows that AI clients can call over stdio.

## What it exposes

- Tools: `winston_year_one_outline`, `winston_score_initiative`, `winston_launch_brief`
- Resources: `winston://roadmap/year-one`, `winston://governance/operating-model`
- Prompts: `winston_official_launch_plan`, `winston_risk_review`

## Quickstart

```bash
npm install
npm run build
node dist/cli.js
```

Example MCP client configuration:

```json
{
  "mcpServers": {
    "winston-ai": {
      "command": "node",
      "args": ["/absolute/path/to/winston-ai-mcp-server/dist/cli.js"]
    }
  }
}
```

## One-year outline

The server encodes a year-one operating model across four phases:

1. Official server foundation
2. Workflow depth and official adoption
3. Hosted and enterprise-ready surfaces
4. Scale, ecosystem, and governance

See `docs/year-one-outline.md` for the complete outline.

## Development

```bash
npm run lint
npm run build
npm run test
npm audit
```
