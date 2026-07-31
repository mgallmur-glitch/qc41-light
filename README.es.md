# QC 4.1 Light

[![CI](https://github.com/mgallmur-glitch/qc41-light/actions/workflows/ci.yml/badge.svg)](https://github.com/mgallmur-glitch/qc41-light/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-%3E%3D18-green.svg)](https://nodejs.org/)
[![EN · ES](https://img.shields.io/badge/language-EN%20%7C%20ES-informational.svg)](README.md)

[English](README.md) · **Agentes IA:** [`AGENTS.md`](AGENTS.md)

**La llamada se sintió bien. La transcripción cuenta otra historia.**

QC 4.1 Light es un diagnóstico de llamadas de ventas basado en evidencia: un transcript entra, un reporte estructurado sale — con citas, un punto de ruptura, correcciones y una línea de recuperación hablable.

## Inicio rápido

```bash
git clone https://github.com/mgallmur-glitch/qc41-light.git
cd qc41-light
npm install   # opcional — solo para CLI/MCP
qc41-light demo
```

La demo offline valida y renderiza un reporte sintético — sin API key ni red.

Muestras: [`examples/synthetic-report.es.md`](examples/synthetic-report.es.md) · EN [`examples/synthetic-report.md`](examples/synthetic-report.md)

## Superficies

| Superficie | Comando |
|------------|---------|
| Demo offline | `qc41-light demo` |
| Analizar archivo (BYOK) | `qc41-light analyze --file call.txt --key env` |
| MCP | `qc41-light mcp` |
| Skill / harness | `SKILL.md` + `prompts/analyze-call.md` |
| Claude Code | [`adapters/claude-code/MARKETPLACE.md`](adapters/claude-code/MARKETPLACE.md) |

## Eval

```bash
python3 eval/generate_corpus.py
python3 eval/run_baseline.py
```

Ejecuta el baseline localmente y revisa [`eval/README.md`](eval/README.md) para las definiciones vigentes de referencia y puntaje naive.

## Qué entregas por llamada

Auditoría del transcript · mapa de etapas · dos fortalezas · un breakpoint · objeciones con citas · tres errores + tres correcciones hablables · línea de recuperación · plan de repetición · checklist.

## Límite

Útil y acotado. La metodología QC propietaria queda fuera — `docs/IP_BOUNDARY.md`.

## Privacidad

Sin telemetría en este paquete. CLI/MCP es BYOK local (claves en tu entorno). Redacta llamadas reales antes de enviar transcripts a cualquier modelo — `docs/PRIVACY.md`.

## Estado

Release actual del paquete: [`v0.3.1`](https://github.com/mgallmur-glitch/qc41-light/releases/tag/v0.3.1). El contrato del schema sigue siendo `qc41-light-0.2` por compatibilidad. CLI · MCP · eval están en `main`.

## Licencia

Apache License 2.0.
