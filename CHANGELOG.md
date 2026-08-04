# Changelog

All notable changes to this project are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.3.2] — 2026-08-04

### Fixed

- Hermes Agent URL installation now includes the canonical prompt, report schema, validator, renderer, privacy requirements, and IP boundary through a standard `references/` runtime bundle.
- Added regression tests that simulate the URL-installed file tree and execute validation plus Markdown rendering from that minimal installation.
- Aligned the `SKILL.md` package version with release `0.3.2`; the JSON schema remains `qc41-light-0.2` by design.
- Unknown call outcomes now require an explicit `not_observed` sentinel; arbitrary transcript fragments can no longer masquerade as outcome evidence.

### Verified

- Real English call E2E: 996 anonymized transcript segments, 33/33 exact evidence quotes, 0 residual PII regex matches, canonical validator PASS, deterministic renderer PASS.

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
