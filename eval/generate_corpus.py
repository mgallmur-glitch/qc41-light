#!/usr/bin/env python3
"""Generate 50 synthetic sales-call eval items (EN/ES) + gold specs.

Item 000 mirrors ``examples/synthetic-call.txt``. Remaining items cycle
public failure modes. Stdlib only. Idempotent unless ``--force``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = Path(__file__).resolve().parent / "corpus"
EXAMPLES_CALL = ROOT / "examples" / "synthetic-call.txt"

FAILURE_MODES = [
    ("premature_pitch", "discovery", "follow_up", ["premature_pitch", "shallow_discovery", "vague_next_step"]),
    ("shallow_discovery", "discovery", "no_decision", ["shallow_discovery", "unsupported_claim", "vague_next_step"]),
    ("objection_not_clarified", "objection", "follow_up", ["objection_not_clarified", "pressure", "vague_next_step"]),
    ("vague_next_step", "next_step", "follow_up", ["vague_next_step", "weak_agenda", "missed_follow_up"]),
    ("pressure", "price", "lost", ["pressure", "objection_not_clarified", "premature_pitch"]),
    ("unsupported_claim", "solution", "no_decision", ["unsupported_claim", "shallow_discovery", "weak_transition"]),
    ("weak_agenda", "opening", "follow_up", ["weak_agenda", "premature_pitch", "vague_next_step"]),
    ("price_before_value", "price", "follow_up", ["premature_pitch", "shallow_discovery", "objection_not_clarified"]),
    ("missed_implementation_risk", "objection", "no_decision", ["objection_not_clarified", "unsupported_claim", "vague_next_step"]),
    ("overtalking", "discovery", "follow_up", ["overtalking", "shallow_discovery", "weak_transition"]),
    ("missed_follow_up", "next_step", "lost", ["missed_follow_up", "vague_next_step", "weak_transition"]),
    ("weak_transition", "solution", "follow_up", ["weak_transition", "premature_pitch", "shallow_discovery"]),
    ("poor_fit_not_addressed", "solution", "disqualified", ["poor_fit_not_addressed", "pressure", "premature_pitch"]),
]

CONCEPTS = {
    "en": ["clarify", "next step", "adoption"],
    "es": ["aclarar", "siguiente paso", "adopción"],
}


def en_call(mode: str, i: int) -> str:
    crm = f"AcmeCRM-{i:02d}"
    templates = {
        "premature_pitch": f"""[00:00] SELLER: Thanks for joining. Let me share my screen and walk the roadmap.
[00:18] PROSPECT: I mainly wanted to know if this works with {crm}.
[00:30] SELLER: Absolutely, and we also have AI scoring, sequences, analytics, coaching, and Slack alerts.
[00:55] PROSPECT: Okay… we tried a tool last year and the team abandoned it.
[01:10] SELLER: Ours is different because the AI is much better. Setup is $2,000 then $600 a month.
[01:28] PROSPECT: That is more than expected. I need to think.
[01:36] SELLER: If you sign this week I can discount setup twenty percent.
[01:48] PROSPECT: Send me a deck and I will review it.
[01:55] SELLER: Perfect, sending now.""",
        "shallow_discovery": f"""[00:00] SELLER: Quick call — what is broken in your pipeline today?
[00:12] PROSPECT: Follow-up is inconsistent after demos.
[00:22] SELLER: Got it. Our sequences fix that. Want a two-minute tour?
[00:35] PROSPECT: Maybe. Who owns follow-up on your side usually?
[00:48] SELLER: Does not matter — the product handles it. Look at this dashboard.
[01:05] PROSPECT: We have compliance constraints in {crm}.
[01:18] SELLER: Everyone says that. Clients love us. Shall I send pricing?
[01:30] PROSPECT: Not yet. I will talk to ops.
[01:38] SELLER: Cool, ping me anytime.""",
        "objection_not_clarified": f"""[00:00] SELLER: Agenda is simple: fit, rollout, commercials.
[00:15] PROSPECT: Sounds good. Budget is tight this quarter.
[00:28] SELLER: Understood. Most teams ROI in thirty days.
[00:42] PROSPECT: Last vendor promised the same and failed adoption.
[00:55] SELLER: We are different. Our onboarding is white-glove.
[01:10] PROSPECT: I still need to think about it.
[01:18] SELLER: Thinking usually means price — I can do 15% off today.
[01:32] PROSPECT: Email me. I am not deciding today.
[01:40] SELLER: Done.""",
        "vague_next_step": f"""[00:00] SELLER: Thanks for the time. What would make this useful today?
