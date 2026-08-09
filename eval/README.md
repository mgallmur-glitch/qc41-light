# QC 4.1 Light — Eval & Leaderboard

Evidence-first harness: **your agent vs QC 4.1 Light** on **50 synthetic sales calls** (≈50/50 English / Spanish).

No proprietary QC taxonomies, scores, or formulas. Scoring uses only public schema fields and transcript substring checks (Python stdlib).

## Quick start

```bash
# From repo root
python3 eval/generate_corpus.py      # writes eval/corpus/ if missing (50 items)
python3 eval/run_baseline.py         # scores fixtures → eval/leaderboard.json
```

Score any candidate report:

```bash
python3 eval/score_report.py REPORT.json GOLD_SPEC.json TRANSCRIPT.txt
python3 eval/score_report.py REPORT.json GOLD_SPEC.json TRANSCRIPT.txt --json
```

Validate schema separately (same contract as CI):

```bash
python3 scripts/validate_report.py REPORT.json
```

## What is measured (0–100)

| Dimension | Points | Rule |
| --- | ---: | --- |
| Schema validity | 20 | Passes `scripts/validate_report.py` |
| Evidence in transcript | 25 | Every evidence `quote` must appear as a substring of the call text |
| Breakpoint stage | 15 | Exact match to `expected_breakpoint_stage` (partial credit for `accepted_breakpoint_stages`) |
| Outcome status | 10 | Exact match to `expected_outcome` (partial credit for `accepted_outcomes`) |
| Mistake category overlap | 15 | Fraction of `expected_mistake_categories` present on the candidate |
| Structure completeness | 15 | Has `recovery_line` + exactly 3 mistakes + 3 corrections (mild concept penalty) |

## Corpus layout

```text
eval/corpus/
  NNN.meta.json       # id, language, failure_mode, expectations
  NNN.call.txt        # synthetic transcript (speakers + timestamps)
  NNN.gold_spec.json  # machine-checkable scoring expectations
```

- **50** items (`000`–`049`).
- Item `000` mirrors `examples/synthetic-call.txt`.
- Failure modes include premature pitch, shallow discovery, objection not clarified, vague next step, pressure, unsupported claim, weak agenda, missed implementation risk, price before value, overtalking, missed follow-up, weak transition, poor fit not addressed.
- Mistake categories on gold specs use the **public** schema enum.

```bash
python3 eval/generate_corpus.py --force   # regenerate / overwrite
```

## How to submit a score

1. Run your agent on `eval/corpus/NNN.call.txt` with `SKILL.md` + `prompts/analyze-call.md`.
2. Validate: `python3 scripts/validate_report.py report.json`.
3. Score:

```bash
python3 eval/score_report.py report.json eval/corpus/NNN.gold_spec.json eval/corpus/NNN.call.txt --json
```

4. Report agent/model name, mean score across the corpus (or a declared subset), and a link to synthetic scored JSON. Open a PR — synthetic only, never real customer calls.

## Official baselines

`python3 eval/run_baseline.py` writes `eval/leaderboard.json` with:

| Entry | Meaning |
| --- | --- |
| `qc41-light-reference` | Published fixtures vs hand-authored gold specs — expect **~90+** |
| `naive-unstructured` | Fake weak report with invented quotes — intentionally low |

Hand-authored gold specs: `eval/gold/`.

## Privacy & IP

- All eval transcripts are **synthetic**.
- Stay inside `docs/IP_BOUNDARY.md`.
- Run `python3 scripts/audit_ip_boundary.py` before publishing eval additions.
