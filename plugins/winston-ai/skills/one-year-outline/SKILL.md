---
name: one-year-outline
description: Create a focused 1-year execution outline with quarterly milestones, deliverables, risks, and success metrics.
---

# One-Year Outline

## Instructions

Use this skill when a user asks for a 1-year plan, annual roadmap, strategic outline, launch plan, transformation plan, or long-range execution sequence.

1. Identify the planning subject:
   - Product, company, team, project, campaign, capability, or personal operating system.
2. Gather or infer the core context:
   - Goal
   - Target audience or stakeholders
   - Current state
   - Constraints
   - Available resources
   - Definition of success
3. If critical context is missing, proceed with clear assumptions unless the plan would be misleading.
4. Divide the year into four quarters:
   - Q1: foundation and validation
   - Q2: workflow depth and repeatability
   - Q3: integration and scaling
   - Q4: readiness, hardening, or expansion
5. For each quarter, include:
   - Outcomes
   - Key deliverables
   - Dependencies
   - Risks
   - Decision gates
   - Success metrics
6. End with immediate next actions and open questions.

When the plan depends on specific technology, business systems, or platform behavior, consult the relevant installed plugin, MCP tool, docs, or local repository context. Avoid using unrelated tools simply because they are installed.

## Examples

### Product launch

User:

```text
Create a 1-year outline for launching a B2B AI analytics product.
```

Response shape:

```text
Objective
Assumptions
Success metrics
Q1: validate the problem and prototype
Q2: private beta and usage instrumentation
Q3: public launch and integrations
Q4: scale, reliability, and expansion
Risks and mitigations
Decision gates
Next actions
```

### Team operating plan

User:

```text
Plan the next year for a platform engineering team.
```

Response should include operational reliability, developer experience, platform adoption, cost controls, and cross-team governance.

## Performance Notes

- Keep the first answer practical. A useful outline beats a comprehensive but unfocused plan.
- Use bullets and tables for scanability.
- Avoid calendar-date commitments unless the user provides specific dates.
- Prefer technical sequencing, dependencies, and validation gates over broad time estimates.
- Make tradeoffs visible when scope exceeds likely capacity.

## Troubleshooting

- If the user asks for "everything," narrow the output to the highest-leverage workstreams.
- If the user asks for a plan in a regulated or high-risk domain, include compliance, review, and approval gates.
- If the user requests an official or public launch plan, include documentation, support, security, validation, and release-readiness steps.
- If the user asks to use all installed plugins, interpret that as using relevant installed capabilities throughout the work, not invoking every plugin regardless of fit.
