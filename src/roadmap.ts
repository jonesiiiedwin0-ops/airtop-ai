export type RoadmapStage = {
  quarter: "Q1" | "Q2" | "Q3" | "Q4";
  theme: string;
  outcomes: string[];
  execution: string[];
  mcpUsage: string[];
  proof: string[];
};

export type InitiativeScoreInput = {
  name: string;
  userImpact: number;
  strategicFit: number;
  revenuePotential: number;
  urgency: number;
  effort: number;
  risk: number;
};

export type InitiativeScore = {
  name: string;
  score: number;
  recommendation: "commit" | "sequence" | "defer";
  rationale: string[];
};

export type LaunchBriefInput = {
  objective: string;
  audience: string;
  timeframe: string;
  constraints: string[];
  successMetrics: string[];
};

export const YEAR_ONE_OUTLINE: RoadmapStage[] = [
  {
    quarter: "Q1",
    theme: "Official server foundation",
    outcomes: [
      "Publish the Winston AI MCP contract with tools, prompts, and resources.",
      "Ship deterministic planning workflows that work without external secrets.",
      "Establish CI checks for build, lint, tests, and dependency audit.",
    ],
    execution: [
      "Define the canonical server name, package metadata, and installation path.",
      "Implement planning, prioritization, and launch-brief tools.",
      "Document local stdio usage and client configuration examples.",
    ],
    mcpUsage: [
      "Use documentation MCP servers to track SDK and hosting guidance.",
      "Use security MCP servers for source and dependency scanning.",
      "Use repository MCP servers when expanding integrations across codebases.",
    ],
    proof: [
      "MCP protocol tests list and call Winston AI tools successfully.",
      "README quickstart starts from a clean checkout.",
      "Security scan reports no blocking findings.",
    ],
  },
  {
    quarter: "Q2",
    theme: "Workflow depth and official adoption",
    outcomes: [
      "Add reusable workflows for product strategy, go-to-market, and operations reviews.",
      "Publish example client configurations for Cursor, Claude Desktop, and CI agents.",
      "Create versioned documentation for every public tool and prompt.",
    ],
    execution: [
      "Add templates for quarterly planning, launch readiness, and risk review.",
      "Introduce compatibility tests for supported MCP clients.",
      "Create contribution guidelines for new Winston AI workflows.",
    ],
    mcpUsage: [
      "Use issue-tracker MCP servers to turn launch feedback into backlog items.",
      "Use documentation MCP servers to keep public guidance current.",
      "Use observability MCP servers once hosted deployments exist.",
    ],
    proof: [
      "Each workflow has at least one MCP protocol test.",
      "Docs link every tool to a concrete operational use case.",
      "Client config examples are validated in automated tests where possible.",
    ],
  },
  {
    quarter: "Q3",
    theme: "Hosted and enterprise-ready surfaces",
    outcomes: [
      "Add an optional remote MCP transport for hosted deployments.",
      "Introduce authentication and tenant-aware policy hooks where hosting requires them.",
      "Publish operational runbooks for deploy, rollback, and incident response.",
    ],
    execution: [
      "Keep stdio as the default path while adding a remote transport behind a separate entrypoint.",
      "Add environment validation for hosted-only settings.",
      "Document data retention, logging, and rate-limit expectations.",
    ],
    mcpUsage: [
      "Use hosting provider MCP servers for deployment guidance.",
      "Use observability MCP servers to validate production behavior.",
      "Use security MCP servers before every hosted release.",
    ],
    proof: [
      "Hosted health checks verify tool listing and a representative tool call.",
      "Security review covers auth, request validation, and logging.",
      "Rollback instructions are tested in a non-production environment.",
    ],
  },
  {
    quarter: "Q4",
    theme: "Scale, ecosystem, and governance",
    outcomes: [
      "Formalize the Winston AI server as the default strategic planning interface.",
      "Add governance for deprecating tools and evolving prompt contracts.",
      "Build ecosystem examples for partner workflows and internal automation.",
    ],
    execution: [
      "Introduce semantic versioning and changelog discipline for MCP surfaces.",
      "Create golden tests that protect public output contracts.",
      "Publish integration examples for common planning and delivery stacks.",
    ],
    mcpUsage: [
      "Use source and docs MCP servers to maintain examples across ecosystems.",
      "Use telemetry MCP servers to understand real usage before changing contracts.",
      "Use security MCP servers to keep release gates continuously enforced.",
    ],
    proof: [
      "Public contracts have backwards-compatibility tests.",
      "Release notes call out every tool, resource, and prompt change.",
      "Usage feedback maps to clear roadmap decisions.",
    ],
  },
];

