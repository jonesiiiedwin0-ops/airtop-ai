import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

import {
  YEAR_ONE_OUTLINE,
  createLaunchBrief,
  formatYearOneOutline,
  scoreInitiative,
} from "./roadmap.js";

const scoreField = z.number().int().min(1).max(5);

const roadmapStageSchema = z.object({
  quarter: z.enum(["Q1", "Q2", "Q3", "Q4"]),
  theme: z.string(),
  outcomes: z.array(z.string()),
  execution: z.array(z.string()),
  mcpUsage: z.array(z.string()),
  proof: z.array(z.string()),
});

const initiativeScoreSchema = z.object({
  name: z.string(),
  score: z.number().int().min(0).max(100),
  recommendation: z.enum(["commit", "sequence", "defer"]),
  rationale: z.array(z.string()),
});

export const WINSTON_AI_SERVER_NAME = "Winston AI";
export const WINSTON_AI_SERVER_VERSION = "1.0.0";

export function createWinstonAiServer(): McpServer {
  const server = new McpServer(
    {
      name: WINSTON_AI_SERVER_NAME,
      version: WINSTON_AI_SERVER_VERSION,
    },
    {
      instructions:
        "Use Winston AI for strategic planning, launch execution, initiative scoring, and MCP-backed operating discipline.",
    },
  );

  server.registerTool(
    "winston_year_one_outline",
    {
      title: "Winston AI Year-One Outline",
      description:
        "Return Winston AI's executable one-year official-server outline, optionally focused by keyword.",
      inputSchema: z.object({
        focus: z
          .string()
          .trim()
          .min(1)
          .optional()
          .describe("Optional keyword such as security, hosted, docs, launch, or MCP."),
      }),
      outputSchema: z.object({
        outline: z.string(),
        stages: z.array(roadmapStageSchema),
      }),
    },
    ({ focus }) => {
      const outline = formatYearOneOutline(focus);
      const normalizedFocus = focus?.toLowerCase();
      const stages =
        normalizedFocus === undefined
          ? YEAR_ONE_OUTLINE
          : YEAR_ONE_OUTLINE.filter((stage) =>
              [
                stage.theme,
                ...stage.outcomes,
                ...stage.execution,
                ...stage.mcpUsage,
                ...stage.proof,
              ].some((value) => value.toLowerCase().includes(normalizedFocus)),
            );
      const structuredContent = {
        outline,
        stages: stages.length > 0 ? stages : YEAR_ONE_OUTLINE,
      };

      return {
        content: [{ type: "text" as const, text: outline }],
        structuredContent,
      };
    },
  );

  server.registerTool(
    "winston_score_initiative",
    {
      title: "Winston AI Initiative Score",
      description:
        "Score a candidate Winston AI initiative on impact, fit, revenue, urgency, effort, and risk.",
      inputSchema: z.object({
        name: z.string().trim().min(1),
        userImpact: scoreField.describe("User impact from 1 low to 5 high."),
        strategicFit: scoreField.describe("Strategic fit from 1 low to 5 high."),
        revenuePotential: scoreField.describe("Revenue potential from 1 low to 5 high."),
        urgency: scoreField.describe("Urgency from 1 low to 5 high."),
        effort: scoreField.describe("Implementation effort from 1 low to 5 high."),
        risk: scoreField.describe("Execution or security risk from 1 low to 5 high."),
      }),
      outputSchema: initiativeScoreSchema,
    },
    (input) => {
      const structuredContent = scoreInitiative(input);
      return {
        content: [
          {
            type: "text" as const,
            text: [
              `${structuredContent.name}: ${String(structuredContent.score)}/100`,
              `Recommendation: ${structuredContent.recommendation}`,
              ...structuredContent.rationale,
            ].join("\n"),
          },
        ],
        structuredContent,
      };
    },
  );

  server.registerTool(
    "winston_launch_brief",
    {
      title: "Winston AI Launch Brief",
      description:
        "Create a concise launch brief with constraints, success metrics, and an MCP-backed execution path.",
      inputSchema: z.object({
        objective: z.string().trim().min(1),
        audience: z.string().trim().min(1),
        timeframe: z.string().trim().min(1),
        constraints: z.array(z.string().trim().min(1)).min(1),
        successMetrics: z.array(z.string().trim().min(1)).min(1),
      }),
      outputSchema: z.object({
        brief: z.string(),
      }),
    },
    (input) => {
      const brief = createLaunchBrief(input);
      return {
        content: [{ type: "text" as const, text: brief }],
        structuredContent: { brief },
      };
    },
  );

  server.registerResource(
    "winston-year-one-outline",
    "winston://roadmap/year-one",
    {
      title: "Winston AI Year-One Outline",
      description: "The official Winston AI one-year execution outline.",
      mimeType: "text/markdown",
    },
    (uri) => ({
      contents: [
        {
          uri: uri.href,
          mimeType: "text/markdown",
          text: `# Winston AI Year-One Outline\n\n${formatYearOneOutline()}`,
        },
      ],
    }),
  );

  server.registerResource(
    "winston-operating-model",
    "winston://governance/operating-model",
    {
      title: "Winston AI Operating Model",
      description: "Operating principles for official Winston AI server governance.",
      mimeType: "text/markdown",
    },
    (uri) => ({
      contents: [
        {
          uri: uri.href,
          mimeType: "text/markdown",
          text: [
            "# Winston AI Operating Model",
            "",
            "- Keep MCP tools deterministic unless credentials and data access are explicitly configured.",
            "- Treat resources and prompts as public contracts with semantic versioning.",
            "- Validate every release with protocol tests, security scanning, and dependency audit.",
            "- Use MCP-backed documentation, telemetry, issue, and security sources for launch evidence.",
          ].join("\n"),
        },
      ],
    }),
  );

  server.registerPrompt(
    "winston_official_launch_plan",
    {
      title: "Winston AI Official Launch Plan",
      description: "Draft a launch plan using Winston AI's year-one operating model.",
      argsSchema: {
        objective: z.string().describe("The launch objective."),
        audience: z.string().describe("The audience or customer segment."),
      },
    },
    ({ objective, audience }) => ({
      messages: [
        {
          role: "user" as const,
          content: {
            type: "text" as const,
            text: [
              `Create a Winston AI launch plan for: ${objective}`,
              `Audience: ${audience}`,
              "Use the winston://roadmap/year-one resource and call Winston AI tools for prioritization evidence.",
            ].join("\n"),
          },
        },
      ],
    }),
  );

  server.registerPrompt(
    "winston_risk_review",
    {
      title: "Winston AI Risk Review",
      description: "Review a planned initiative for operational, security, and delivery risk.",
      argsSchema: {
        initiative: z.string().describe("The initiative to review."),
      },
    },
    ({ initiative }) => ({
      messages: [
        {
          role: "user" as const,
          content: {
            type: "text" as const,
            text: [
              `Review this Winston AI initiative: ${initiative}`,
              "Identify blocking risks, MCP evidence sources to check, and the minimum proof needed before launch.",
            ].join("\n"),
          },
        },
      ],
    }),
  );

  return server;
}
