# Winston AI MCP Server

Official MCP server for Winston AI, a planning and execution assistant that turns goals into one-year outlines, decision briefs, and launch checklists.

## Capabilities

- `winston_capabilities` - list the server purpose and public tools.
- `winston_plan_year` - create a quarterly or monthly one-year execution outline.
- `winston_decision_brief` - compare options and produce a recommendation with tradeoffs.
- `winston_execution_checklist` - turn deliverables into ownership, validation, and launch-readiness tasks.

## Local development

```bash
npm install
npm run build
npm test
```

Run the server over stdio:

```bash
npm run dev
```

## MCP client configuration

After building, add this server to an MCP client configuration:

```json
{
  "servers": {
    "winston-ai": {
      "type": "stdio",
      "command": "node",
      "args": ["./dist/index.js"]
    }
  }
}
```

During development, use:

```json
{
  "servers": {
    "winston-ai": {
      "type": "stdio",
      "command": "npm",
      "args": ["run", "dev"]
    }
  }
}
```

## Quality checks

```bash
npm run check
```

This runs TypeScript type checking, the Vitest suite, and a high-severity npm audit.
