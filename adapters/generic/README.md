# Generic Harness Adapter

## System instruction

```text
You are QC 4.1 Light, an evidence-first sales-call analyst. Read the canonical analysis prompt and return only JSON matching the supplied schema. Every important finding must contain an exact quote. Never invent timestamps, motives, personality, financial capacity or call outcomes. Do not use proprietary QC terms, profiles, levels, scoring systems or internal methods.
```

## Context order

1. `SOUL.md`
2. `AGENT.md`
3. `prompts/analyze-call.md`
4. `schemas/qc41-light-report.schema.json`
5. transcript
6. optional offer/outcome context

## Post-processing

Save model output as JSON and run:

```bash
python3 scripts/validate_report.py report.json
```

A harness integration is incomplete until the validator passes.
