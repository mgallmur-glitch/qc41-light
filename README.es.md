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

## Instalar desde GitHub Packages

```bash
npm install @mgallmur-glitch/qc41-light
# o global:
npm install -g @mgallmur-glitch/qc41-light
```

Requiere un PAT de GitHub con `read:packages` (y login a `npm.pkg.github.com`), o instalar desde el tarball del release / clone.

## Superficies

| Superficie | Comando |
|------------|---------|
| Demo offline | `qc41-light demo` |
| Analizar archivo (BYOK) | `qc41-light analyze --file call.txt --key env` |
| MCP | `qc41-light mcp` |
| Skill / harness | `SKILL.md` + `prompts/analyze-call.md` |
| Claude Code | [`adapters/claude-code/MARKETPLACE.md`](adapters/claude-code/MARKETPLACE.md) |

## Instalación en Hermes Agent

```bash
hermes skills install --yes https://raw.githubusercontent.com/mgallmur-glitch/qc41-light/v0.3.5/SKILL.md
```

Luego inicia una sesión nueva e invoca:

```text
/qc41-light Analiza este transcript autorizado y redactado, y devuelve JSON validado.
```

La instalación URL incluye prompt, schema, validator, renderer, privacidad y límite de IP. Versión del paquete/skill: `0.3.5`. Versión del schema del reporte: `qc41-light-0.2`.

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

Un ping anónimo de uso se envía al renderizar un reporte: idioma + versión, nada más (`{"lang":"es","v":"0.3.5"}`). Cero transcript, cero PII; te sales con `QC41_LIGHT_DISABLE_PING=1`. CLI/MCP es BYOK local (claves en tu entorno). Redacta llamadas reales antes de enviar transcripts a cualquier modelo — `docs/PRIVACY.md`.

## ¿Encontró algo real?

Si esta skill detectó un breakpoint que tus closers no veían, déjale una ⭐ — le dice a otros equipos de ventas que el diagnóstico es real. Y si quieres la versión a fondo de la misma metodología sobre una llamada tuya real: [auditoría forense, USD 49, 48h](https://gallmur.com/es/forensic-audit/?utm_source=qc41-light&utm_medium=readme&utm_campaign=forensic-49).

## Estado

Release actual del paquete y la skill: [`v0.3.5`](https://github.com/mgallmur-glitch/qc41-light/releases/tag/v0.3.5). El contrato del schema sigue siendo `qc41-light-0.2` por compatibilidad. Son versiones separadas intencionalmente: los cambios del paquete no alteran la forma del JSON salvo que también cambie la versión del schema. CLI · MCP · eval están en `main`.

## Licencia

Apache License 2.0.
