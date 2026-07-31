#!/usr/bin/env python3
"""Regression tests for English and Spanish blind fixtures.

Runs with ``python3 -m unittest discover -s tests -v``.
Uses only the Python standard library.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_report.py"
RENDERER = ROOT / "scripts" / "render_report.py"
CASES = [
    (
        "en",
        ROOT / "tests" / "blind-english-call.txt",
        ROOT / "tests" / "blind-english-report.json",
        ["Call-stage map", "What to keep", "Replay plan", "Five-point checklist"],
    ),
    (
        "es",
        ROOT / "tests" / "blind-spanish-call.txt",
        ROOT / "tests" / "blind-spanish-report.json",
        [
            "Mapa de etapas",
            "Qué conservar",
            "Plan de repetición",
            "Checklist de cinco puntos",
        ],
    ),
]


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *map(str, args)],
        capture_output=True,
        text=True,
    )


def quotes_in(obj):
    """Collect every evidence quote from a nested JSON object."""
    out = []

    def walk(x):
        if isinstance(x, dict):
            if {"quote", "speaker", "timestamp"} <= set(x):
                out.append(x["quote"])
            for value in x.values():
                walk(value)
        elif isinstance(x, list):
            for value in x:
                walk(value)

    walk(obj)
    return out


class TestBilingualFixtures(unittest.TestCase):
    """Validate every blind fixture in English and Spanish."""

    def _check_case(self, language, transcript_path, report_path, headings):
        # 1. Validator accepts the report.
        check = run(VALIDATOR, report_path)
        self.assertEqual(check.returncode, 0, check.stderr)

        # 2. Language field matches.
        data = json.loads(report_path.read_text())
        self.assertTrue(
            data["language"] == language or data["language"].startswith(language + "-"),
            f"{language}: language field mismatch: {data['language']}",
        )

        # 3. Every evidence quote appears verbatim in the transcript.
        transcript = transcript_path.read_text()
        quotes = quotes_in(data)
        missing = [q for q in quotes if q not in transcript]
        self.assertEqual(
            missing, [], f"{language}: missing exact quotes: {missing}"
        )

        # 4. Renderer accepts and emits localized sections.
        render = run(RENDERER, report_path)
        self.assertEqual(render.returncode, 0, render.stderr)
        for heading in headings:
            self.assertIn(
                heading, render.stdout, f"{language}: missing heading: {heading}"
            )

    def test_english_fixture(self):
        lang, transcript, report, headings = CASES[0]
        self._check_case(lang, transcript, report, headings)

    def test_spanish_fixture(self):
        lang, transcript, report, headings = CASES[1]
        self._check_case(lang, transcript, report, headings)


if __name__ == "__main__":
    unittest.main()
