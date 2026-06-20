import assert from 'node:assert/strict';
import { test } from 'node:test';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const repoRoot = dirname(dirname(fileURLToPath(import.meta.url)));

test('Winston AI server exposes official MCP capabilities over stdio', async () => {
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [join(repoRoot, 'build/index.js')],
    cwd: repoRoot,
    stderr: 'pipe'
  });
  const client = new Client(
    {
      name: 'winston-ai-test-client',
      version: '0.1.0'
    },
    {
      capabilities: {}
    }
  );

  await client.connect(transport);

  try {
    const tools = await client.listTools();
    const toolNames = tools.tools.map((tool) => tool.name).sort();
    assert.deepEqual(toolNames, [
      'assess-launch-readiness',
      'get-year-one-outline',
      'plan-milestone'
    ]);

    const resources = await client.listResources();
    const resourceUris = resources.resources.map((resource) => resource.uri).sort();
    assert.deepEqual(resourceUris, ['winston://roadmap/year-one', 'winston://status']);

    const status = await client.readResource({ uri: 'winston://status' });
    assert.match(status.contents[0].text, /"name": "Winston AI"/);

    const outline = await client.callTool({
      name: 'get-year-one-outline',
      arguments: { detail: 'quarter', quarter: 3 }
    });
    assert.match(outline.content[0].text, /Official launch candidate/);

    const milestone = await client.callTool({
      name: 'plan-milestone',
      arguments: { month: 8, owner: 'Launch team' }
    });
    assert.match(milestone.content[0].text, /Official launch/);
    assert.match(milestone.content[0].text, /Launch team/);

    const readiness = await client.callTool({
      name: 'assess-launch-readiness',
      arguments: { includeDeferred: true }
    });
    assert.match(readiness.content[0].text, /Hosted deployment/);

    const prompts = await client.listPrompts();
    assert.deepEqual(
      prompts.prompts.map((prompt) => prompt.name),
      ['year-one-execution-brief']
    );

    const prompt = await client.getPrompt({
      name: 'year-one-execution-brief',
      arguments: { audience: 'engineering', quarter: '1' }
    });
    assert.match(prompt.messages[0].content.text, /engineering execution brief/);
    assert.match(prompt.messages[0].content.text, /Official foundation/);
  } finally {
    await client.close();
  }
});
