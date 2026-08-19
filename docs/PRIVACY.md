# Privacy and Data Handling

QC 4.1 Light sends one anonymous HTTPS ping when a report is rendered: language + skill version only (example payload: `{"lang":"es","v":"0.3.5"}`). No transcript, no user identifiers, no IP storage on our side. Opt out by setting `QC41_LIGHT_DISABLE_PING=1`. Beyond that ping it contains no uploader and no other telemetry or hosted API client. It reads only what the user provides to their chosen AI harness.

## Before analysis

- Obtain authorization to analyze the call.
- Remove names, email addresses, phone numbers, company secrets and payment details.
- Prefer synthetic transcripts for demos and tests.
- Check the data policy of the model/provider running the analysis.
- Prefer local models when confidentiality requires it.

## Do not include

- API keys;
- CRM IDs;
- customer records;
- payment credentials;
- medical or legal records;
- unrelated personal information;
- real transcripts in public issues or pull requests.

## Output limitations

The report analyzes language in one transcript. It does not establish personality, mental health, financial capacity, legal compliance, truthfulness or future performance.

## Deletion

The package does not retain data itself. Users must delete transcript and report files according to their own retention policy and the behavior of the AI harness they selected.
