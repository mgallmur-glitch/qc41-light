#!/usr/bin/env python3
"""Validate a QC 4.1 Light report using only Python stdlib."""
from __future__ import annotations
import json
import sys
from pathlib import Path

STAGES = {"opening","agenda","discovery","problem","impact","solution","proof","price","objection","decision","next_step","unknown"}
OBJECTIONS = {"timing","priority","trust","fit","price","authority","risk","implementation","unknown"}
MISTAKES = {"weak_agenda","premature_pitch","shallow_discovery","missed_follow_up","unsupported_claim","overtalking","weak_transition","objection_not_clarified","pressure","vague_next_step","poor_fit_not_addressed","other"}
TOP = {"version","language","transcript_quality","call_summary","call_outcome","stage_analysis","strengths","breakpoint","objections","mistakes","corrections","recovery_line","replay_plan","next_call_focus","next_call_checklist","confidence","limitations"}


def fail(msg: str) -> None:
    raise ValueError(msg)


def nonempty(value, path: str, minimum: int = 1) -> str:
    if not isinstance(value, str) or len(value.strip()) < minimum:
        fail(f"{path}: expected non-empty string (min {minimum})")
    return value


def evidence(obj, path: str) -> None:
    if not isinstance(obj, dict): fail(f"{path}: expected object")
    if set(obj) != {"quote","speaker","timestamp"}: fail(f"{path}: fields must be quote,speaker,timestamp")
    nonempty(obj["quote"], f"{path}.quote", 2)
    for key in ("speaker","timestamp"):
        if obj[key] is not None and not isinstance(obj[key], str): fail(f"{path}.{key}: expected string or null")


def score(value, path: str) -> None:
    if not isinstance(value, (int,float)) or isinstance(value, bool) or not 0 <= value <= 1:
        fail(f"{path}: expected number between 0 and 1")


