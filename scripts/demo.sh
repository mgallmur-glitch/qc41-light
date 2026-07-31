#!/usr/bin/env bash
# One-command demo: validate + render the synthetic QC 4.1 Light example.
# No API key, no network, no third-party deps — stdlib Python only.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

EN_JSON="examples/synthetic-report.json"
ES_JSON="tests/blind-spanish-report.json"

echo "==> QC 4.1 Light demo"
echo "    Validate + render a synthetic English diagnosis (no LLM required)."
echo

echo "==> Validating ${EN_JSON}"
python3 scripts/validate_report.py "${EN_JSON}"

echo
echo "==> Rendering Markdown"
echo "------------------------------------------------------------------------"
python3 scripts/render_report.py "${EN_JSON}"
echo "------------------------------------------------------------------------"

if [[ "${1:-}" == "--es" || "${1:-}" == "--bilingual" ]]; then
  echo
  echo "==> Validating Spanish fixture ${ES_JSON}"
  python3 scripts/validate_report.py "${ES_JSON}"
  echo
  echo "==> Rendering Spanish Markdown"
  echo "------------------------------------------------------------------------"
  python3 scripts/render_report.py "${ES_JSON}"
  echo "------------------------------------------------------------------------"
fi

echo
echo "Done. Shareable samples:"
echo "  examples/synthetic-report.md"
echo "  examples/synthetic-report.es.md"
echo
echo "To diagnose a real transcript with an AI harness, see README.md Quick start."
