#!/usr/bin/env node
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { createWinstonAiServer } from "./server.js";

async function main(): Promise<void> {
  const server = createWinstonAiServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : "Unknown Winston AI server error";
  console.error(message);
  process.exitCode = 1;
});
