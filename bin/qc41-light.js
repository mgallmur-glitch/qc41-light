#!/usr/bin/env node
import { runCli } from '../src/cli.js';

runCli(process.argv.slice(2)).catch((err) => {
  const msg = err?.message || String(err);
  console.error(`qc41-light: ${msg}`);
  process.exit(err?.exitCode || 1);
});
