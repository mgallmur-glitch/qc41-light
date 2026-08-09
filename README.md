# QC 4.1 Light

[![CI](https://github.com/mgallmur-glitch/qc41-light/actions/workflows/ci.yml/badge.svg)](https://github.com/mgallmur-glitch/qc41-light/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-%3E%3D18-green.svg)](https://nodejs.org/)
[![EN · ES](https://img.shields.io/badge/language-EN%20%7C%20ES-informational.svg)](README.es.md)

[Español](README.es.md) · **AI agents:** [`AGENTS.md`](AGENTS.md)

**The call felt fine. The transcript tells another story.**

QC 4.1 Light is an open, evidence-first sales-call diagnostic: one transcript in, one structured report out — with quotes, a breakpoint, corrections, and a speakable recovery line.

## Quick start

```bash
git clone https://github.com/mgallmur-glitch/qc41-light.git
cd qc41-light
npm install   # optional — for CLI/MCP only
qc41-light demo
```

The offline demo validates and renders a synthetic report — no API key, no network.

Shareable samples: [`examples/synthetic-report.md`](examples/synthetic-report.md) · ES [`examples/synthetic-report.es.md`](examples/synthetic-report.es.md)

## Install from GitHub Packages


> Package visibility on GitHub Packages defaults to private for user accounts. Make it **Public** at: https://github.com/users/mgallmur-glitch/packages/npm/package/qc41-light → Package settings → Change visibility.

```bash
npm install @mgallmur-glitch/qc41-light
# or globally:
npm install -g @mgallmur-glitch/qc41-light
```

Requires a GitHub PAT with `read:packages` (and login to `npm.pkg.github.com`), or install from the release tarball / clone.

## Install surfaces

| Surface | Command |
|---------|---------|
| Offline demo | `qc41-light demo` |
| Analyze file (BYOK) | `qc41-light analyze --file call.txt --key env` |
| MCP server | `qc41-light mcp` |
| Skill / harness | `SKILL.md` + `prompts/analyze-call.md` |
| Claude Code | [`adapters/claude-code/MARKETPLACE.md`](adapters/claude-code/MARKETPLACE.md) |

MCP tools: `analyze_sales_call`, `get_qc41_light_prompt`, `get_schema`.

## Skill / harness path

### Hermes Agent — one-command install

```bash
hermes skills install --yes https://raw.githubusercontent.com/mgallmur-glitch/qc41-light/v0.3.5/SKILL.md
```

Then invoke it in a new Hermes session:

```text
/qc41-light Analyze this authorized, redacted sales-call transcript and return validated JSON.
```

The URL installation includes the canonical prompt, report schema, validator, renderer, privacy rules, and IP boundary. Package version: `0.3.5`. Report schema version: `qc41-light-0.2`.

For any other assistant, provide `SKILL.md` + `prompts/analyze-call.md`, then validate:

```bash
python3 scripts/validate_report.py report.json
python3 scripts/render_report.py report.json > report.md
```

Adapters: Claude Code · Codex · Hermes · generic — under `adapters/`.

## Eval harness

```bash
python3 eval/generate_corpus.py   # 50 synthetic EN/ES calls
python3 eval/run_baseline.py      # reference vs naive baseline
```

Run the baseline locally and consult [`eval/README.md`](eval/README.md) for the current reference and naive-score definitions.

## What one call returns

| Output | Why it matters |
|--------|----------------|
| Transcript quality audit | Know when confidence should drop |
| Stage map + two strengths | Preserve what already works |
| One breakpoint | Not a laundry list |
| Objections with quotes only | Evidence or silence |
| Three mistakes + three speakable corrections | Ready for the next call |
| Recovery line + replay plan + checklist | Actionable next step |

## Boundary

Useful and bounded. Proprietary QC methodology, taxonomies, scoring formulas and team systems stay out of this package — see `docs/IP_BOUNDARY.md`.

## Privacy

No telemetry in this package. CLI/MCP analysis is local BYOK (env keys). Redact real calls before sending transcripts to any model — `docs/PRIVACY.md`.

## Status

Current package and skill release: [`v0.3.5`](https://github.com/mgallmur-glitch/qc41-light/releases/tag/v0.3.5). The report schema contract remains `qc41-light-0.2` for compatibility. These versions are intentionally separate: package changes do not alter the JSON shape unless the schema version also changes. CLI · MCP · eval are on `main`.

## License

Apache-2.0. See `LICENSE`.
