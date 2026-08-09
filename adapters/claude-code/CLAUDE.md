# QC 4.1 Light — Claude Code Adapter

When the user asks to analyze a sales-call transcript:

1. Read the repository root `SKILL.md`.
2. Read `prompts/analyze-call.md`.
3. Read the complete transcript.
4. Return JSON matching `schemas/qc41-light-report.schema.json`.
5. Save it as `qc41-light-report.json` unless the user chooses another path.
6. Run `python3 scripts/validate_report.py qc41-light-report.json`.
7. If validation fails, repair the report and validate again.
8. Render Markdown only when requested.

Never expose or recreate private QC 4.1 terminology, scoring, taxonomies, prompts or system mappings. Never upload a transcript without the user's authorization.

## Marketplace / plugin install

See [`MARKETPLACE.md`](./MARKETPLACE.md) for `/plugin marketplace add`, skill path, and MCP stdio setup (`qc41-light mcp`).
