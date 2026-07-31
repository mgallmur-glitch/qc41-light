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

Give any assistant `SKILL.md` + `prompts/analyze-call.md`, then validate:

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

Baselines: reference fixtures **100** · naive unstructured **~32**. Details: [`eval/README.md`](eval/README.md).

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

Report contract: `qc41-light-0.2` JSON. CLI · MCP · eval on `main`. Tagged release `0.2.0` remains the stable skill baseline.

## License

Apache-2.0. See `LICENSE`.