export function formatYearOneOutline(focus?: string): string {
  const normalizedFocus = focus?.trim().toLowerCase();
  const stages = normalizedFocus
    ? YEAR_ONE_OUTLINE.filter((stage) =>
        [
          stage.theme,
          ...stage.outcomes,
          ...stage.execution,
          ...stage.mcpUsage,
          ...stage.proof,
        ].some((value) => value.toLowerCase().includes(normalizedFocus)),
      )
    : YEAR_ONE_OUTLINE;

  const selectedStages = stages.length > 0 ? stages : YEAR_ONE_OUTLINE;

  return selectedStages
    .map((stage) =>
      [
        `${stage.quarter}: ${stage.theme}`,
        listBlock("Outcomes", stage.outcomes),
        listBlock("Execution", stage.execution),
        listBlock("MCP usage", stage.mcpUsage),
        listBlock("Proof", stage.proof),
      ].join("\n"),
    )
    .join("\n\n");
}

export function scoreInitiative(input: InitiativeScoreInput): InitiativeScore {
  const weighted =
    input.userImpact * 0.3 +
    input.strategicFit * 0.25 +
    input.revenuePotential * 0.2 +
    input.urgency * 0.15 +
    (6 - input.effort) * 0.05 +
    (6 - input.risk) * 0.05;
  const score = Math.round((weighted / 5) * 100);

  const recommendation: InitiativeScore["recommendation"] =
    score >= 75 ? "commit" : score >= 50 ? "sequence" : "defer";

  const upsideContribution = Math.round(
    ((input.userImpact * 0.3 + input.strategicFit * 0.25 + input.revenuePotential * 0.2) / 3.75) *
      100,
  );
  const feasibilityCredit = Math.round(
    (((6 - input.effort) * 0.05 + (6 - input.risk) * 0.05) / 0.5) * 100,
  );

  const rationale = [
    `Impact/fit/revenue contributed ${String(upsideContribution)}% of the available upside.`,
    `Effort and risk adjusted the score by ${String(feasibilityCredit)}% of the available feasibility credit.`,
    recommendation === "commit"
      ? "This is ready to make an official roadmap commitment."
      : recommendation === "sequence"
        ? "This is worth pursuing after dependencies or scope are narrowed."
        : "This should wait until its impact, fit, or feasibility improves.",
  ];

  return {
    name: input.name,
    score,
    recommendation,
    rationale,
  };
}

export function createLaunchBrief(input: LaunchBriefInput): string {
  return [
    `Objective: ${input.objective}`,
    `Audience: ${input.audience}`,
    `Timeframe: ${input.timeframe}`,
    listBlock("Constraints", input.constraints),
    listBlock("Success metrics", input.successMetrics),
    listBlock("Execution path", [
      "Confirm the highest-risk assumptions before widening scope.",
      "Map each launch task to an owner, proof artifact, and rollback condition.",
      "Use MCP-backed documentation, issue, and telemetry sources for evidence at every review gate.",
    ]),
  ].join("\n");
}

export function listBlock(title: string, items: string[]): string {
  return `${title}:\n${items.map((item) => `- ${item}`).join("\n")}`;
}
