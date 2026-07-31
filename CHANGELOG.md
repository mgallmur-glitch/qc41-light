# Changelog

All notable changes to this project are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.3.0] — 2026-07-31

### Added

- npm CLI: `demo`, `analyze` (BYOK), `mcp`
- MCP tools: `analyze_sales_call`, `get_qc41_light_prompt`, `get_schema`
- Eval corpus (50 synthetic EN/ES calls), scorer, and leaderboard baselines
- Bilingual fixtures and anonymized demo call fragments
- Root `AGENTS.md` for AI coding agents

### Changed

- README focused on skill, CLI, MCP, and eval surfaces
- Schema `$id` points to this GitHub repository

## [0.2.0] — 2026-07-29

### Added

- Evidence-first single-call diagnostic contract (`qc41-light-0.2`)
- Transcript quality audit, stage map, breakpoint, objections, recovery line
- JSON schema, stdlib validator, Markdown renderer
- Adapters for Hermes, Claude Code, Codex, and generic harnesses
- IP-boundary auditor and CI matrix (Python 3.10–3.12)
- Blind English/Spanish fixtures and synthetic examples

## [0.1.0] — 2026-07-29

- Initial bounded transcript diagnostic prototype
