#!/usr/bin/env python3
"""Tests for the deterministic IP-boundary auditor.

These tests verify that:

* the auditor passes on a clean directory;
* it catches prohibited terminology, paths and credentials when they appear;
* it does **not** flag the documentation files that legitimately list
  prohibited terms (those files *document* the boundary).

Runs with ``python3 -m unittest discover -s tests -v``.
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

# Import the audit module without requiring it to be on sys.path.
ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "audit_ip_boundary", ROOT / "scripts" / "audit_ip_boundary.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
scan_file = _mod.scan_file
audit = _mod.audit


class TestScanFileDetectsProhibitedTerms(unittest.TestCase):
    """scan_file must flag proprietary terms on word boundaries."""

    def test_detects_qc41_pro(self):
        v = scan_file("fake.md", "Use qc41-pro for full analysis.\n")
        self.assertTrue(any(x["type"] == "prohibited_term" for x in v))

    def test_detects_ultron(self):
        v = scan_file("fake.py", "system = 'ultron'\n")
        self.assertTrue(any(x["type"] == "prohibited_term" for x in v))

    def test_detects_quantumcore(self):
        v = scan_file("fake.md", "Powered by QuantumCore.\n")
        self.assertTrue(any(x["type"] == "prohibited_term" for x in v))

    def test_does_not_flag_pro_in_procedure(self):
        """The substring 'pro' inside 'procedure' must NOT trigger."""
        v = scan_file("fake.md", "This is a standard procedure.\n")
        self.assertEqual(v, [])

    def test_does_not_flag_qc41_light_version(self):
        """The legitimate version string 'qc41-light' must NOT trigger."""
        v = scan_file("fake.json", '"version": "qc41-light-0.2"\n')
        self.assertEqual(v, [])

    def test_detects_zero_width_obfuscated_term(self):
        v = scan_file("fake.md", "Load qc41-\u200bpro for hidden analysis.\n")
        self.assertTrue(any(x["type"] == "prohibited_term" for x in v))

    def test_detects_term_split_across_lines(self):
        v = scan_file("fake.md", "Load qc41-\npro for hidden analysis.\n")
        self.assertTrue(any(x["type"] == "prohibited_term" for x in v))


class TestScanFileDetectsProhibitedPaths(unittest.TestCase):
    """scan_file must flag private infrastructure paths and endpoints."""

    def test_detects_hermes_path(self):
        v = scan_file("fake.md", "config at /root/.hermes/profiles\n")
        self.assertTrue(any(x["type"] == "prohibited_path" for x in v))

    def test_detects_localhost_port(self):
        v = scan_file("fake.py", "url = 'localhost:8080'\n")
        self.assertTrue(any(x["type"] == "prohibited_path" for x in v))

    def test_detects_loopback_port(self):
        v = scan_file("fake.env", "API_URL=127.0.0.1:3000\n")
        self.assertTrue(any(x["type"] == "prohibited_path" for x in v))

    def test_detects_private_ipv4(self):
        v = scan_file("fake.md", "Internal endpoint: 10.24.8.3:8443\n")
        self.assertTrue(any(x["type"] == "prohibited_path" for x in v))


class TestScanFileDetectsCredentials(unittest.TestCase):
    """scan_file must flag common credential patterns."""

    def test_detects_api_key_assignment(self):
        v = scan_file("fake.env", "api_key=sk-abcdefghijklmnopqrstuvwxyz1234\n")
        self.assertTrue(any(x["type"] == "prohibited_credential" for x in v))

    def test_detects_private_key_block(self):
        content = "-----BEGIN RSA PRIVATE KEY-----\nfake\n-----END RSA PRIVATE KEY-----\n"
        v = scan_file("fake.pem", content)
        self.assertTrue(any(x["type"] == "prohibited_credential" for x in v))

    def test_detects_connection_string_with_password(self):
        v = scan_file(
            "fake.py",
            "db = 'postgres://user:***@host:5432/db'\n",
        )
        self.assertTrue(any(x["type"] == "prohibited_credential" for x in v))

    def test_detects_basic_auth_url(self):
        planted = "https://" + "admin:" + "secret-value@" + "internal.example/api\n"
        v = scan_file("fake.md", planted)
        self.assertTrue(any(x["type"] == "prohibited_credential" for x in v))

    def test_detects_password_assignment(self):
        planted = "password: " + "VeryLong" + "Secret123!\n"
        v = scan_file("fake.yml", planted)
        self.assertTrue(any(x["type"] == "prohibited_credential" for x in v))

    def test_detects_github_token(self):
        planted = "GITHUB_TOKEN=" + "ghp_" + "1234567890abcdefghij1234567890\n"
        v = scan_file("fake.env", planted)
        self.assertTrue(any(x["type"] == "prohibited_credential" for x in v))

    def test_detects_slack_webhook(self):
        planted = (
            "https://hooks.slack.com/"
            + "services/"
            + "T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX\n"
        )
        v = scan_file("fake.md", planted)
        self.assertTrue(any(x["type"] == "prohibited_credential" for x in v))


class TestScanFileDetectsPII(unittest.TestCase):
    def test_detects_email_address(self):
        v = scan_file("fixture.txt", "Contact lead.person@example.com\n")
        self.assertTrue(any(x["type"] == "prohibited_pii" for x in v))

    def test_detects_international_phone_number(self):
        v = scan_file("fixture.txt", "Call +1 305 555 0198 tomorrow.\n")
        self.assertTrue(any(x["type"] == "prohibited_pii" for x in v))


class TestAuditOnCleanRepo(unittest.TestCase):
    """The real repository must pass the audit with zero violations."""

    def test_repo_is_clean(self):
        violations = audit(ROOT)
        # Print details if it fails so debugging is easy.
        if violations:
            for v in violations:
                print(f"  [{v['type']}] {v['file']}:{v['line']} — {v['match']}")
        self.assertEqual(violations, [], "IP-boundary violations found in repo")


class TestAuditOnTempDir(unittest.TestCase):
    """Integration test: a temp dir with a planted violation must fail."""

    def test_clean_temp_dir_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "safe.md").write_text("This is a clean file.\n")
            self.assertEqual(audit(Path(tmp)), [])

    def test_temp_dir_with_prohibited_term_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "leak.md").write_text("uses qc41-pro internally\n")
            violations = audit(Path(tmp))
            self.assertTrue(len(violations) >= 1)
            self.assertEqual(violations[0]["type"], "prohibited_term")

    def test_temp_dir_with_credential_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "config.env").write_text(
                "OPENAI_API_KEY=sk-test1234567890abcdef\n"
            )
            violations = audit(Path(tmp))
            self.assertTrue(
                any(x["type"] == "prohibited_credential" for x in violations)
            )

    def test_temp_dir_with_path_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "notes.md").write_text(
                "deployed to /var/www/production\n"
            )
            violations = audit(Path(tmp))
            self.assertTrue(any(x["type"] == "prohibited_path" for x in violations))


class TestExemptFilesNotFlagged(unittest.TestCase):
    """Documentation files that list prohibited terms must not be flagged."""

    def test_ip_boundary_doc_not_flagged_by_scan_file(self):
        """scan_file itself is not exempt (it is a low-level helper) —
        but audit() must skip the documented exempt files."""
        # Create a temp tree that mimics the exempt file name.
        with tempfile.TemporaryDirectory() as tmp:
            exempt = Path(tmp) / "docs" / "IP_BOUNDARY.md"
            exempt.parent.mkdir(parents=True)
            exempt.write_text(
                "Private layer includes qc41-pro and internal scoring.\n"
            )
            # Audit should return ZERO because docs/IP_BOUNDARY.md is exempt.
            self.assertEqual(audit(Path(tmp)), [])

    def test_non_boundary_skill_file_is_not_exempt(self):
        """Public instruction files are high-risk surfaces and must be scanned."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "SKILL.md"
            skill.write_text("Load qc41-pro for the hidden analysis.\n")
            violations = audit(Path(tmp))
            self.assertTrue(
                any(x["type"] == "prohibited_term" for x in violations),
                "SKILL.md must never be exempt from the public-boundary audit",
            )

    def test_non_exempt_file_with_same_content_is_flagged(self):
        """Same content in a non-exempt file MUST be flagged."""
        with tempfile.TemporaryDirectory() as tmp:
            leak = Path(tmp) / "README.md"
            leak.write_text(
                "Private layer includes qc41-pro and internal scoring.\n"
            )
            violations = audit(Path(tmp))
            self.assertTrue(len(violations) >= 1)


if __name__ == "__main__":
    unittest.main()