[00:14] PROSPECT: See whether managers can review calls without listening for an hour.
[00:30] SELLER: Yes — we surface breakpoints and recovery lines automatically.
[00:48] PROSPECT: Interesting. We would need security review.
[01:02] SELLER: We can handle that. I will send materials.
[01:12] PROSPECT: Okay.
[01:18] SELLER: Great talking. Let me know what you think.
[01:25] PROSPECT: Sure.""",
        "pressure": f"""[00:00] SELLER: Pricing starts at $500/mo. Can you approve this week?
[00:14] PROSPECT: We just started evaluating. I have not seen a workflow demo.
[00:28] SELLER: Spots are limited for onboarding this month.
[00:40] PROSPECT: That feels rushed.
[00:48] SELLER: If you wait, implementation slips to Q4 and you lose another quarter.
[01:05] PROSPECT: I need my partner on the call.
[01:14] SELLER: Bring them tomorrow or the discount expires.
[01:25] PROSPECT: I will pass for now.""",
        "unsupported_claim": f"""[00:00] SELLER: We increase close rates by 40% for every customer.
[00:14] PROSPECT: Based on what sample size?
[00:22] SELLER: Trust me, it is consistent. AI is magic now.
[00:36] PROSPECT: We need proof in our niche — field services.
[00:48] SELLER: It works for everyone. Here is the feature list.
[01:05] PROSPECT: Without proof I cannot champion this internally.
[01:18] SELLER: I can send logos.
[01:25] PROSPECT: Logos are not outcomes. Let us stop here.""",
        "weak_agenda": f"""[00:00] SELLER: Hey! How is your day?
[00:08] PROSPECT: Fine. I have 20 minutes.
[00:15] SELLER: Cool cool. Sooo… yeah we built this thing for sales teams.
[00:30] PROSPECT: What problem does it solve first?
[00:38] SELLER: A lot of things honestly. Coaching, CRM, WhatsApp, whatever.
[00:55] PROSPECT: I need one primary use case.
[01:05] SELLER: Let me just click around.
[01:18] PROSPECT: Maybe reschedule when there is an agenda.
[01:28] SELLER: Okay.""",
        "price_before_value": f"""[00:00] SELLER: Before we dig in, packages are 497, 997, and 2497.
[00:16] PROSPECT: I do not know what I am buying yet.
[00:25] SELLER: Fair. Mid tier is most popular.
[00:36] PROSPECT: What changes in my weekly coaching meeting?
[00:48] SELLER: Everything. AI. Automation. Scale.
[01:00] PROSPECT: That is vague. Also we are on {crm}.
[01:12] SELLER: Integration is easy. Want a discount on annual?
[01:24] PROSPECT: Send info. No decision today.""",
        "missed_implementation_risk": f"""[00:00] SELLER: Discovery looks solid — manual notes, missed follow-ups.
[00:18] PROSPECT: Right. But the last CRM failed because reps hated the UI.
[00:32] SELLER: Ours is beautiful. You will love it.
[00:42] PROSPECT: What is the rollout plan for ten closers?
[00:55] SELLER: You just turn it on. Super simple.
[01:08] PROSPECT: Who trains managers? Who owns QA in week one?
[01:20] SELLER: Support can help. Shall we talk pricing?
[01:32] PROSPECT: Not until rollout is concrete.""",
        "overtalking": f"""[00:00] SELLER: I will tell you our story, founding myth, roadmap, and vision for AI sales.
[00:25] PROSPECT: I only have—
[00:28] SELLER: —and then the architecture, the models, the data flywheel, the moat…
[00:50] PROSPECT: Can I ask about CRM sync?
[00:55] SELLER: Yes after I finish this part. So in 2019…
[01:20] PROSPECT: I need to drop. Email me.
[01:28] SELLER: Wait one more slide.""",
        "missed_follow_up": f"""[00:00] SELLER: Thanks for the intro from Alex.
[00:08] PROSPECT: We are comparing three vendors this month.
[00:16] SELLER: Great. Here is why we win on speed with {crm}.
[00:28] PROSPECT: Useful. Can you send security docs and book a technical review?
[00:38] SELLER: Yes I can send docs.
[00:44] PROSPECT: And the technical review?
[00:48] SELLER: Someone will reach out if needed. Bye!""",
        "weak_transition": f"""[00:00] SELLER: What is breaking in your onboarding today?
