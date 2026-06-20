# Winston AI official server

Winston AI is an official Model Context Protocol (MCP) server for planning, launching, and operating the Winston AI roadmap.

The first release provides a local stdio server with:

- A complete 12-month official server outline.
- MCP tools for roadmap lookup, milestone planning, and launch readiness checks.
- MCP resources for server status and the year-one roadmap.
- An MCP prompt for audience-specific execution briefs.

## Install

```bash
npm install
npm run build
```

## Run

```bash
npm start
```

The server uses stdio, so logs are written to stderr and stdout remains reserved for MCP JSON-RPC messages.

## MCP client configuration

The repository includes `.vscode/mcp.json`:

```json
{
  "servers": {
    "winston-ai": {
      "type": "stdio",
      "command": "node",
      "args": ["./build/index.js"]
    }
  }
}
```

Build before starting the server from an MCP client.

## Capabilities

### Tools

- `get-year-one-outline`: Returns the full roadmap, a quarter, or a month.
- `plan-milestone`: Converts a roadmap month into an execution-ready milestone.
- `assess-launch-readiness`: Reviews launch readiness and planned deferred areas.

### Resources

- `winston://status`: Server identity, version, transport, and posture.
- `winston://roadmap/year-one`: Markdown year-one outline.

### Prompt

- `year-one-execution-brief`: Generates an execution brief for engineering, leadership, or operations.

## Test

```bash
npm test
```

The test suite builds the server, launches it through an MCP stdio client, and verifies tools, resources, and prompts end-to-end.

## Roadmap

See `docs/year-one-outline.md` for the complete one-year outline.
