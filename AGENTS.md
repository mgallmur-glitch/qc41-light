# AGENTS.md — QC 4.1 Light

Guide for AI coding agents (Cursor, Claude Code, Codex, Hermes, etc.) using this repository.

## What this project is

**QC 4.1 Light** is an open, evidence-first diagnostic for **one sales-call transcript**. It outputs a bounded JSON report (`qc41-light-0.2`) with transcript quotes, one breakpoint, three mistakes, three corrections, and one speakable recovery line.

This repo is **product only**: skill, schema, validator, CLI, MCP, eval harness, and examples. It does not include hosted marketing sites, checkout flows, or proprietary QC methodology.

Read `docs/IP_BOUNDARY.md` before adding docs, examples, or generated output.

## Quick orientation

| Path | Purpose |
|------|---------|
| `SKILL.md` | Skill entrypoint for any harness |
| `prompts/analyze-call.md` | Canonical analysis prompt |
| `schemas/qc41-light-report.schema.json` | JSON contract |
| `scripts/validate_report.py` | Schema + business-rule validator |
| `scripts/render_report.py` | JSON → Markdown |
| `bin/qc41-light.js` | CLI entry |
| `src/mcp-server.js` | MCP stdio server |
| `eval/` | 50 synthetic calls + public scorer |
| `examples/` | Shareable synthetic reports |
| `AGENT.md` / `SOUL.md` | Analyst persona (optional for harnesses) |

## How to run (no API key)

```bash
git clone https://github.com/mgallmur-glitch/qc41-light.git
cd qc41-light
./scripts/demo.sh
python3 scripts/validate_report.py examples/synthetic-report.json
python3 scripts/render_report.py examples/synthetic-report.json
```

## How to analyze a real transcript

### Option A — Skill / harness (recommended offline)

1. Load `SKILL.md` and `prompts/analyze-call.md`.
2. Paste the full transcript (never invent one).
3. Ask the model to return **only** JSON matching the schema.
4. Validate: `python3 scripts/validate_report.py report.json`
5. Optionally render: `python3 scripts/render_report.py report.json`

Language: English transcript → `language: "en"`. Spanish → neutral Latin American Spanish (`"es"`), **tú** form, never voseo.

### Option B — CLI (BYOK, local)

```bash
npm install
# Set ANTHROPIC_API_KEY or OPENAI_API_KEY in your shell (never commit keys).
qc41-light analyze --file call.txt --key env --out qc41-light-report.json
```

### Option C — MCP (BYOK, local)

```bash
qc41-light mcp
```

Tools: `analyze_sales_call`, `get_qc41_light_prompt`, `get_schema`. Keys live in the **MCP server environment**, never in client chat or browser UI.

## Eval / open challenge

```bash
python3 eval/generate_corpus.py
python3 eval/run_baseline.py
python3 eval/score_report.py REPORT.json eval/corpus/000.gold_spec.json eval/corpus/000.call.txt
```

Baselines: reference fixtures ~**100** · naive unstructured ~**32**. See `eval/README.md`. Use **synthetic** transcripts only in PRs.

## Rules agents must follow

1. **Evidence before interpretation** — every finding needs a transcript quote or explicit silence.
2. **No proprietary QC doctrine** — no internal taxonomies, scoring formulas, profile names, or depth levels (see `docs/IP_BOUNDARY.md`).
3. **Validate before claiming success** — run `validate_report.py` on any JSON you produce or modify.
4. **No secrets in git** — no API keys, customer transcripts, internal paths, or commercial funnel copy.
5. **Privacy** — redact PII in examples; see `docs/PRIVACY.md`.
6. **Do not expand scope** — this package is single-call Light only; team/longitudinal products are out of repo.

## CI gate (run before proposing changes)

```bash
python3 -m unittest discover -s tests -v
python3 scripts/audit_ip_boundary.py
python3 scripts/validate_report.py examples/synthetic-report.json
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Invented quotes | Quote must appear as substring in transcript |
| Wrong mistake enums | Use schema allowlist only |
| Ten breakpoints | Exactly **one** `breakpoint` |
| Proprietary labels | Use generic stage/objection language |
| Skipping validation | CI blocks invalid JSON |

## Adapters

- Claude Code: `adapters/claude-code/MARKETPLACE.md`
- Codex: `adapters/codex/AGENTS.md`
- Hermes: `adapters/hermes/README.md`
- Generic: `adapters/generic/README.md`

## License

Apache-2.0. Copyright Mauricio Gallmur. See `LICENSE` and `NOTICE`.
