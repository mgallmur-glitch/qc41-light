#!/usr/bin/env python3
"""Run official baseline scores and write the eval leaderboard.

Scores:
  * qc41-light-reference — published fixtures (synthetic EN + blind ES/EN)
  * naive-unstructured — intentionally weak report (evidence fails)

Also writes ``eval/leaderboard.json``.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = Path(__file__).resolve().parent
sys.path.insert(0, str(EVAL))

from score_report import score_report  # noqa: E402


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _entry(name: str, description: str, results: list[dict], notes: str = "") -> dict:
    scores = [r["result"]["score"] for r in results]
    avg = round(sum(scores) / len(scores), 2) if scores else 0.0
    return {
        "name": name,
        "description": description,
        "average_score": avg,
        "scores": [
            {
                "fixture": r["fixture"],
                "score": r["result"]["score"],
                "breakdown": {k: v["points"] for k, v in r["result"]["breakdown"].items()},
            }
            for r in results
        ],
        "notes": notes,
    }


def main() -> int:
    if not (EVAL / "corpus" / "000.gold_spec.json").exists():
        subprocess.check_call([sys.executable, str(EVAL / "generate_corpus.py")])

    fixtures = [
        {
            "fixture": "examples/synthetic-report.json",
            "report": ROOT / "examples" / "synthetic-report.json",
            "gold": EVAL / "gold" / "synthetic-en.gold_spec.json",
            "transcript": ROOT / "examples" / "synthetic-call.txt",
        },
        {
            "fixture": "tests/blind-spanish-report.json",
            "report": ROOT / "tests" / "blind-spanish-report.json",
            "gold": EVAL / "gold" / "blind-es.gold_spec.json",
            "transcript": ROOT / "tests" / "blind-spanish-call.txt",
        },
        {
            "fixture": "tests/blind-english-report.json",
            "report": ROOT / "tests" / "blind-english-report.json",
            "gold": EVAL / "gold" / "blind-en.gold_spec.json",
            "transcript": ROOT / "tests" / "blind-english-call.txt",
        },
    ]

    ref_results = []
    for fx in fixtures:
        result = score_report(
            _load(fx["report"]),
            _load(fx["gold"]),
            fx["transcript"].read_text(encoding="utf-8"),
        )
        ref_results.append({"fixture": fx["fixture"], "result": result})
        print(f"reference {fx['fixture']}: {result['score']}")

    naive_result = score_report(
        _load(EVAL / "fixtures" / "naive-unstructured-report.json"),
        _load(EVAL / "gold" / "synthetic-en.gold_spec.json"),
        (ROOT / "examples" / "synthetic-call.txt").read_text(encoding="utf-8"),
    )
    print(f"naive-unstructured: {naive_result['score']}")

    corpus_result = score_report(
        _load(ROOT / "examples" / "synthetic-report.json"),
        _load(EVAL / "corpus" / "000.gold_spec.json"),
        (EVAL / "corpus" / "000.call.txt").read_text(encoding="utf-8"),
    )
    print(f"corpus/000 vs synthetic-report: {corpus_result['score']}")

    leaderboard = {
        "version": "qc41-light-eval-0.1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "corpus_size": 50,
        "scoring": {
            "weights": {
                "schema_validity": 20,
                "evidence_in_transcript": 25,
                "breakpoint_stage": 15,
                "outcome_status": 10,
                "mistake_category_overlap": 15,
                "structure_completeness": 15,
            },
            "notes": (
                "Evidence quotes must appear as substrings of the transcript. "
                "No proprietary QC taxonomies or formulas are used."
            ),
        },
        "entries": [
            _entry(
                "qc41-light-reference",
                "Official fixtures: synthetic EN + blind ES/EN reports",
                ref_results,
                notes="Hand-authored gold_specs; expect ~90+ average.",
            ),
            _entry(
                "naive-unstructured",
                "Intentionally weak report with invented evidence quotes",
                [
                    {
                        "fixture": "eval/fixtures/naive-unstructured-report.json",
                        "result": naive_result,
                    }
                ],
                notes="Shows the gap when evidence grounding and categories fail.",
            ),
        ],
        "corpus_anchor": {
            "fixture": "examples/synthetic-report.json vs corpus/000",
            "score": corpus_result["score"],
        },
    }

    out = EVAL / "leaderboard.json"
    out.write_text(json.dumps(leaderboard, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
