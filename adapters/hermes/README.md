# Hermes Agent Adapter

## Install

Install the tagged skill with one command:

```bash
hermes skills install --yes https://raw.githubusercontent.com/mgallmur-glitch/qc41-light/v0.3.4/SKILL.md
```

The installer must report these runtime files:

```text
SKILL.md
references/analyze-call.md
references/qc41-light-report.schema.json
references/IP_BOUNDARY.md
references/PRIVACY.md
scripts/validate_report.py
scripts/render_report.py
```

Start a new Hermes session and invoke:

```text
/qc41-light Analyze this authorized, redacted sales-call transcript and return validated JSON.
```

Hermes loads `SKILL.md`, reads the complete transcript, writes canonical JSON in the active workspace, validates it with `scripts/validate_report.py`, and optionally renders Markdown with `scripts/render_report.py`.

Package/skill version is `0.3.4`. The report schema remains `qc41-light-0.2` for compatibility.

Do not install into another Hermes profile without explicit authorization. Do not send unredacted customer transcripts to hosted models. This open skill does not connect to private Closing Code AI endpoints.
