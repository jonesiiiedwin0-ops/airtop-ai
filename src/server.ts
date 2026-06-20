import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';

import {
  formatRoadmapMarkdown,
  getRoadmapPhase,
  launchReadinessChecks,
  SERVER_NAME,
  SERVER_SLUG,
  SERVER_VERSION,
  summarizeQuarter,
  yearOneRoadmap
} from './roadmap.js';

const detailSchema = z.enum(['month', 'quarter', 'year']);
const audienceSchema = z.enum(['engineering', 'leadership', 'operations']);

function asJsonText(value: unknown): string {
  return JSON.stringify(value, null, 2);
}

function contentWithJson(value: unknown) {
  return {
    content: [
      {
        type: 'text' as const,
        text: asJsonText(value)
      }
    ],
    structuredContent: value
  };
}

export function createWinstonAiServer(): McpServer {
  const server = new McpServer(
    {
      name: SERVER_SLUG,
      title: SERVER_NAME,
      version: SERVER_VERSION
    },
    {
      capabilities: {
        logging: {}
      },
      instructions:
        'Use Winston AI to plan official server milestones, inspect year-one readiness, and produce launch execution briefs.'
    }
  );

  server.registerResource(
    'winston-ai-status',
    'winston://status',
    {
      title: 'Winston AI status',
      description: 'Official server identity, version, and current operating posture.',
      mimeType: 'application/json'
    },
    (uri) => ({
      contents: [
        {
          uri: uri.href,
          mimeType: 'application/json',
          text: asJsonText({
            name: SERVER_NAME,
            slug: SERVER_SLUG,
            version: SERVER_VERSION,
            transport: 'stdio',
            posture: 'official foundation ready',
            capabilities: ['roadmap planning', 'launch readiness', 'milestone execution briefs']
          })
        }
      ]
    })
  );

  server.registerResource(
    'winston-ai-year-one-outline',
    'winston://roadmap/year-one',
    {
      title: 'Winston AI year-one outline',
      description: 'The complete 12-month outline for creating and operating the official Winston AI server.',
      mimeType: 'text/markdown'
    },
    (uri) => ({
      contents: [
        {
          uri: uri.href,
          mimeType: 'text/markdown',
          text: formatRoadmapMarkdown()
        }
      ]
    })
  );

  server.registerTool(
    'get-year-one-outline',
    {
      title: 'Get year-one outline',
      description: 'Return Winston AI official server roadmap details by month, quarter, or full year.',
      inputSchema: {
        detail: detailSchema.default('year').describe('Level of roadmap detail to return.'),
        quarter: z.number().int().min(1).max(4).optional().describe('Quarter to return when detail is quarter.'),
        month: z.number().int().min(1).max(12).optional().describe('Month to return when detail is month.')
      }
    },
    async ({ detail, quarter, month }) => {
      if (detail === 'month') {
        const selected = getRoadmapPhase(month ?? 1);
        return contentWithJson({ detail, roadmap: [selected] });
      }

      if (detail === 'quarter') {
        const selectedQuarter = quarter ?? 1;
        return contentWithJson({
          detail,
          quarter: selectedQuarter,
          roadmap: summarizeQuarter(selectedQuarter)
        });
      }

      return contentWithJson({ detail, roadmap: yearOneRoadmap });
    }
  );

  server.registerTool(
    'plan-milestone',
    {
      title: 'Plan milestone',
      description: 'Convert a Winston AI roadmap month into an execution-ready milestone brief.',
      inputSchema: {
        month: z.number().int().min(1).max(12).describe('Roadmap month to plan.'),
        owner: z.string().min(1).default('Winston AI maintainers').describe('Responsible owner for the milestone.')
      }
    },
    async ({ month, owner }) => {
      const phase = getRoadmapPhase(month);
      const milestone = {
        name: `${SERVER_NAME} month ${phase.month}: ${phase.name}`,
        owner,
        objective: phase.objective,
        workItems: phase.deliverables.map((deliverable, index) => ({
          id: `M${phase.month}-${index + 1}`,
          title: deliverable,
          acceptanceCriteria: phase.successSignals
        })),
        exitCriteria: phase.successSignals
      };

      return contentWithJson(milestone);
    }
  );

  server.registerTool(
    'assess-launch-readiness',
    {
      title: 'Assess launch readiness',
      description: 'Review readiness areas for the Winston AI official server launch path.',
      inputSchema: {
        includeDeferred: z
          .boolean()
          .default(false)
          .describe('Include planned areas that are intentionally deferred beyond the foundation release.')
      }
    },
    async ({ includeDeferred }) => {
      const checks = includeDeferred
        ? launchReadinessChecks
        : launchReadinessChecks.filter((check) => check.status === 'ready');
      const blockers = launchReadinessChecks.filter((check) => check.status !== 'ready');

      return contentWithJson({
        server: SERVER_NAME,
        foundationReady: blockers.length === 0 || !includeDeferred,
        checks,
        deferred: blockers
      });
    }
  );

  server.registerPrompt(
    'year-one-execution-brief',
    {
      title: 'Year-one execution brief',
      description: 'Create an audience-specific execution brief for the Winston AI official server.',
      argsSchema: {
        audience: audienceSchema.default('engineering'),
        quarter: z.number().int().min(1).max(4).optional()
      }
    },
    ({ audience, quarter }) => {
      const scope = quarter ? `quarter ${quarter}` : 'the full year';
      const roadmap = quarter ? summarizeQuarter(quarter) : yearOneRoadmap;

      return {
        messages: [
          {
            role: 'user' as const,
            content: {
              type: 'text' as const,
              text: [
                `Create a concise ${audience} execution brief for ${SERVER_NAME} covering ${scope}.`,
                'Use these roadmap entries as source material:',
                asJsonText(roadmap),
                'Call out objectives, deliverables, risks, and evidence required to prove completion.'
              ].join('\n\n')
            }
          }
        ]
      };
    }
  );

  return server;
}