[00:10] PROSPECT: New hires take eight weeks to ramp and still miss discovery questions.
[00:22] SELLER: Speaking of questions, look at this pricing calculator on screen.
[00:34] PROSPECT: We were still on the ramp problem.
[00:40] SELLER: Right, and the calculator shows ROI once they ramp faster.
[00:52] PROSPECT: You skipped confirming the problem. Email me later.""",
        "poor_fit_not_addressed": f"""[00:00] SELLER: Excited to show the enterprise suite for {crm}.
[00:10] PROSPECT: We are two founders. We need a lightweight CRM sync only.
[00:22] SELLER: Enterprise still works. Minimum is twenty-four thousand a year.
[00:34] PROSPECT: That is not a fit for us.
[00:40] SELLER: Most startups grow into it. Sign a pilot today.
[00:50] PROSPECT: No. Please remove us from the pipeline.""",
    }
    key = mode if mode in templates else "premature_pitch"
    return templates[key].strip() + "\n"


def es_call(mode: str, i: int) -> str:
    crm = f"CRM-{i:02d}"
    templates = {
        "premature_pitch": f"""[00:00] ASESOR: Gracias por estar. Te comparto pantalla y el roadmap.
[00:18] PROSPECTO: Quería saber si funciona con {crm}.
[00:30] ASESOR: Claro, y además tenemos IA, secuencias, analítica y coaching.
[00:55] PROSPECTO: El año pasado un tool quedó abandonado por el equipo.
[01:10] ASESOR: Este es distinto: la IA es mucho mejor. Setup 2000 y 600 al mes.
[01:28] PROSPECTO: Es más de lo que esperaba. Lo tengo que pensar.
[01:36] ASESOR: Si firmas esta semana te bajo el setup un 20%.
[01:48] PROSPECTO: Mándame un deck y lo reviso.
[01:55] ASESOR: Perfecto, te lo mando.""",
        "shallow_discovery": f"""[00:00] ASESOR: ¿Qué está roto en tu pipeline hoy?
[00:12] PROSPECTO: El seguimiento después de demos es inconsistente.
[00:22] ASESOR: Nuestras secuencias lo resuelven. ¿Te muestro dos minutos?
[00:35] PROSPECTO: Tal vez. ¿Quién es dueño del follow-up hoy?
[00:48] ASESOR: No importa, el producto lo hace. Mira el dashboard.
[01:05] PROSPECTO: Tenemos restricciones de cumplimiento en {crm}.
[01:18] ASESOR: Todos dicen eso. ¿Te mando precios?
[01:30] PROSPECTO: Todavía no. Voy a hablar con operaciones.
[01:38] ASESOR: Dale, avísame.""",
        "objection_not_clarified": f"""[00:00] ASESOR: Agenda: encaje, implementación y números.
[00:15] PROSPECTO: Bien. El presupuesto este trimestre está apretado.
[00:28] ASESOR: Entiendo. La mayoría recupera en treinta días.
[00:42] PROSPECTO: El proveedor anterior prometió lo mismo y falló la adopción.
[00:55] ASESOR: Nosotros somos distintos. Onboarding white-glove.
[01:10] PROSPECTO: Igual lo tengo que pensar.
[01:18] ASESOR: Pensar suele ser precio — te puedo hacer 15% hoy.
[01:32] PROSPECTO: Mándame un correo. Hoy no decido.
[01:40] ASESOR: Listo.""",
        "vague_next_step": f"""[00:00] ASESOR: ¿Qué haría útil esta llamada?
[00:14] PROSPECTO: Ver si los managers pueden revisar llamadas sin escuchar una hora.
[00:30] ASESOR: Sí — marcamos el punto de ruptura y la línea de recuperación.
[00:48] PROSPECTO: Interesante. Necesitaríamos revisión de seguridad.
[01:02] ASESOR: Lo manejamos. Te mando materiales.
[01:12] PROSPECTO: Ok.
[01:18] ASESOR: Buen chat. Me dices qué te parece.
[01:25] PROSPECTO: Sí.""",
        "pressure": f"""[00:00] ASESOR: El plan empieza en 500 al mes. ¿Puedes aprobar esta semana?
[00:14] PROSPECTO: Recién empezamos a evaluar. No vi el flujo.
[00:28] ASESOR: Quedan pocos cupos de onboarding este mes.
[00:40] PROSPECTO: Se siente apurado.
[00:48] ASESOR: Si esperas, la implementación se va a Q4.
[01:05] PROSPECTO: Necesito a mi socio en la llamada.
[01:14] ASESOR: Tráelo mañana o se acaba el descuento.
[01:25] PROSPECTO: Por ahora paso.""",
        "unsupported_claim": f"""[00:00] ASESOR: Subimos el close rate un 40% a todos los clientes.
