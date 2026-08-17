---
name: qc41-light
description: "Use when analyzing, auditing, reviewing or diagnosing a sales call transcript — find where the deal was lost, closer mistakes, objections missed, and a recovery line. Returns an evidence-backed QC 4.1 Light report with exact quotes, breakpoint minute, corrections, and a speakable recovery script. Works for high-ticket closers, sales managers auditing rep calls, and owners reviewing their sales team's calls."
version: 0.3.5
---

# QC 4.1 Light (Claude Code skill)

When the user provides a sales-call transcript and wants analysis, feedback, diagnosis, mistakes, objections, or a recovery line:

1. Read the package root `SKILL.md` (repo root when developing; otherwise the installed plugin package).
2. Read `prompts/analyze-call.md`.
3. Read the complete transcript. Never invent one.
4. Return **only** JSON matching `schemas/qc41-light-report.schema.json`.
5. Save as `qc41-light-report.json` unless the user chooses another path.
6. Run `python3 scripts/validate_report.py qc41-light-report.json` when available.
7. Render Markdown with `python3 scripts/render_report.py` only when asked.

## Language

- English transcript → English diagnosis (`language`: `en`).
- Spanish transcript → neutral Latin American Spanish (`tú`), never voseo (`language`: `es` / `es-419`).
- Preserve evidence quotes in the original language.

## Boundary

Do not invent proprietary QC terminology, scoring formulas, depth levels, or personality profiles. Stay within the public schema and generic sales language.

## MCP alternative

`qc41-light mcp` exposes `analyze_sales_call`, `get_qc41_light_prompt`, and `get_schema` (BYOK via `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`).