def validate(data: dict) -> None:
    if not isinstance(data, dict): fail("root: expected object")
    if set(data) != TOP: fail(f"root fields mismatch; missing={sorted(TOP-set(data))}, extra={sorted(set(data)-TOP)}")
    if data["version"] != "qc41-light-0.2": fail("version: expected qc41-light-0.2")
    nonempty(data["language"], "language", 2)
    if not (data["language"]=="en" or data["language"].startswith("en-") or data["language"]=="es" or data["language"].startswith("es-")):
        fail("language: expected en, es, or a regional variant such as en-US/es-419")

    tq=data["transcript_quality"]
    if not isinstance(tq,dict) or set(tq)!={"completeness","speaker_labels","timestamps","notes"}: fail("transcript_quality: invalid fields")
    if tq["completeness"] not in {"complete","partial","fragment"}: fail("transcript_quality.completeness: invalid")
    if not isinstance(tq["speaker_labels"],bool) or not isinstance(tq["timestamps"],bool): fail("transcript_quality labels/timestamps: expected boolean")
    if not isinstance(tq["notes"],list): fail("transcript_quality.notes: expected array")
    for i,x in enumerate(tq["notes"]): nonempty(x,f"transcript_quality.notes[{i}]",3)

    nonempty(data["call_summary"], "call_summary", 20)
    outcome=data["call_outcome"]
    if not isinstance(outcome,dict) or set(outcome)!={"status","evidence"}: fail("call_outcome: invalid fields")
    if outcome["status"] not in {"won","lost","follow_up","no_decision","disqualified","unknown"}: fail("call_outcome.status: invalid")
    evidence(outcome["evidence"],"call_outcome.evidence")

    stages=data["stage_analysis"]
    if not isinstance(stages,list) or not 3<=len(stages)<=12: fail("stage_analysis: expected 3-12 items")
    for i,s in enumerate(stages):
        p=f"stage_analysis[{i}]"
        if not isinstance(s,dict) or set(s)!={"stage","status","evidence","finding"}: fail(f"{p}: invalid fields")
        if s["stage"] not in STAGES: fail(f"{p}.stage: invalid")
        if s["status"] not in {"strong","partial","weak","not_observed"}: fail(f"{p}.status: invalid")
        if not isinstance(s["evidence"],list) or len(s["evidence"])>3: fail(f"{p}.evidence: expected max 3")
        for j,e in enumerate(s["evidence"]): evidence(e,f"{p}.evidence[{j}]")
        nonempty(s["finding"],f"{p}.finding",10)

    strengths=data["strengths"]
    if not isinstance(strengths,list) or len(strengths)!=2: fail("strengths: expected exactly 2")
    for i,s in enumerate(strengths):
        p=f"strengths[{i}]"
        if not isinstance(s,dict) or set(s)!={"finding","evidence","why_keep"}: fail(f"{p}: invalid fields")
        nonempty(s["finding"],f"{p}.finding",10); evidence(s["evidence"],f"{p}.evidence"); nonempty(s["why_keep"],f"{p}.why_keep",10)

    bp=data["breakpoint"]
    if not isinstance(bp,dict) or set(bp)!={"stage","evidence","why_it_mattered"}: fail("breakpoint: invalid fields")
    if bp["stage"] not in STAGES: fail("breakpoint.stage: invalid")
    evidence(bp["evidence"], "breakpoint.evidence")
    nonempty(bp["why_it_mattered"], "breakpoint.why_it_mattered", 10)

    if not isinstance(data["objections"],list) or len(data["objections"])>5: fail("objections: expected array with max 5")
    for i,o in enumerate(data["objections"]):
        p=f"objections[{i}]"
        if not isinstance(o,dict) or set(o)!={"label","evidence","interpretation","confidence"}: fail(f"{p}: invalid fields")
        if o["label"] not in OBJECTIONS: fail(f"{p}.label: invalid")
        evidence(o["evidence"],f"{p}.evidence")
        nonempty(o["interpretation"],f"{p}.interpretation",10)
        score(o["confidence"],f"{p}.confidence")

    if not isinstance(data["mistakes"],list) or len(data["mistakes"])!=3: fail("mistakes: expected exactly 3")
    ids=[]
    for i,m in enumerate(data["mistakes"]):
        p=f"mistakes[{i}]"
        if not isinstance(m,dict) or set(m)!={"id","category","finding","evidence","consequence"}: fail(f"{p}: invalid fields")
        ids.append(m["id"])
        if m["category"] not in MISTAKES: fail(f"{p}.category: invalid")
        nonempty(m["finding"],f"{p}.finding",10); evidence(m["evidence"],f"{p}.evidence"); nonempty(m["consequence"],f"{p}.consequence",10)
    if ids != ["M1","M2","M3"]: fail("mistakes ids must be M1,M2,M3 in order")

    if not isinstance(data["corrections"],list) or len(data["corrections"])!=3: fail("corrections: expected exactly 3")
    correction_ids=[]
    for i,c in enumerate(data["corrections"]):
        p=f"corrections[{i}]"
        if not isinstance(c,dict) or set(c)!={"mistake_id","action","why","example_line"}: fail(f"{p}: invalid fields")
        correction_ids.append(c["mistake_id"])
        nonempty(c["action"],f"{p}.action",10); nonempty(c["why"],f"{p}.why",10); nonempty(c["example_line"],f"{p}.example_line",5)
    if correction_ids != ["M1","M2","M3"]: fail("correction mistake_ids must map M1,M2,M3 in order")

    r=data["recovery_line"]
    if not isinstance(r,dict) or set(r)!={"text","why"}: fail("recovery_line: invalid fields")
    nonempty(r["text"],"recovery_line.text",10); nonempty(r["why"],"recovery_line.why",10)

    replay=data["replay_plan"]
    replay_keys={"opening_question","diagnostic_follow_up","objection_clarifier","next_step_line"}
    if not isinstance(replay,dict) or set(replay)!=replay_keys: fail("replay_plan: invalid fields")
    for key in replay_keys: nonempty(replay[key],f"replay_plan.{key}",10)

    nf=data["next_call_focus"]
    if not isinstance(nf,list) or not 1<=len(nf)<=3: fail("next_call_focus: expected 1-3 strings")
    for i,x in enumerate(nf): nonempty(x,f"next_call_focus[{i}]",5)

    checklist=data["next_call_checklist"]
    if not isinstance(checklist,list) or len(checklist)!=5: fail("next_call_checklist: expected exactly 5")
    for i,x in enumerate(checklist): nonempty(x,f"next_call_checklist[{i}]",5)

    conf=data["confidence"]
    if not isinstance(conf,dict) or set(conf)!={"score","reason","missing_context"}: fail("confidence: invalid fields")
    score(conf["score"],"confidence.score"); nonempty(conf["reason"],"confidence.reason",10)
    if not isinstance(conf["missing_context"],list): fail("confidence.missing_context: expected array")
    for i,x in enumerate(conf["missing_context"]): nonempty(x,f"confidence.missing_context[{i}]",3)

    if not isinstance(data["limitations"],list) or not data["limitations"]: fail("limitations: expected non-empty array")
    for i,x in enumerate(data["limitations"]): nonempty(x,f"limitations[{i}]",5)


def main() -> int:
    if len(sys.argv)!=2:
        print("usage: validate_report.py REPORT.json", file=sys.stderr); return 2
    try:
        data=json.loads(Path(sys.argv[1]).read_text())
        validate(data)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr); return 1
    print("PASS: valid QC 4.1 Light report")
    return 0

if __name__ == "__main__": raise SystemExit(main())
