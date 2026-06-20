import { describe, expect, it } from "vitest";

import {
  createDecisionBrief,
  createExecutionChecklist,
  createYearPlan,
  getCapabilities,
} from "../src/winston.js";

describe("Winston AI planning tools", () => {
  it("creates a quarterly one-year outline by default", () => {
    const plan = createYearPlan({
      objective: "launch Winston AI as an official MCP server",
    });

    expect(plan.serverName).toBe("Winston AI");
    expect(plan.phases).toHaveLength(4);
    expect(plan.phases.map((phase) => phase.label)).toEqual([
      "Quarter 1",
      "Quarter 2",
      "Quarter 3",
      "Quarter 4",
    ]);
  });

  it("creates a monthly one-year outline when requested", () => {
    const plan = createYearPlan({
      objective: "expand Winston AI adoption",
      horizon: "monthly",
      focusAreas: ["developer experience", "security"],
    });

    expect(plan.phases).toHaveLength(12);
    expect(plan.phases[0]?.deliverables[0]).toContain("developer experience");
    expect(plan.phases[1]?.deliverables[0]).toContain("security");
  });

  it("requires at least two options for decision briefs", () => {
    expect(() => createDecisionBrief({
      decision: "pick a launch channel",
      options: ["developer docs"],
    })).toThrow("At least two options are required");
  });

  it("adds launch-readiness review items for high-risk execution", () => {
    const checklist = createExecutionChecklist({
      initiative: "Winston AI launch",
      phase: "Launch",
      deliverables: ["MCP server package"],
      riskLevel: "high",
    });

    expect(checklist.checklist).toContain(
      "Run a pre-launch review covering security, reliability, and operational readiness.",
    );
  });

  it("lists public Winston AI tools", () => {
    const capabilities = getCapabilities();

    expect(capabilities.serverName).toBe("Winston AI");
    expect(capabilities.tools).toContain("winston_plan_year");
  });
});
