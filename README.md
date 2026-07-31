# QC 4.1 Light

[Versión en español](README.es.md)

A portable, evidence-first sales-call diagnostic for AI coding agents and agent harnesses.

Paste a transcript. Get a useful diagnosis grounded in exact excerpts from the call:

- the most likely breakpoint;
- explicit and implicit objections;
- three observable mistakes;
- three concrete corrections;
- one recovery line;
- confidence and limitations.

## Bilingual contract

English and Spanish are first-class markets:

- English transcript → English diagnosis.
- Spanish transcript → neutral Latin American Spanish diagnosis.
- Evidence quotes stay in their original language.
- Stable JSON field names remain in English so Hermes, Claude Code, Codex and generic harnesses can consume the same schema.

## What it is

QC 4.1 Light is a free, bounded diagnostic layer inspired by Mauricio Gallmur's experience closing high-ticket sales and building Closing Code AI.

It is useful on its own and intentionally robust: it audits transcript quality, maps the call stages, preserves strengths, locates the breakpoint, diagnoses objections, corrects mistakes and produces a replay plan. It is **not** the full QC 4.1 methodology, a team performance system, or a substitute for professional review.

## What stays private

The open package does not include proprietary buyer taxonomies, internal scoring formulas, diagnostic depth models, close-system selection, team comparison, coaching history, or the complete QC 4.1 prompt corpus.

See `docs/IP_BOUNDARY.md`.

## Quick start

### Any AI assistant

1. Give the assistant `SKILL.md` and `prompts/analyze-call.md`.
2. Paste or attach a transcript.
3. Ask: `Analyze this call with QC 4.1 Light.`
4. Save the JSON output.
5. Validate it:

```bash
python3 scripts/validate_report.py report.json
```

6. Render a readable report:

```bash
python3 scripts/render_report.py report.json > report.md
```

### Claude Code

Copy `adapters/claude-code/CLAUDE.md` into your project instructions or reference it from your existing `CLAUDE.md`.

### Codex

Copy `adapters/codex/AGENTS.md` into the project or merge its QC section into your existing `AGENTS.md`.

### Hermes Agent

Install the directory under your profile skills and use the included `SKILL.md`. Keep the package private until you have reviewed the transcript's data-handling requirements.

## Privacy

- Use synthetic or authorized transcripts.
- Remove names, emails, phone numbers and payment details before sharing with a hosted model.
- Prefer local processing when confidentiality matters.
- This package does not upload data by itself. Your chosen model or harness may do so.

See `docs/PRIVACY.md`.

## Input quality

Best results include speaker labels:

```text
[00:00] CLOSER: Thanks for joining. What made you take this call?
[00:08] PROSPECT: We have leads, but follow-up is inconsistent.
```

The tool still works without timestamps, but confidence should decrease.

## Output contract

The canonical JSON schema is `schemas/qc41-light-report.schema.json`.

Every important finding must include transcript evidence. If evidence is missing, the output must say so rather than inventing intent, emotion or buyer psychology.

## Full-depth analysis

For longitudinal analysis, team comparison, complete QC 4.1 diagnostics and professional forensic review, use Closing Code AI or request a forensic call audit from Mauricio Gallmur.

- https://closingcodeai.online

## Status

Release candidate `0.2.0`. The repository is private during review. Not yet published, not connected to a public API, and not guaranteed stable until the first tagged release.

## License

Apache-2.0. See `LICENSE`.
