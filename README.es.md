# QC 4.1 Light

Diagnóstico portable y basado en evidencia para llamadas de ventas, compatible con agentes de código y harnesses de IA.

Pega una transcripción y recibe:

- auditoría de calidad de la transcripción;
- resultado de la llamada respaldado por evidencia;
- mapa de etapas;
- dos fortalezas que conviene conservar;
- punto de ruptura más probable;
- objeciones explícitas e implícitas respaldadas por citas;
- tres errores observables;
- tres correcciones vinculadas;
- una línea de recuperación;
- plan de repetición de cuatro líneas;
- checklist para la próxima llamada;
- nivel de confianza y limitaciones.

## Bilingüe por diseño

- Transcripción en inglés → diagnóstico completo en inglés.
- Transcripción en español → diagnóstico completo en español neutro latinoamericano.
- Las citas de evidencia se conservan en el idioma original.
- Los campos y enums del JSON permanecen en inglés para mantener compatibilidad entre Hermes, Claude Code, Codex y otros harnesses.

## Qué es

QC 4.1 Light es una capa gratuita, útil y deliberadamente robusta para analizar una llamada individual. Se inspira en la experiencia de Mauricio Gallmur cerrando ventas high-ticket y construyendo Closing Code AI.

No es la metodología QC 4.1 completa, un sistema de gestión de equipos ni un reemplazo de la auditoría profesional.

## Uso rápido

### Hermes Agent

Copia el directorio completo dentro del directorio de skills del perfil:

```text
~/.hermes/skills/qc41-light/
```

Después solicita:

```text
Analiza esta transcripción con qc41-light y devuelve un reporte JSON validado.
```

### Claude Code

Usa:

- `adapters/claude-code/CLAUDE.md`
- `SKILL.md`
- `prompts/analyze-call.md`

### Codex

Usa:

- `adapters/codex/AGENTS.md`
- `SKILL.md`
- `prompts/analyze-call.md`

### Cualquier harness

Compila el prompt completo:

```bash
python3 scripts/build_prompt.py transcript.txt > compiled-prompt.txt
```

Después de obtener el JSON:

```bash
python3 scripts/validate_report.py report.json
python3 scripts/render_report.py report.json > report.md
```

## Privacidad

Este repositorio no incluye uploader, telemetría ni cliente de API. El transcript se procesa dentro del harness que elija el usuario. El usuario debe eliminar datos personales, tener autorización para analizar la llamada y revisar las políticas del modelo utilizado.

## Light vs. producto completo

Light resuelve bien una llamada individual. Closing Code AI y QC 4.1 profesional agregan metodología completa, scoring, profundidad diagnóstica, comparación longitudinal, análisis de equipos, coaching, dashboards, integraciones y soporte.

Consulta `docs/FEATURE_MATRIX.md` y `docs/IP_BOUNDARY.md`.

## Estado

Candidato de release `0.2.0`. El repositorio es privado durante revisión. Aún no publicado, no conectado a una API pública y sin garantía de estabilidad hasta el primer release etiquetado.

## Licencia

Apache License 2.0 para los archivos incluidos en este paquete. Los nombres, taxonomías, prompts, scoring y metodología propietaria que no aparecen en el paquete permanecen reservados.
