import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cli = path.join(ROOT, 'bin', 'qc41-light.js');

function run(args) {
  return spawnSync(process.execPath, [cli, ...args], {
    cwd: ROOT,
    encoding: 'utf8',
    timeout: 30_000,
  });
}

const help = run(['--help']);
assert.equal(help.status, 0, help.stderr);
assert.match(help.stdout, /QC 4\.1 Light/);
assert.match(help.stdout, /demo/);
assert.match(help.stdout, /analyze/);
assert.match(help.stdout, /mcp/);

const demo = run(['demo']);
assert.equal(demo.status, 0, demo.stderr);
assert.match(demo.stdout + demo.stderr, /PASS: valid QC 4\.1 Light report/);

const unknown = run(['not-a-command']);
assert.equal(unknown.status, 1);
assert.match(unknown.stderr, /Unknown command/);

const pkg = JSON.parse(fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8'));
assert.match(pkg.version, /^\d+\.\d+\.\d+$/);
assert.equal(pkg.scripts.test, 'node tests/node-smoke.mjs');
const skill = fs.readFileSync(path.join(ROOT, 'SKILL.md'), 'utf8');
assert.ok(new RegExp(`^version: ${pkg.version}$`, 'm').test(skill));


console.log('PASS: Node CLI smoke tests');
