# QC 4.1 Light — Codex Adapter

## Sales-call transcript tasks

For any request to analyze a sales-call transcript:

- Follow `/SKILL.md` and `/prompts/analyze-call.md`.
- Produce `/schemas/qc41-light-report.schema.json` compatible JSON.
- Save the result and execute `/scripts/validate_report.py` against it.
- Repair validation failures before reporting success.
- Use exact transcript evidence and explicit limits.
- Do not reveal, reconstruct or infer proprietary QC 4.1 doctrine.
- Do not send transcripts to external systems or publish outputs.

A complete task ends only after a real validation pass.
