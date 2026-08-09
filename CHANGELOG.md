# Changelog

All notable changes to this project are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.3.5] — 2026-08-09

### Changed

- Republished on the fresh `mgallmur-glitch/qc41-light` repository after contributor-metadata reset; package contents unchanged from v0.3.4.
- All skill, marketplace, plugin, and documentation surfaces aligned to `0.3.5`.

## [0.3.4] — 2026-08-09

### Changed

- Package name is now `@mgallmur-glitch/qc41-light` and publishes to **GitHub Packages** (`npm.pkg.github.com`) using the repository `GITHUB_TOKEN` (no separate npmjs token required for launch).
- Optional npmjs.org publish remains gated behind `ENABLE_NPMJS_PUBLISH` + `NPM_TOKEN`.

## [0.3.3] — 2026-08-09

### Fixed

- Aligned package, skill, Claude marketplace/plugin manifests, MCP server version, CONTRIBUTING, and SECURITY to `0.3.3`.
- MCP server now reads its version from `package.json` to prevent future drift.
- Excluded `__pycache__` and local pack artifacts from the npm tarball via `.npmignore`.

### Changed

- GitHub repository topics and homepage set for launch discoverability.
- Branch protection enabled on `main` (PR + CI required).

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