[00:14] PROSPECTO: ¿Con qué muestra?
[00:22] ASESOR: Confía, es consistente. La IA es magia.
[00:36] PROSPECTO: Necesito prueba en nuestro nicho.
[00:48] ASESOR: Sirve para todos. Aquí va el listado de features.
[01:05] PROSPECTO: Sin prueba no lo puedo defender adentro.
[01:18] ASESOR: Te mando logos.
[01:25] PROSPECTO: Logos no son resultados. Paramos aquí.""",
        "weak_agenda": f"""[00:00] ASESOR: ¡Hola! ¿Cómo va tu día?
[00:08] PROSPECTO: Bien. Tengo 20 minutos.
[00:15] ASESOR: Genial… construimos esto para equipos de ventas.
[00:30] PROSPECTO: ¿Qué problema resuelve primero?
[00:38] ASESOR: Muchas cosas: coaching, CRM, WhatsApp, lo que sea.
[00:55] PROSPECTO: Necesito un caso de uso primario.
[01:05] ASESOR: Déjame clickear un rato.
[01:18] PROSPECTO: Mejor reagendamos con agenda.
[01:28] ASESOR: Ok.""",
        "price_before_value": f"""[00:00] ASESOR: Antes de entrar: paquetes 497, 997 y 2497.
[00:16] PROSPECTO: Todavía no sé qué estoy comprando.
[00:25] ASESOR: El mid es el más popular.
[00:36] PROSPECTO: ¿Qué cambia en mi reunión semanal de coaching?
[00:48] ASESOR: Todo. IA. Automatización. Escala.
[01:00] PROSPECTO: Es vago. Además estamos en {crm}.
[01:12] ASESOR: La integración es fácil. ¿Descuento anual?
[01:24] PROSPECTO: Mándame info. Hoy no decido.""",
        "missed_implementation_risk": f"""[00:00] ASESOR: El discovery cuadra: notas manuales y follow-ups perdidos.
[00:18] PROSPECTO: Sí. Pero el CRM anterior falló porque los reps odiaban la UI.
[00:32] ASESOR: La nuestra es hermosa. Les va a encantar.
[00:42] PROSPECTO: ¿Cuál es el plan de rollout para diez closers?
[00:55] ASESOR: Solo lo enciendes. Súper simple.
[01:08] PROSPECTO: ¿Quién entrena managers? ¿Quién hace QA la semana uno?
[01:20] ASESOR: Soporte ayuda. ¿Hablamos de precio?
[01:32] PROSPECTO: No hasta que el rollout sea concreto.""",
        "overtalking": f"""[00:00] ASESOR: Te cuento la historia, el roadmap y la visión de IA.
[00:25] PROSPECTO: Solo tengo—
[00:28] ASESOR: —y la arquitectura, los modelos, el data flywheel…
[00:50] PROSPECTO: ¿Puedo preguntar por el sync del CRM?
[00:55] ASESOR: Sí, después de esta parte. Entonces en 2019…
[01:20] PROSPECTO: Tengo que salir. Mándame un correo.
[01:28] ASESOR: Espera una slide más.""",
        "missed_follow_up": f"""[00:00] VENDEDORA: Gracias por la referencia de Carla.
[00:08] PROSPECTO: Estamos eligiendo proveedor este mes.
[00:16] VENDEDORA: Genial. Somos más rápidos con {crm}.
[00:28] PROSPECTO: ¿Puedes enviar el cuestionario de seguridad y agendar revisión técnica?
[00:40] VENDEDORA: Te envío el cuestionario.
[00:46] PROSPECTO: ¿Y la revisión técnica?
[00:50] VENDEDORA: Si hace falta alguien avisa. ¡Éxito!""",
        "weak_transition": f"""[00:00] ASESORA: ¿Qué se rompe en tu onboarding hoy?
[00:10] PROSPECTO: Los nuevos tardan ocho semanas y fallan en descubrimiento.
[00:22] ASESORA: Hablando de eso, mira esta calculadora de precios.
[00:34] PROSPECTO: Seguíamos en el problema de rampa.
[00:40] ASESORA: Sí, y la calculadora muestra el ROI cuando rampan más rápido.
[00:52] PROSPECTO: Saltaste confirmar el problema. Escríbeme luego.""",
        "poor_fit_not_addressed": f"""[00:00] CONSULTOR: Te presento el plan enterprise.
