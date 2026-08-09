#!/usr/bin/env python3
"""Score a candidate QC 4.1 Light report against a gold_spec + transcript.

Uses only the Python standard library. Schema checks reuse
``scripts/validate_report.py`` when available, with an embedded fallback.

Scoring dimensions (0–100 total):
  schema_validity          20
  evidence_in_transcript   25
  breakpoint_stage         15
  outcome_status           10
  mistake_category_overlap 15
  structure_completeness   15  (recovery_line + 3 mistakes + 3 corrections)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

try:
    from validate_report import validate as validate_schema  # type: ignore
except Exception:  # pragma: no cover - import path edge cases
    validate_schema = None  # type: ignore


WEIGHTS = {
    "schema_validity": 20.0,
    "evidence_in_transcript": 25.0,
    "breakpoint_stage": 15.0,
    "outcome_status": 10.0,
    "mistake_category_overlap": 15.0,
    "structure_completeness": 15.0,
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _collect_evidence_quotes(report: dict) -> list[str]:
    quotes: list[str] = []

    def add(ev: Any) -> None:
        if isinstance(ev, dict) and isinstance(ev.get("quote"), str):
            q = ev["quote"].strip()
            if q:
                quotes.append(q)
        elif isinstance(ev, list):
            for item in ev:
                add(item)

    outcome = report.get("call_outcome")
    if isinstance(outcome, dict):
        add(outcome.get("evidence"))

    bp = report.get("breakpoint")
    if isinstance(bp, dict):
        add(bp.get("evidence"))

    for key in ("stage_analysis", "strengths", "objections", "mistakes"):
        items = report.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict):
                add(item.get("evidence"))

    return quotes


def _quote_in_transcript(quote: str, transcript: str) -> bool:
    """Substring match; ignore trivial whitespace differences."""
    if not quote:
        return False
    if quote in transcript:
        return True
    # Soft normalize: collapse whitespace for matching only
    norm_q = " ".join(quote.split())
    norm_t = " ".join(transcript.split())
    return norm_q in norm_t


def _schema_score(report: dict) -> tuple[float, str]:
    if validate_schema is None:
        # Minimal embedded checks if import failed
        required = {
            "version",
            "language",
            "call_outcome",
            "breakpoint",
            "mistakes",
            "corrections",
            "recovery_line",
        }
        missing = sorted(required - set(report))
        if missing:
            return 0.0, f"missing fields: {missing}"
        if report.get("version") != "qc41-light-0.2":
            return 0.0, "bad version"
        return 1.0, "embedded minimal pass"
    try:
        validate_schema(report)
        return 1.0, "valid"
    except Exception as exc:  # noqa: BLE001 — surface validator message
        return 0.0, str(exc)


def _evidence_score(report: dict, transcript: str) -> tuple[float, dict]:
    quotes = _collect_evidence_quotes(report)
    if not quotes:
        return 0.0, {"total": 0, "matched": 0, "misses": []}
    matched = 0
    misses: list[str] = []
    for q in quotes:
        if _quote_in_transcript(q, transcript):
            matched += 1
        else:
            misses.append(q[:120])
    ratio = matched / len(quotes)
    return ratio, {"total": len(quotes), "matched": matched, "misses": misses[:8]}


def _breakpoint_score(report: dict, gold: dict) -> tuple[float, str]:
    expected = gold.get("expected_breakpoint_stage")
    if not expected:
        return 1.0, "no expectation"
    bp = report.get("breakpoint")
    if not isinstance(bp, dict):
        return 0.0, "missing breakpoint"
    actual = bp.get("stage")
    if actual == expected:
        return 1.0, f"exact match ({actual})"
    accepted = gold.get("accepted_breakpoint_stages") or []
    if actual in accepted:
        return 0.5, f"partial ({actual} in accepted)"
    return 0.0, f"mismatch actual={actual} expected={expected}"


def _outcome_score(report: dict, gold: dict) -> tuple[float, str]:
    expected = gold.get("expected_outcome")
    if not expected:
        return 1.0, "no expectation"
    outcome = report.get("call_outcome")
    if not isinstance(outcome, dict):
        return 0.0, "missing call_outcome"
    actual = outcome.get("status")
    if actual == expected:
        return 1.0, f"exact match ({actual})"
    accepted = gold.get("accepted_outcomes") or []
    if actual in accepted:
        return 0.5, f"partial ({actual} in accepted)"
    return 0.0, f"mismatch actual={actual} expected={expected}"


def _mistake_overlap_score(report: dict, gold: dict) -> tuple[float, str]:
    expected = gold.get("expected_mistake_categories") or []
    if not expected:
        return 1.0, "no expectation"
    expected_set = {str(x) for x in expected}
    mistakes = report.get("mistakes")
    if not isinstance(mistakes, list):
        return 0.0, "missing mistakes"
    actual = {m.get("category") for m in mistakes if isinstance(m, dict)}
    overlap = expected_set & actual
    # Jaccard against expected (candidate can have extras without penalty beyond missing)
    ratio = len(overlap) / len(expected_set)
    return ratio, f"overlap {sorted(overlap)} / expected {sorted(expected_set)}"


def _structure_score(report: dict) -> tuple[float, str]:
    parts = 0
    notes: list[str] = []

    recovery = report.get("recovery_line")
    if isinstance(recovery, dict) and isinstance(recovery.get("text"), str) and len(recovery["text"].strip()) >= 10:
        parts += 1
    else:
        notes.append("missing recovery_line")

    mistakes = report.get("mistakes")
    if isinstance(mistakes, list) and len(mistakes) == 3:
        parts += 1
    else:
        notes.append(f"mistakes count={len(mistakes) if isinstance(mistakes, list) else 'n/a'}")

    corrections = report.get("corrections")
    if isinstance(corrections, list) and len(corrections) == 3:
        parts += 1
    else:
        notes.append(f"corrections count={len(corrections) if isinstance(corrections, list) else 'n/a'}")

    return parts / 3.0, "; ".join(notes) if notes else "ok"


def _recovery_concept_bonus(report: dict, gold: dict) -> tuple[float, str]:
    """Optional soft check: recovery text should touch gold concepts (informational)."""
    concepts = gold.get("gold_recovery_must_include_concepts") or []
    if not concepts:
        return 1.0, "n/a"
    recovery = report.get("recovery_line")
    text = ""
    if isinstance(recovery, dict):
        text = f"{recovery.get('text', '')} {recovery.get('why', '')}".lower()
    hit = [c for c in concepts if str(c).lower() in text]
    ratio = len(hit) / len(concepts)
    return ratio, f"concepts hit {hit} / {concepts}"


def score_report(report: dict, gold: dict, transcript: str) -> dict:
    schema_r, schema_note = _schema_score(report)
    evidence_r, evidence_detail = _evidence_score(report, transcript)
    bp_r, bp_note = _breakpoint_score(report, gold)
    out_r, out_note = _outcome_score(report, gold)
    mist_r, mist_note = _mistake_overlap_score(report, gold)
    struct_r, struct_note = _structure_score(report)
    concept_r, concept_note = _recovery_concept_bonus(report, gold)

    # Fold recovery-concept as a soft modifier on structure (up to -3 pts if zero)
    structure_effective = struct_r
    if gold.get("gold_recovery_must_include_concepts"):
        # Keep structure weight; apply mild penalty when concepts miss
        structure_effective = max(0.0, struct_r - (1.0 - concept_r) * 0.2)

    breakdown = {
        "schema_validity": {
            "ratio": round(schema_r, 4),
            "points": round(schema_r * WEIGHTS["schema_validity"], 2),
            "max": WEIGHTS["schema_validity"],
            "note": schema_note,
        },
        "evidence_in_transcript": {
            "ratio": round(evidence_r, 4),
            "points": round(evidence_r * WEIGHTS["evidence_in_transcript"], 2),
            "max": WEIGHTS["evidence_in_transcript"],
            "detail": evidence_detail,
        },
        "breakpoint_stage": {
            "ratio": round(bp_r, 4),
            "points": round(bp_r * WEIGHTS["breakpoint_stage"], 2),
            "max": WEIGHTS["breakpoint_stage"],
            "note": bp_note,
        },
        "outcome_status": {
            "ratio": round(out_r, 4),
            "points": round(out_r * WEIGHTS["outcome_status"], 2),
            "max": WEIGHTS["outcome_status"],
            "note": out_note,
        },
        "mistake_category_overlap": {
            "ratio": round(mist_r, 4),
            "points": round(mist_r * WEIGHTS["mistake_category_overlap"], 2),
            "max": WEIGHTS["mistake_category_overlap"],
            "note": mist_note,
        },
        "structure_completeness": {
            "ratio": round(structure_effective, 4),
            "points": round(structure_effective * WEIGHTS["structure_completeness"], 2),
            "max": WEIGHTS["structure_completeness"],
            "note": struct_note,
            "recovery_concepts": {"ratio": round(concept_r, 4), "note": concept_note},
        },
    }

    total = sum(item["points"] for item in breakdown.values())
    return {
        "score": round(total, 2),
        "max_score": 100.0,
        "breakdown": breakdown,
        "gold_id": gold.get("id"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score a QC 4.1 Light candidate report")
    parser.add_argument("report", type=Path, help="Candidate report JSON")
    parser.add_argument("gold_spec", type=Path, help="Gold spec JSON")
    parser.add_argument("transcript", type=Path, help="Call transcript .txt")
    parser.add_argument("--json", action="store_true", help="Print full JSON result")
    args = parser.parse_args(argv)

    report = _load_json(args.report)
    gold = _load_json(args.gold_spec)
    transcript = args.transcript.read_text(encoding="utf-8")
    result = score_report(report, gold, transcript)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"score: {result['score']} / {result['max_score']}")
        for name, block in result["breakdown"].items():
            print(f"  {name}: {block['points']} / {block['max']} (ratio={block['ratio']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
