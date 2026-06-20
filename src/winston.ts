export type PlanningHorizon = "quarterly" | "monthly";
export type RiskLevel = "low" | "medium" | "high";

export interface YearPlanInput {
  objective: string;
  audience?: string;
  constraints?: string[];
  focusAreas?: string[];
  horizon?: PlanningHorizon;
}

export interface PlanPhase {
  label: string;
  theme: string;
  goals: string[];
  deliverables: string[];
  validation: string[];
  risks: string[];
}

export interface YearPlan extends Record<string, unknown> {
  serverName: "Winston AI";
  objective: string;
  audience: string;
  operatingPrinciples: string[];
  phases: PlanPhase[];
  executionCadence: string[];
}

export interface DecisionBriefInput {
  decision: string;
  options: string[];
  successCriteria?: string[];
  constraints?: string[];
}

export interface DecisionBrief extends Record<string, unknown> {
  decision: string;
  recommendedOption: string;
  rationale: string[];
  tradeoffs: string[];
  nextSteps: string[];
}

export interface ExecutionChecklistInput {
  initiative: string;
  phase: string;
  deliverables: string[];
  riskLevel?: RiskLevel;
}

export interface ExecutionChecklist extends Record<string, unknown> {
  initiative: string;
  phase: string;
  riskLevel: RiskLevel;
  checklist: string[];
}

const DEFAULT_FOCUS_AREAS = [
  "product definition",
  "technical foundation",
  "go-to-market readiness",
  "operational resilience",
] as const;

const DEFAULT_CONSTRAINTS = [
  "Keep scope measurable.",
  "Prefer reversible implementation choices until user demand is proven.",
  "Validate every launch milestone with evidence.",
] as const;

export function createYearPlan(input: YearPlanInput): YearPlan {
  const objective = requireNonEmpty(input.objective, "objective");
  const audience = input.audience?.trim() || "operators, builders, and decision makers";
  const focusAreas = normalizeList(input.focusAreas, DEFAULT_FOCUS_AREAS);
  const constraints = normalizeList(input.constraints, DEFAULT_CONSTRAINTS);
  const horizon = input.horizon ?? "quarterly";

  return {
    serverName: "Winston AI",
    objective,
    audience,
    operatingPrinciples: [
      "Start with explicit outcomes before tools or implementation details.",
      "Convert strategy into testable execution slices.",
      "Keep risks visible with named owners and validation checkpoints.",
      ...constraints,
    ],
    phases: horizon === "monthly"
      ? buildMonthlyPhases(objective, focusAreas)
      : buildQuarterlyPhases(objective, focusAreas),
    executionCadence: [
      "Review priorities weekly against evidence, blockers, and new constraints.",
      "Publish a monthly decision log with assumptions, reversals, and shipped outcomes.",
      "Run a quarterly readiness review before expanding scope.",
    ],
  };
}

export function createDecisionBrief(input: DecisionBriefInput): DecisionBrief {
  const decision = requireNonEmpty(input.decision, "decision");
  const options = normalizeList(input.options, []);

  if (options.length < 2) {
    throw new Error("At least two options are required for a decision brief.");
  }

  const successCriteria = normalizeList(input.successCriteria, [
    "clear user value",
    "low operational risk",
    "fast validation path",
  ]);
  const constraints = normalizeList(input.constraints, ["limited complexity", "maintainable delivery"]);
  const recommendedOption = options[0] ?? "";

  return {
    decision,
    recommendedOption,
    rationale: successCriteria.map((criterion) => `${recommendedOption} best supports ${criterion}.`),
    tradeoffs: constraints.map((constraint) => `Track ${constraint} explicitly before committing deeper investment.`),
    nextSteps: [
      `Write acceptance criteria for ${recommendedOption}.`,
      "Identify the smallest reversible implementation slice.",
      "Define evidence that would change the recommendation.",
    ],
  };
}

export function createExecutionChecklist(input: ExecutionChecklistInput): ExecutionChecklist {
  const initiative = requireNonEmpty(input.initiative, "initiative");
  const phase = requireNonEmpty(input.phase, "phase");
  const deliverables = normalizeList(input.deliverables, []);

  if (deliverables.length === 0) {
    throw new Error("At least one deliverable is required for an execution checklist.");
  }

  const riskLevel = input.riskLevel ?? "medium";
  const checklist = deliverables.flatMap((deliverable) => [
    `Define owner and acceptance criteria for ${deliverable}.`,
    `Validate ${deliverable} with the target user or stakeholder.`,
  ]);

  if (riskLevel !== "low") {
    checklist.push("Document rollback triggers, monitoring signals, and escalation owner.");
  }

  if (riskLevel === "high") {
    checklist.push("Run a pre-launch review covering security, reliability, and operational readiness.");
  }

  return {
    initiative,
    phase,
    riskLevel,
    checklist,
  };
}

export function getCapabilities(): Record<string, unknown> {
  return {
    serverName: "Winston AI",
    description: "A planning and execution MCP server for turning strategic goals into validated operating plans.",
    tools: [
      "winston_plan_year",
      "winston_decision_brief",
      "winston_execution_checklist",
      "winston_capabilities",
    ],
    strengths: [
      "one-year outlines",
      "decision briefs",
      "execution checklists",
      "risk-aware operating cadence",
    ],
  };
}

function buildQuarterlyPhases(objective: string, focusAreas: string[]): PlanPhase[] {
  const labels = ["Quarter 1", "Quarter 2", "Quarter 3", "Quarter 4"] as const;
  const themes = ["Foundation", "Prototype", "Launch", "Scale"] as const;

  return labels.map((label, index) => {
    const focus = focusAreas[index % focusAreas.length] ?? "execution";
    const theme = themes[index] ?? "Execution";
    return buildPhase(label, theme, objective, focus);
  });
}

function buildMonthlyPhases(objective: string, focusAreas: string[]): PlanPhase[] {
  return Array.from({ length: 12 }, (_, index) => {
    const monthNumber = index + 1;
    const focus = focusAreas[index % focusAreas.length] ?? "execution";
    const theme = monthNumber <= 3
      ? "Foundation"
      : monthNumber <= 6
        ? "Prototype"
        : monthNumber <= 9
          ? "Launch"
          : "Scale";

    return buildPhase(`Month ${monthNumber}`, theme, objective, focus);
  });
}

function buildPhase(label: string, theme: string, objective: string, focus: string): PlanPhase {
  return {
    label,
    theme,
    goals: [
      `Advance ${objective} through ${focus}.`,
      "Reduce the largest unresolved execution risk.",
    ],
    deliverables: [
      `${theme} brief for ${focus}`,
      `${theme} validation evidence`,
      `${theme} decision log update`,
    ],
    validation: [
      "Define measurable acceptance criteria before implementation.",
      "Review evidence with the intended audience before expanding scope.",
    ],
    risks: [
      `Scope creep around ${focus}`,
      "Unvalidated assumptions treated as commitments",
    ],
  };
}

function normalizeList(values: readonly string[] | undefined, fallback: readonly string[]): string[] {
  const normalized = values
    ?.map((value) => value.trim())
    .filter((value) => value.length > 0);

  return normalized && normalized.length > 0 ? normalized : [...fallback];
}

function requireNonEmpty(value: string, fieldName: string): string {
  const normalized = value.trim();

  if (normalized.length === 0) {
    throw new Error(`${fieldName} is required.`);
  }

  return normalized;
}
