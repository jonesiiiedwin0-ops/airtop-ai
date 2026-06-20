export type RoadmapPhase = {
  month: number;
  name: string;
  objective: string;
  deliverables: string[];
  successSignals: string[];
};

export const SERVER_NAME = 'Winston AI';
export const SERVER_SLUG = 'winston-ai';
export const SERVER_VERSION = '0.1.0';

export const yearOneRoadmap: RoadmapPhase[] = [
  {
    month: 1,
    name: 'Official foundation',
    objective: 'Ship the first signed, documented MCP server surface for Winston AI.',
    deliverables: [
      'Create the Winston AI MCP package, build pipeline, and local stdio transport.',
      'Publish official server identity, README, license, and client configuration.',
      'Expose roadmap, readiness, and milestone planning capabilities.'
    ],
    successSignals: [
      'Server builds from a clean checkout.',
      'An MCP client can list tools, read resources, and fetch prompts end-to-end.'
    ]
  },
  {
    month: 2,
    name: 'Security and governance baseline',
    objective: 'Define the controls required before external beta use.',
    deliverables: [
      'Document data handling boundaries and approval requirements for tools.',
      'Add security review checklists for every new capability.',
      'Establish release notes, versioning, and dependency update policy.'
    ],
    successSignals: [
      'Every tool has an owner, approval class, and input validation.',
      'Dependency scans remain clean before each release.'
    ]
  },
  {
    month: 3,
    name: 'Private alpha',
    objective: 'Validate Winston AI with a small set of trusted technical users.',
    deliverables: [
      'Add alpha feedback capture and issue triage workflow.',
      'Create sample prompts for engineering, operations, and leadership use cases.',
      'Measure tool invocation quality and confusing failure modes.'
    ],
    successSignals: [
      'Alpha users can complete the three primary workflows without maintainer help.',
      'Top usability defects are tracked with reproduction steps.'
    ]
  },
  {
    month: 4,
    name: 'Hosted transport design',
    objective: 'Prepare Winston AI for remote MCP clients without weakening local stdio support.',
    deliverables: [
      'Design a stateless Streamable HTTP transport option.',
      'Document DNS rebinding, CORS, auth, and deployment constraints.',
      'Choose observability events for tool, resource, and prompt usage.'
    ],
    successSignals: [
      'Remote deployment architecture is documented and reviewable.',
      'Local stdio behavior remains stable.'
    ]
  },
  {
    month: 5,
    name: 'Beta capability expansion',
    objective: 'Broaden the server from planning to operational execution support.',
    deliverables: [
      'Add integration templates for project tracking, deployment, and incident workflows.',
      'Introduce structured output schemas for beta tools.',
      'Create examples that show safe tool chaining.'
    ],
    successSignals: [
      'Beta workflows return machine-readable output for downstream clients.',
      'Examples run without credentials by default.'
    ]
  },
  {
    month: 6,
    name: 'Public beta readiness',
    objective: 'Make the server supportable for users outside the founding team.',
    deliverables: [
      'Publish troubleshooting docs and compatibility notes.',
      'Add CI coverage for build, tests, and package integrity.',
      'Define support escalation and severity labels.'
    ],
    successSignals: [
      'Fresh users can install, configure, and verify the server from README instructions.',
      'CI blocks regressions in core MCP capabilities.'
    ]
  },
  {
    month: 7,
    name: 'Official launch candidate',
    objective: 'Freeze the public launch surface and harden release operations.',
    deliverables: [
      'Cut a launch candidate with stable tool names and resource URIs.',
      'Run compatibility checks against target MCP clients.',
      'Complete launch readiness assessment.'
    ],
    successSignals: [
      'No launch-blocking readiness items remain open.',
      'Client compatibility evidence is attached to the release.'
    ]
  },
  {
    month: 8,
    name: 'Official launch',
    objective: 'Release Winston AI as an official server with public documentation.',
    deliverables: [
      'Publish the official package and release notes.',
      'Create installation guides for supported clients.',
      'Open public feedback channels and maintenance policy.'
    ],
    successSignals: [
      'Users can install Winston AI using the documented package entrypoint.',
      'Launch issues are triaged within the published support policy.'
    ]
  },
  {
    month: 9,
    name: 'Ecosystem integrations',
    objective: 'Connect Winston AI to the services users already rely on.',
    deliverables: [
      'Prioritize first-party integration adapters from beta feedback.',
      'Add credential-safe configuration examples.',
      'Document integration testing expectations.'
    ],
    successSignals: [
      'Top-requested integrations have implementation plans and owners.',
      'Credential handling never leaks secrets into MCP content responses.'
    ]
  },
  {
    month: 10,
    name: 'Reliability and scale',
    objective: 'Improve resilience for larger teams and hosted deployments.',
    deliverables: [
      'Define performance budgets for startup, tool latency, and payload size.',
      'Add smoke tests for hosted transport when implemented.',
      'Document backup and rollback practices for releases.'
    ],
    successSignals: [
      'Performance regressions are measurable before release.',
      'Rollback steps are tested during release drills.'
    ]
  },
  {
    month: 11,
    name: 'Governed extensibility',
    objective: 'Allow new Winston AI capabilities without destabilizing the official server.',
    deliverables: [
      'Define contribution guidelines for tools, prompts, and resources.',
      'Create review criteria for new integration modules.',
      'Add examples for extension authors.'
    ],
    successSignals: [
      'New capabilities follow consistent naming and schema rules.',
      'Reviewers can reject unsafe extensions with documented criteria.'
    ]
  },
  {
    month: 12,
    name: 'Year-two strategy',
    objective: 'Convert launch learnings into a measurable next-year operating plan.',
    deliverables: [
      'Summarize adoption, reliability, support, and feature metrics.',
      'Identify the next set of official server capabilities.',
      'Publish the year-two roadmap proposal.'
    ],
    successSignals: [
      'Year-one outcomes are tied to evidence, not anecdotes.',
      'Year-two priorities have clear acceptance criteria.'
    ]
  }
];

