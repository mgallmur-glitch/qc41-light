# QC 4.1 Light v0.2.0

QC 4.1 Light is a portable, evidence-first diagnostic for one sales-call transcript. It produces a bounded English or neutral Latin American Spanish report while preserving exact transcript evidence.

## Included

- transcript-quality audit and call-outcome evidence;
- evidence-backed call-stage map;
- two strengths worth preserving;
- one most likely breakpoint;
- explicit and implicit objections only when supported by excerpts;
- exactly three observable mistakes and three linked corrections;
- one recovery line, four-line replay plan and five-point checklist;
- stable JSON schema, stdlib validator and Markdown renderer;
- adapters for Hermes Agent, Claude Code, Codex and generic harnesses;
- blind English and Spanish fixtures with 44 exact evidence excerpts, plus a separate 15-excerpt synthetic example;
- discoverable `unittest` suite;
- CI across Python 3.10, 3.11 and 3.12;
- deterministic credential, infrastructure and IP-boundary audit.

## Verification

```bash
python3 -m unittest discover -s tests -v
python3 scripts/audit_ip_boundary.py
python3 scripts/validate_report.py examples/synthetic-report.json
```

Release verification:

- 42 discoverable tests passed locally;
- 44/44 blind-fixture excerpts matched their source transcripts exactly;
- clean installation test passed from an isolated temporary directory;
- no runtime third-party dependencies;
- no uploader, telemetry or hosted API client;
- adversarial IP-boundary scan passed.

## Boundaries

This release analyzes a single transcript. It does not include the complete QC 4.1 methodology, proprietary taxonomies or verdict logic, team comparison, coaching history, private prompt corpora, customer data or internal infrastructure.

## Privacy

Use only synthetic or authorized transcripts. Remove names, email addresses, phone numbers, payment details and other personal data before using a hosted model. The package does not upload data by itself; the selected AI harness controls model and data handling.

## License

Apache License 2.0 for the files included in this repository.