[00:10] PROSPECTO: Somos un equipo de tres. Solo necesitamos sync liviano.
[00:22] CONSULTOR: Enterprise igual sirve. Mínimo dieciocho mil al año.
[00:34] PROSPECTO: No encaja.
[00:38] CONSULTOR: Firmen el piloto hoy y crecen después.
[00:48] PROSPECTO: Sáquenme del pipeline, por favor.""",
    }
    key = mode if mode in templates else "premature_pitch"
    return templates[key].strip() + "\n"


def _write_json(path: Path, data: dict, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True


def _write_text(path: Path, text: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def gold_spec(item_id: str, mode: str, lang: str, breakpoint: str, outcome: str, mistakes: list[str]) -> dict:
    return {
        "id": item_id,
        "expected_breakpoint_stage": breakpoint,
        "accepted_breakpoint_stages": [],
        "expected_outcome": outcome,
        "accepted_outcomes": ["follow_up", "no_decision"] if outcome in {"follow_up", "no_decision"} else [],
        "expected_mistake_categories": mistakes,
        "gold_recovery_must_include_concepts": CONCEPTS["es" if lang == "es" else "en"],
        "failure_mode": mode,
        "require_evidence_in_transcript": True,
        "min_mistakes": 3,
        "min_corrections": 3,
        "require_recovery_line": True,
    }


def item_000(force: bool) -> int:
    """Canonical fixture mirrored from examples/."""
    written = 0
    call = EXAMPLES_CALL.read_text(encoding="utf-8")
    meta = {
        "id": "000",
        "language": "en",
        "failure_mode": "premature_pitch",
        "expected_breakpoint_stage": "discovery",
        "expected_outcome": "follow_up",
        "expected_mistake_categories": [
            "premature_pitch",
            "objection_not_clarified",
            "vague_next_step",
        ],
        "gold_recovery_must_include_concepts": ["adopt", "discount", "failed"],
        "source": "examples/synthetic-call.txt",
    }
    gold = {
        "id": "000",
        "expected_breakpoint_stage": "discovery",
        "accepted_breakpoint_stages": ["solution", "price"],
        "expected_outcome": "follow_up",
        "accepted_outcomes": ["no_decision"],
        "expected_mistake_categories": [
            "premature_pitch",
            "objection_not_clarified",
            "vague_next_step",
        ],
        "gold_recovery_must_include_concepts": ["adopt", "discount", "failed"],
        "require_recovery_line": True,
        "min_mistakes": 3,
        "min_corrections": 3,
    }
    if _write_text(CORPUS / "000.call.txt", call, force):
        written += 1
    if _write_json(CORPUS / "000.meta.json", meta, force):
        written += 1
    if _write_json(CORPUS / "000.gold_spec.json", gold, force):
        written += 1
    return written


def generate(force: bool = False) -> int:
    CORPUS.mkdir(parents=True, exist_ok=True)
    written = item_000(force)

    for n in range(1, 50):
        mode, bp, outcome, mistakes = FAILURE_MODES[(n - 1) % len(FAILURE_MODES)]
        lang = "en" if n % 2 == 1 else "es"
        idx = f"{n:03d}"
        call = en_call(mode, n) if lang == "en" else es_call(mode, n)
        concepts = CONCEPTS["es" if lang == "es" else "en"]
        meta = {
            "id": idx,
            "language": lang,
            "failure_mode": mode,
            "expected_breakpoint_stage": bp,
            "expected_outcome": outcome,
            "expected_mistake_categories": mistakes,
            "gold_recovery_must_include_concepts": concepts,
        }
        if _write_text(CORPUS / f"{idx}.call.txt", call, force):
            written += 1
        if _write_json(CORPUS / f"{idx}.meta.json", meta, force):
            written += 1
        if _write_json(CORPUS / f"{idx}.gold_spec.json", gold_spec(idx, mode, lang, bp, outcome, mistakes), force):
            written += 1

    metas = list(CORPUS.glob("*.meta.json"))
    en = sum(1 for p in metas if json.loads(p.read_text(encoding="utf-8"))["language"] == "en")
    es = sum(1 for p in metas if json.loads(p.read_text(encoding="utf-8"))["language"] == "es")
    print(f"corpus ready: {len(metas)} items (en={en}, es={es}); files written this run: {written}")
    if len(metas) != 50:
        raise SystemExit(f"expected 50 meta files, got {len(metas)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate eval corpus (50 synthetic calls)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing corpus files")
    args = parser.parse_args(argv)
    return generate(force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())
