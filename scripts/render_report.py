#!/usr/bin/env python3
"""Render a validated bilingual QC 4.1 Light JSON report to Markdown."""
import json, subprocess, sys
from pathlib import Path

if len(sys.argv)!=2:
    print("usage: render_report.py REPORT.json", file=sys.stderr); raise SystemExit(2)
path=Path(sys.argv[1])
validator=Path(__file__).with_name("validate_report.py")
check=subprocess.run([sys.executable,str(validator),str(path)],capture_output=True,text=True)
if check.returncode:
    print(check.stderr,file=sys.stderr); raise SystemExit(check.returncode)
d=json.loads(path.read_text())
es=d["language"]=="es" or d["language"].startswith("es-")
T={
    "title": "Diagnóstico de llamada" if es else "Call Diagnosis",
    "transcript": "Transcripción" if es else "Transcript",
    "labels": "etiquetas de hablante" if es else "speaker labels",
    "timestamps": "marcas de tiempo" if es else "timestamps",
    "outcome": "Resultado" if es else "Outcome",
    "stages": "Mapa de etapas" if es else "Call-stage map",
    "keep": "Qué conservar" if es else "What to keep",
    "breakpoint": "Punto de ruptura más probable" if es else "Most likely breakpoint",
    "stage": "Etapa" if es else "Stage",
    "evidence": "Evidencia" if es else "Evidence",
    "why": "Por qué importó" if es else "Why it mattered",
    "objections": "Objeciones" if es else "Objections",
    "no_obj": "No se observó una objeción respaldada por evidencia." if es else "No supported objection was observed.",
    "confidence": "confianza" if es else "confidence",
    "mistakes": "Tres errores" if es else "Three mistakes",
    "consequence": "Consecuencia" if es else "Consequence",
    "corrections": "Tres correcciones" if es else "Three corrections",
    "fix": "Corrección para" if es else "Fix for",
    "example": "Ejemplo" if es else "Example",
    "recovery": "Línea de recuperación" if es else "Recovery line",
    "replay": "Plan de repetición" if es else "Replay plan",
    "opening": "Apertura" if es else "Opening",
    "followup": "Seguimiento diagnóstico" if es else "Diagnostic follow-up",
    "clarifier": "Clarificador de objeción" if es else "Objection clarifier",
    "nextstep": "Próximo paso" if es else "Next step",
    "focus": "Foco para la próxima llamada" if es else "Next-call focus",
    "checklist": "Checklist de cinco puntos" if es else "Five-point checklist",
    "missing": "Contexto faltante" if es else "Missing context",
    "limitations": "Limitaciones" if es else "Limitations",
    "hero": "Lo que dices en la próxima llamada" if es else "What you say on the next call",
}
print(f"# QC 4.1 Light — {T['title']}\n")
q=d["transcript_quality"]
print(f"**{T['transcript']}:** {q['completeness']} · {T['labels']}: {q['speaker_labels']} · {T['timestamps']}: {q['timestamps']}  ")
print(f"**{T['outcome']}:** `{d['call_outcome']['status']}` — “{d['call_outcome']['evidence']['quote']}”\n")
print(d["call_summary"],"\n")
# Hero: recovery line first — the unfair-free moment
print(f"## {T['hero']}\n")
print(f"> {d['recovery_line']['text']}\n\n{d['recovery_line']['why']}\n")
print(f"## {T['stages']}\n")
for s in d["stage_analysis"]:
    quote=f" — “{s['evidence'][0]['quote']}”" if s["evidence"] else ""
    print(f"- **{s['stage']} · {s['status']}**: {s['finding']}{quote}")
print(f"\n## {T['keep']}\n")
for s in d["strengths"]:
    print(f"- **{s['finding']}** — “{s['evidence']['quote']}” — {s['why_keep']}")
print(f"\n## {T['breakpoint']}\n")
b=d["breakpoint"]
print(f"**{T['stage']}:** `{b['stage']}`  ")
print(f"**{T['evidence']}:** “{b['evidence']['quote']}”  ")
print(f"**{T['why']}:** {b['why_it_mattered']}\n")
print(f"## {T['objections']}\n")
if not d["objections"]: print(T["no_obj"],"\n")
for o in d["objections"]:
    print(f"- **{o['label']}** ({o['confidence']:.0%} {T['confidence']}): “{o['evidence']['quote']}” — {o['interpretation']}")
print(f"\n## {T['mistakes']}\n")
for m in d["mistakes"]:
    print(f"### {m['id']} — {m['finding']}\n- {T['evidence']}: “{m['evidence']['quote']}”\n- {T['consequence']}: {m['consequence']}\n")
print(f"## {T['corrections']}\n")
for c in d["corrections"]:
    print(f"### {T['fix']} {c['mistake_id']}\n{c['action']}\n\n**{T['example']}:** “{c['example_line']}”\n")
print(f"## {T['recovery']}\n")
print(f"> {d['recovery_line']['text']}\n\n{d['recovery_line']['why']}\n")
print(f"## {T['replay']}\n")
rp=d["replay_plan"]
print(f"- **{T['opening']}:** “{rp['opening_question']}”")
print(f"- **{T['followup']}:** “{rp['diagnostic_follow_up']}”")
print(f"- **{T['clarifier']}:** “{rp['objection_clarifier']}”")
print(f"- **{T['nextstep']}:** “{rp['next_step_line']}”\n")
print(f"## {T['focus']}\n")
for x in d["next_call_focus"]: print(f"- {x}")
print(f"\n## {T['checklist']}\n")
for x in d["next_call_checklist"]: print(f"- [ ] {x}")
print(f"\n## {T['confidence'].capitalize()}\n\n**{d['confidence']['score']:.0%}** — {d['confidence']['reason']}\n")
if d['confidence']['missing_context']:
    print(f"{T['missing']}:")
    for x in d['confidence']['missing_context']: print(f"- {x}")
print(f"\n## {T['limitations']}\n")
for x in d["limitations"]: print(f"- {x}")
