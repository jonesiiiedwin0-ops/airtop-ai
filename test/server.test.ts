import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { TextContent } from "@modelcontextprotocol/sdk/types.js";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { createWinstonAiServer } from "../src/server.js";

let client: Client;
let server: McpServer;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function firstText(content: unknown): string {
  if (!Array.isArray(content)) {
    throw new Error("Expected MCP content array");
  }

  const textContent = content.find((item): item is TextContent => {
    return isRecord(item) && item["type"] === "text" && typeof item["text"] === "string";
  });

  if (textContent === undefined) {
    throw new Error("Expected text content");
  }

  return textContent.text;
}

function firstResourceText(
  contents: Array<{ text: string } | { blob: string }>,
): string {
  const first = contents[0];
  if (first === undefined || !("text" in first)) {
    throw new Error("Expected text resource content");
  }

  return first.text;
}

beforeEach(async () => {
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  server = createWinstonAiServer();
  client = new Client({ name: "winston-ai-test-client", version: "1.0.0" });

  await server.connect(serverTransport);
  await client.connect(clientTransport);
});

afterEach(async () => {
  await client.close();
  await server.close();
});

describe("Winston AI MCP server", () => {
  it("advertises the official server identity and public tools", async () => {
    expect(client.getServerVersion()).toEqual({ name: "Winston AI", version: "1.0.0" });
    expect(client.getInstructions()).toContain("strategic planning");

    const { tools } = await client.listTools();

    expect(tools.map((tool) => tool.name).sort()).toEqual([
      "winston_launch_brief",
      "winston_score_initiative",
      "winston_year_one_outline",
    ]);
  });

  it("returns the year-one outline with MCP usage evidence", async () => {
    const result = await client.callTool({
      name: "winston_year_one_outline",
      arguments: { focus: "security" },
    });

    const text = firstText("content" in result ? result.content : undefined);
    const structuredContent = "structuredContent" in result ? result.structuredContent : undefined;

    expect(text).toContain("Security scan reports no blocking findings");
    if (!isRecord(structuredContent) || !Array.isArray(structuredContent["stages"])) {
      throw new Error("Expected structured stages");
    }
    expect(
      structuredContent["stages"].some(
        (stage) =>
          isRecord(stage) &&
          stage["quarter"] === "Q1" &&
          stage["theme"] === "Official server foundation",
      ),
    ).toBe(true);
  });

  it("scores initiatives and produces structured recommendations", async () => {
    const result = await client.callTool({
      name: "winston_score_initiative",
      arguments: {
        name: "Hosted MCP transport",
        userImpact: 5,
        strategicFit: 5,
        revenuePotential: 4,
        urgency: 4,
        effort: 2,
        risk: 2,
      },
    });

    expect(firstText("content" in result ? result.content : undefined)).toContain(
      "Recommendation: commit",
    );
    const structuredContent = "structuredContent" in result ? result.structuredContent : undefined;
    expect(structuredContent).toMatchObject({
      name: "Hosted MCP transport",
      recommendation: "commit",
    });
  });

  it("serves resources and prompts for launch planning", async () => {
    const resources = await client.listResources();
    expect(resources.resources.map((resource) => resource.uri).sort()).toEqual([
      "winston://governance/operating-model",
      "winston://roadmap/year-one",
    ]);

    const outlineResource = await client.readResource({ uri: "winston://roadmap/year-one" });
    expect(firstResourceText(outlineResource.contents)).toContain("# Winston AI Year-One Outline");

    const prompt = await client.getPrompt({
      name: "winston_official_launch_plan",
      arguments: {
        objective: "Launch Winston AI as an official planning server",
        audience: "AI platform teams",
      },
    });

    expect(firstText(prompt.messages[0]?.content === undefined ? [] : [prompt.messages[0].content])).toContain(
      "Launch Winston AI as an official planning server",
    );
  });
});
