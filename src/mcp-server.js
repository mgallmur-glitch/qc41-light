#!/usr/bin/env node
/**
 * QC 4.1 Light — MCP stdio server
 *
 * Tools:
 *   analyze_sales_call  — BYOK analysis (ANTHROPIC_API_KEY or OPENAI_API_KEY)
 *   get_qc41_light_prompt — returns analysis prompt
 *   get_schema — returns schema JSON
 */
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { analyzeTranscript, offlineSkillHint } from './analyze.js';
import { readPrompt, readSchema } from './prompt.js';

export function createMcpServer() {
  const server = new McpServer({
    name: 'qc41-light',
    version: '0.2.0',
  });

  server.tool(
    'analyze_sales_call',
    'Analyze a sales-call transcript with QC 4.1 Light. Returns a validated JSON report string. Requires ANTHROPIC_API_KEY or OPENAI_API_KEY in the environment (BYOK).',
    {
      transcript: z.string().min(20).describe('Full sales-call transcript text'),
      language: z
        .string()
        .optional()
        .describe('Optional output language hint: en or es (neutral Latin American Spanish)'),
      context: z
        .string()
        .optional()
        .describe('Optional offer / outcome / next-step context (untrusted)'),
      provider: z
        .enum(['anthropic', 'openai'])
        .optional()
        .describe('Force provider; otherwise auto-detect from env keys'),
    },
    async ({ transcript, language, context, provider }) => {
      try {
        const report = await analyzeTranscript(transcript, {
          language: language || '',
          context: context || '',
          provider,
          key: 'env',
        });
        return {
          content: [{ type: 'text', text: JSON.stringify(report, null, 2) }],
        };
      } catch (err) {
        const msg =
          err?.code === 'NO_API_KEY'
            ? [
                'BYOK required for live analysis.',
                'Set ANTHROPIC_API_KEY or OPENAI_API_KEY in the MCP server environment.',
                '',
                offlineSkillHint(),
              ].join('\n')
            : err?.message || String(err);
        return {
          content: [{ type: 'text', text: msg }],
          isError: true,
        };
      }
    },
  );

  server.tool(
    'get_qc41_light_prompt',
    'Return the canonical QC 4.1 Light analysis prompt (prompts/analyze-call.md).',
    {},
    async () => ({
      content: [{ type: 'text', text: readPrompt() }],
    }),
  );

  server.tool(
    'get_schema',
    'Return the QC 4.1 Light report JSON schema.',
    {},
    async () => ({
      content: [{ type: 'text', text: JSON.stringify(readSchema(), null, 2) }],
    }),
  );

  return server;
}

export async function startMcpStdio() {
  const server = createMcpServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

// Allow `node src/mcp-server.js` directly
const isDirect =
  process.argv[1] &&
  (process.argv[1].endsWith('mcp-server.js') || process.argv[1].includes('mcp-server'));

if (isDirect) {
  startMcpStdio().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}
