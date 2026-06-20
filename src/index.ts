#!/usr/bin/env node
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

import { createWinstonAiServer } from './server.js';

async function main(): Promise<void> {
  const server = createWinstonAiServer();
  const transport = new StdioServerTransport();

  await server.connect(transport);
  console.error('Winston AI MCP server running on stdio.');
}

main().catch((error: unknown) => {
  console.error('Fatal error starting Winston AI MCP server:', error);
  process.exit(1);
});
