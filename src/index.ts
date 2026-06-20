#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import {
  createDecisionBrief,
  createExecutionChecklist,
  createYearPlan,
  getCapabilities,
} from "./winston.js";

const server = new McpServer({
  name: "Winston AI",
  version: "1.0.0",
});

const yearPlanOutputSchema = {
  serverName: z.literal("Winston AI"),
  objective: z.string(),
  audience: z.string(),
  operatingPrinciples: z.array(z.string()),
  phases: z.array(z.object({
    label: z.string(),
    theme: z.string(),
    goals: z.array(z.string()),
    deliverables: z.array(z.string()),
    validation: z.array(z.string()),
    risks: z.array(z.string()),
  })),
  executionCadence: z.array(z.string()),
};

server.registerTool(
  "winston_capabilities",
  {
    title: "Winston AI Capabilities",
    description: "Describe the Winston AI official MCP server and its available planning tools.",
    inputSchema: {},
  },
  async () => {
    const output = getCapabilities();
    return asStructuredResult(output);
  },
);

server.registerTool(
  "winston_plan_year",
  {
    title: "Create One-Year Outline",
    description: "Create a one-year strategic execution outline for a goal or initiative.",
    inputSchema: {
      objective: z.string().min(1).describe("The strategic goal Winston AI should plan around."),
      audience: z.string().optional().describe("The intended users, stakeholders, or operators."),
      constraints: z.array(z.string()).optional().describe("Constraints Winston AI should respect."),
      focusAreas: z.array(z.string()).optional().describe("Focus areas to cycle through in the outline."),
      horizon: z.enum(["quarterly", "monthly"]).optional().describe("Quarterly or monthly outline granularity."),
    },
    outputSchema: yearPlanOutputSchema,
  },
  async (input) => {
    const output = createYearPlan(input);
    return asStructuredResult(output);
  },
);

server.registerTool(
  "winston_decision_brief",
  {
    title: "Create Decision Brief",
    description: "Compare options and produce a concise recommendation with tradeoffs and next steps.",
    inputSchema: {
      decision: z.string().min(1).describe("The decision to make."),
      options: z.array(z.string().min(1)).min(2).describe("Candidate options in priority order."),
      successCriteria: z.array(z.string()).optional().describe("Criteria used to evaluate the options."),
      constraints: z.array(z.string()).optional().describe("Constraints or risks to account for."),
    },
    outputSchema: {
      decision: z.string(),
      recommendedOption: z.string(),
      rationale: z.array(z.string()),
      tradeoffs: z.array(z.string()),
      nextSteps: z.array(z.string()),
    },
  },
  async (input) => {
    const output = createDecisionBrief(input);
    return asStructuredResult(output);
  },
);

server.registerTool(
  "winston_execution_checklist",
  {
    title: "Create Execution Checklist",
    description: "Turn deliverables into validation, ownership, and launch-readiness checklist items.",
    inputSchema: {
      initiative: z.string().min(1).describe("The initiative being executed."),
      phase: z.string().min(1).describe("The plan phase this checklist covers."),
      deliverables: z.array(z.string().min(1)).min(1).describe("Deliverables that need execution coverage."),
      riskLevel: z.enum(["low", "medium", "high"]).optional().describe("Execution risk level."),
    },
    outputSchema: {
      initiative: z.string(),
      phase: z.string(),
      riskLevel: z.enum(["low", "medium", "high"]),
      checklist: z.array(z.string()),
    },
  },
  async (input) => {
    const output = createExecutionChecklist(input);
    return asStructuredResult(output);
  },
);

async function main(): Promise<void> {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Winston AI MCP server running on stdio.");
}

function asStructuredResult<T extends object>(output: T) {
  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(output, null, 2),
      },
    ],
    structuredContent: output,
  };
}

await main();
