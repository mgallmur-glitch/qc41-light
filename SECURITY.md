# Security Policy

## Supported versions

QC 4.1 Light `v0.3.5` is supported on the latest `main` branch. Security fixes
target `main`.

## Data handling

QC 4.1 Light contains **no uploader, telemetry, or hosted API client**. It
reads only the files the user provides to their chosen AI harness. See
`docs/PRIVACY.md` for the full data-handling policy.

## What this package is not

- It is not a hosted service.
- It does not make network requests on its own.
- It does not store, transmit or persist transcript or report data beyond the
  local filesystem.

## Reporting a vulnerability

If you discover a security issue:

1. **Do not** open a public GitHub issue.
2. Email the maintainer directly with a description and, if possible, a
   reproduction steps or proof of concept.
3. Allow a reasonable window for acknowledgment and a fix before any public
   disclosure.

## IP-boundary protection

The repository includes an automated IP-boundary audit
(`scripts/audit_ip_boundary.py`) that scans for prohibited proprietary
terminology, credentials and private infrastructure paths. This audit runs in
CI on every push and pull request. See `docs/IP_BOUNDARY.md` and
`CONTRIBUTING.md` for details.
