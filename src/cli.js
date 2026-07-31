import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { resolveFromRoot, ROOT } from './paths.js';
import { analyzeTranscript, offlineSkillHint } from './analyze.js';
import { startMcpStdio } from './mcp-server.js';

const HELP = `QC 4.1 Light — evidence-first sales-call diagnosis

Usage:
  qc41-light <command> [options]

Commands:
  demo                 Run offline demo (validate + render synthetic report)
  analyze              Analyze a transcript file (BYOK via env or --key)
  mcp                  Start MCP stdio server
  help                 Show this help

analyze options:
  --file <path>        Transcript file (required)
  --provider <name>    anthropic | openai (auto-detect if omitted)
  --key env|<key>      API key; prefer env (ANTHROPIC_API_KEY / OPENAI_API_KEY)
  --out <path>         Output JSON path (default: qc41-light-report.json)
  --language <code>    en | es
  --context <text>     Optional offer/outcome context

Examples:
  qc41-light demo
  qc41-light analyze --file call.txt --provider anthropic --key env
  qc41-light mcp

Offline skill (no key): give SKILL.md + prompts/analyze-call.md to any harness.
See AGENTS.md for agent integration.
`;

function parseArgs(argv) {
  const args = { _: [], flags: {} };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--help' || a === '-h') {
      args.flags.help = true;
    } else if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith('--')) {
        args.flags[key] = next;
        i++;
      } else {
        args.flags[key] = true;
      }
    } else {
      args._.push(a);
    }
  }
  return args;
}

function runDemoScript() {
  return new Promise((resolve, reject) => {
    const script = resolveFromRoot('scripts', 'demo.sh');
    const child = spawn('bash', [script], {
      cwd: ROOT,
      stdio: 'inherit',
    });
    child.on('error', reject);
    child.on('close', (code) => {
      if (code === 0) resolve();
      else reject(Object.assign(new Error(`demo.sh exited ${code}`), { exitCode: code || 1 }));
    });
  });
}

async function cmdDemo() {
  await runDemoScript();
}

async function cmdAnalyze(flags) {
  const file = flags.file;
  if (!file) {
    console.error('Missing --file <path>');
    console.error(offlineSkillHint());
    process.exitCode = 2;
    return;
  }
  const abs = path.isAbsolute(file) ? file : path.resolve(process.cwd(), file);
  if (!fs.existsSync(abs)) {
    throw Object.assign(new Error(`file not found: ${abs}`), { exitCode: 1 });
  }
  const transcript = fs.readFileSync(abs, 'utf8');
  try {
    const report = await analyzeTranscript(transcript, {
      provider: flags.provider,
      key: flags.key || 'env',
      language: flags.language || '',
      context: flags.context || '',
    });
    const out = flags.out
      ? path.isAbsolute(flags.out)
        ? flags.out
        : path.resolve(process.cwd(), flags.out)
      : path.resolve(process.cwd(), 'qc41-light-report.json');
    fs.writeFileSync(out, JSON.stringify(report, null, 2) + '\n', 'utf8');
    console.log(`Wrote ${out}`);
    console.log(`Breakpoint: ${report.breakpoint.stage}`);
    console.log(`Recovery:   ${report.recovery_line.text}`);
  } catch (err) {
    if (err.code === 'NO_API_KEY') {
      console.error(err.message);
      process.exitCode = 2;
      return;
    }
    throw err;
  }
}

export async function runCli(argv) {
  const { _, flags } = parseArgs(argv);
  const cmd = _[0];

  if (!cmd || cmd === 'help' || flags.help) {
    process.stdout.write(HELP);
    return;
  }

  switch (cmd) {
    case 'demo':
      return cmdDemo();
    case 'analyze':
      return cmdAnalyze(flags);
    case 'mcp':
      return startMcpStdio();
    default:
      console.error(`Unknown command: ${cmd}\n`);
      process.stdout.write(HELP);
      process.exitCode = 1;
  }
}
