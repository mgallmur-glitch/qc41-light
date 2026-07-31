# Hermes Adapter

Copy the complete `qc41-light` directory into the target Hermes profile's skills directory, preserving linked folders:

```text
~/.hermes/skills/qc41-light/
```

Then ask:

```text
Analyze this sales-call transcript with qc41-light and return a validated JSON report.
```

Hermes should load `SKILL.md`, execute the procedure, save the JSON in the active workspace, and run `scripts/validate_report.py`.

Do not install into another Hermes profile without explicit authorization. Do not connect the open skill to production Closing Code AI endpoints until an authenticated public API contract exists.
