# Contributing to QC 4.1 Light

Thank you for your interest in improving QC 4.1 Light. This repository is
currently in **release-candidate** status and is reviewed privately before any
public visibility decision.

## Running the tests

The test suite uses only the Python standard library — no virtual environment
or extra dependencies are required.

```bash
python3 -m unittest discover -s tests -v
```

The CI workflow (`.github/workflows/ci.yml`) runs the same suite on Python
3.10, 3.11 and 3.12, plus fixture validation and the IP-boundary audit.

## IP-boundary rules (read before contributing)

QC 4.1 Light is intentionally bounded. Contributions must **not** introduce:

- proprietary buyer taxonomies, profile names or diagnostic levels;
- internal scoring formulas, weights or verdict logic;
- internal prompt corpus or few-shot examples from the full methodology;
- system-selection mappings or team benchmarking data;
- real customer data, real transcripts or personally identifiable information;
- API keys, credentials, internal server paths or endpoint URLs.

Every pull request is automatically checked by
`scripts/audit_ip_boundary.py`. If the audit fails, the CI will block the
merge. You can run it locally:

```bash
python3 scripts/audit_ip_boundary.py
```

See `docs/IP_BOUNDARY.md` for the full boundary definition.

## How to contribute

1. Fork or branch from `main`.
2. Write or update tests under `tests/` using `unittest.TestCase` so they are
   discoverable by `python3 -m unittest discover`.
3. Ensure all fixtures remain **synthetic** — never use real call data.
4. Run the full suite and the audit locally before pushing.
5. Keep pull requests focused: one feature or fix per PR.

## Coding conventions

- Scripts and tests run on Python 3.10+ with **zero third-party dependencies**.
- All JSON output must conform to `schemas/qc41-light-report.schema.json`.
- Bilingual output: English transcripts produce English reports; Spanish
  transcripts produce neutral Latin American Spanish reports.

## Reporting issues

Use GitHub Issues for bugs, feature requests and documentation improvements.
Do **not** include real transcripts, customer names, credentials or any
proprietary information in issues or pull requests.
