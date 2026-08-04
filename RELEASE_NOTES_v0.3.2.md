# QC 4.1 Light v0.3.2

## Production readiness release

This patch closes the Hermes Agent installation gap discovered during real-call end-to-end acceptance.

### Fixed

- `hermes skills install <raw SKILL.md URL>` now installs the complete runtime bundle through standard linked `references/` and `scripts/` paths.
- `SKILL.md`, npm package, package lock, README status, and Git tag align at `0.3.2`.
- The report contract remains `qc41-light-0.2`; package and schema versions are intentionally separate.
- Hermes adapter documents the exact one-command installation and `/qc41-light` invocation.

### Added gates

- URL-install-shape regression test.
- Runtime/canonical file parity checks.
- Node CLI smoke tests via `npm test`.
- CI Node 24 job with `npm ci`, `npm audit --audit-level=moderate`, and `npm test`.
- Dependency lock updated to 0 known npm vulnerabilities.

### Real-data acceptance

- Full English call: 996 sanitized segments; canonical validation PASS; deterministic render PASS; 33/33 evidence quotes exact; 0 residual PII regex matches.
- Low-quality no-close case: 34 sanitized segments; expected behavior is bounded confidence, explicit limitations, and no invented outcome.

No customer transcript, private endpoint, credential, proprietary taxonomy, or internal methodology is included in this release.
