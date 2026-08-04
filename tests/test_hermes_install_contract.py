import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"


class TestHermesInstallContract(unittest.TestCase):
    def test_skill_package_version_matches_release(self):
        text = SKILL.read_text()
        self.assertRegex(text, r"(?m)^version: 0\.3\.2$")

    def test_runtime_dependencies_are_markdown_linked_from_skill(self):
        text = SKILL.read_text()
        required = {
            "references/analyze-call.md",
            "references/qc41-light-report.schema.json",
            "references/IP_BOUNDARY.md",
            "references/PRIVACY.md",
            "scripts/validate_report.py",
            "scripts/render_report.py",
        }
        linked = set(re.findall(r"\[[^\]]+\]\(([^)]+)\)", text))
        self.assertTrue(required <= linked, f"missing linked runtime files: {sorted(required-linked)}")
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_runtime_reference_copies_match_canonical_sources(self):
        pairs = {
            "references/analyze-call.md": "prompts/analyze-call.md",
            "references/qc41-light-report.schema.json": "schemas/qc41-light-report.schema.json",
            "references/IP_BOUNDARY.md": "docs/IP_BOUNDARY.md",
            "references/PRIVACY.md": "docs/PRIVACY.md",
        }
        for runtime, canonical in pairs.items():
            self.assertEqual((ROOT/runtime).read_bytes(), (ROOT/canonical).read_bytes(), runtime)

    def test_ci_enforces_node_smoke_and_security_gates(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        for required in (
            "actions/setup-node@v6",
            "npm ci",
            "npm audit --audit-level=moderate",
            "npm test",
        ):
            self.assertIn(required, workflow)

    def test_url_install_shape_can_validate_and_render(self):
        with tempfile.TemporaryDirectory() as td:
            install = Path(td) / "qc41-light"
            for relative in [
                "SKILL.md",
                "references/analyze-call.md",
                "references/qc41-light-report.schema.json",
                "references/IP_BOUNDARY.md",
                "references/PRIVACY.md",
                "scripts/validate_report.py",
                "scripts/render_report.py",
            ]:
                target = install / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, target)
            report = ROOT / "examples/synthetic-report.json"
            check = subprocess.run(
                [sys.executable, str(install/"scripts/validate_report.py"), str(report)],
                text=True, capture_output=True,
            )
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            render = subprocess.run(
                [sys.executable, str(install/"scripts/render_report.py"), str(report)],
                text=True, capture_output=True,
            )
            self.assertEqual(render.returncode, 0, render.stdout + render.stderr)
            self.assertIn("QC 4.1 Light", render.stdout)


if __name__ == "__main__":
    unittest.main()