export const launchReadinessChecks = [
  {
    area: 'MCP protocol surface',
    status: 'ready',
    evidence: 'Stdio transport, tools, resources, and prompts are implemented in this package.'
  },
  {
    area: 'Documentation',
    status: 'ready',
    evidence: 'README and year-one outline describe install, run, and operating intent.'
  },
  {
    area: 'Automated verification',
    status: 'ready',
    evidence: 'Node test client launches the built server and exercises MCP methods.'
  },
  {
    area: 'Hosted deployment',
    status: 'planned',
    evidence: 'Streamable HTTP deployment remains a roadmap item until auth and observability are finalized.'
  },
  {
    area: 'External service credentials',
    status: 'planned',
    evidence: 'No credentialed integrations are enabled in the initial official server.'
  }
] as const;

export function getRoadmapPhase(month: number): RoadmapPhase {
  const phase = yearOneRoadmap.find((entry) => entry.month === month);

  if (!phase) {
    throw new RangeError(`Month must be between 1 and ${yearOneRoadmap.length}.`);
  }

  return phase;
}

export function formatRoadmapMarkdown(phases: RoadmapPhase[] = yearOneRoadmap): string {
  const body = phases
    .map((phase) => {
      const deliverables = phase.deliverables.map((item) => `- ${item}`).join('\n');
      const signals = phase.successSignals.map((item) => `- ${item}`).join('\n');

      return [
        `## Month ${phase.month}: ${phase.name}`,
        '',
        `Objective: ${phase.objective}`,
        '',
        'Deliverables:',
        deliverables,
        '',
        'Success signals:',
        signals
      ].join('\n');
    })
    .join('\n\n');

  return [`# ${SERVER_NAME} year-one official server outline`, '', body].join('\n');
}

export function summarizeQuarter(quarter: number): RoadmapPhase[] {
  if (!Number.isInteger(quarter) || quarter < 1 || quarter > 4) {
    throw new RangeError('Quarter must be between 1 and 4.');
  }

  const firstMonth = (quarter - 1) * 3 + 1;
  return yearOneRoadmap.slice(firstMonth - 1, firstMonth + 2);
}
