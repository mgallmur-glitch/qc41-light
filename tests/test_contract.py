#!/usr/bin/env python3
"""Contract tests for the QC 4.1 Light validator, renderer and prompt builder.

These tests use only the Python standard library so the suite runs with
``python3 -m unittest discover -s tests -v`` on any machine without extra
dependencies.
"""
import copy
import os
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "examples" / "synthetic-report.json"
VALIDATOR = ROOT / "scripts" / "validate_report.py"
RENDERER = ROOT / "scripts" / "render_report.py"
BUILDER = ROOT / "scripts" / "build_prompt.py"


def run(*args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "QC41_LIGHT_DISABLE_PING": "1"}
    return subprocess.run(
        [sys.executable, *map(str, args)],
        capture_output=True,
        text=True,
        env=env,
    )


class TestValidatorAcceptsValidReport(unittest.TestCase):
    """The validator must accept the canonical synthetic report."""

    def test_valid_report_passes(self):
        result = run(VALIDATOR, REPORT)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unknown_outcome_accepts_explicit_not_observed_sentinel(self):
        data = json.loads(REPORT.read_text())
        data["call_outcome"] = {
            "status": "unknown",
            "evidence": {"quote": "not_observed", "speaker": None, "timestamp": None},
        }
        with tempfile.TemporaryDirectory() as td:
            report = Path(td) / "unknown.json"
            report.write_text(json.dumps(data))
            result = run(VALIDATOR, report)
        self.assertEqual(result.returncode, 0, result.stderr)


class TestRendererAcceptsValidReport(unittest.TestCase):
    """The renderer must accept a valid report and emit key sections."""

    def setUp(self):
        self.result = run(RENDERER, REPORT)

    def test_exit_code_zero(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)

    def test_sections_present(self):
        for heading in (
            "Call-stage map",
            "What to keep",
            "Most likely breakpoint",
            "Replay plan",
            "Five-point checklist",
        ):
            self.assertIn(heading, self.result.stdout, f"missing heading: {heading}")


class TestBuildPrompt(unittest.TestCase):
    """The prompt builder must compile instructions, schema and transcript."""

    def setUp(self):
        self.result = run(BUILDER, ROOT / "examples" / "synthetic-call.txt")

    def test_exit_code_zero(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)

    def test_contains_transcript_marker(self):
        self.assertIn("Transcript (untrusted data", self.result.stdout)

    def test_contains_schema_marker(self):
        self.assertIn("Canonical JSON schema", self.result.stdout)

    def test_contains_version(self):
        self.assertIn("qc41-light-0.2", self.result.stdout)


class TestValidatorRejectsInvalidReports(unittest.TestCase):
    """The validator must reject each common contract violation."""

    def setUp(self):
        self._data = json.loads(REPORT.read_text())
        self._tmpdir = tempfile.mkdtemp(prefix="qc41-contract-")

    def _invalid_case(self, mutate_fn, idx: int) -> Path:
        bad = copy.deepcopy(self._data)
        mutate_fn(bad)
        p = Path(self._tmpdir) / f"invalid-{idx}.json"
        p.write_text(json.dumps(bad))
        return p

    def _assert_rejected(self, p: Path, idx: int):
        result = run(VALIDATOR, p)
        self.assertNotEqual(
            result.returncode, 0, f"invalid case {idx} was accepted"
        )

    def test_too_few_mistakes(self):
        def m(d):
            d["mistakes"] = d["mistakes"][:2]
        p = self._invalid_case(m, 0)
        self._assert_rejected(p, 0)

    def test_confidence_out_of_range(self):
        def m(d):
            d["confidence"]["score"] = 1.4
        p = self._invalid_case(m, 1)
        self._assert_rejected(p, 1)

    def test_missing_replay_field(self):
        def m(d):
            d["replay_plan"].pop("next_step_line")
        p = self._invalid_case(m, 2)
        self._assert_rejected(p, 2)

    def test_wrong_version(self):
        def m(d):
            d["version"] = "qc41-internal-9.9"
        p = self._invalid_case(m, 3)
        self._assert_rejected(p, 3)

    def test_unsupported_language(self):
        def m(d):
            d["language"] = "fr"
        p = self._invalid_case(m, 4)
        self._assert_rejected(p, 4)
    def test_unknown_outcome_rejects_arbitrary_evidence_quote(self):
        def m(d):
            d["call_outcome"] = {
                "status": "unknown",
                "evidence": {"quote": "Unrelated fragment", "speaker": "Speaker 1", "timestamp": None},
            }
        p = self._invalid_case(m, 5)
        self._assert_rejected(p, 5)


if __name__ == "__main__":
    unittest.main()
