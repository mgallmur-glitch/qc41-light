#!/usr/bin/env python3
"""Deterministic IP-boundary auditor for the QC 4.1 Light repository.

Scans every tracked text file for prohibited internal terminology, secret
patterns, and private paths that must never appear in the public-safe package.
Exits non-zero if any violation is found.

Design notes
------------
* The scanner is **word/token based** for prohibited terminology — it matches
  on word boundaries so that the English word ``pro`` inside ``procedure``
  does not trigger a false positive.
* The prohibition **lists themselves** (e.g. the prose in
  ``docs/IP_BOUNDARY.md`` that explains what is private) are explicitly
  excluded from scanning.  Those files *document* the boundary; they are not
  leaks.
* Credential and path patterns use regex.

Usage
-----
::

    python3 scripts/audit_ip_boundary.py [ROOT_DIR]

If ROOT_DIR is omitted the script's parent-parent directory is used.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# ── Files that DOCUMENT the boundary and therefore legitimately contain the
#    prohibited terms as prose.  Their purpose is to explain what is private;
#    scanning them would produce a false positive on every run.
EXEMPT_FILES = {
    "docs/IP_BOUNDARY.md",
    "references/IP_BOUNDARY.md",
    "scripts/audit_ip_boundary.py",
    "tests/test_audit_ip_boundary.py",
}

# ── Commercial-funnel allowlist: files where the continuity-ladder URLs
#    (gallmur.com forensic-audit / closingcodeai.online/teams) are deliberate
#    upgrade pointers, not GTM copy leaks.  The URLs still may not appear
#    anywhere else in the package.
GTM_ALLOWLIST = {
    "SKILL.md",
    "adapters/claude-code/skills/qc41-light/SKILL.md",
    "adapters/codex/skills/qc41-light/SKILL.md",
    "scripts/render_report.py",
    ".github/ISSUE_TEMPLATE/config.yml",
    "README.md",
    "README.es.md",
}

# ── Binary / generated directories to never scan.
SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".mypy_cache",
    ".ruff_cache",
    "playground",
}

# ── File extensions that are safe to read as text.
TEXT_EXTENSIONS = {
    ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml",
    ".html", ".htm", ".css", ".js", ".ts", ".sh", ".cfg", ".ini",
    ".sql", ".xml", ".env", ".tf", ".dockerfile", ".editorconfig",
    ".gitignore", ".yml",
}

# ── Files with no extension that should still be scanned.
NOEXT_FILES = {
    "Dockerfile",
    "Makefile",
    "LICENSE",
    "NOTICE",
}

# ── Prohibited proprietary terminology.
#    Matched as whole words (case-insensitive) using \\b boundaries.
#    ``pro`` alone is NOT here — only the compound proprietary identifiers.
PROHIBITED_TERMS = [
    # Proprietary system / profile identifiers
    "qc41-pro",
    "qc-4-1-pro",
    "qc_4_1_pro",
    "closing-code-ai-internal",
    "ultron",
    "jarvis",
    "quantumcore",
    # Proprietary scoring / taxonomy identifiers
    "diagnostic_depth_level",
    "buyer_taxonomy",
    "close_system_selection",
    "scoring_formula",
    "depth_model",
    # Internal prompt corpus markers
    "internal_prompt_corpus",
    "few_shot_corpus",
    # Commercial upsell / funnel copy must not ship in the public package
    "lead magnet",
]

PROHIBITED_COMMERCIAL = [
    r"\$49\b",
    r"/teams/#team-audit",
    r"\bULTRON\b",
    r"closingcodeai\.online",
    r"Co-authored-by:\s*Cursor",
    r"cursoragent@cursor\.com",
    r"quantum-agent-MGM",
]

# ── Prohibited path / infrastructure patterns (regex, case-insensitive).
PROHIBITED_PATHS = [
    r"/root/\.hermes",
    r"/home/[^/\s]+/\.hermes",
    r"\\Users\\[^\\]+\\\.hermes",
    r"/var/www/",
    r"/opt/closingcode",
    r"/etc/systemd/system/.*closing",
    r"localhost:\d{4,5}",
    r"127\.0\.0\.1:\d{4,5}",
    r"0\.0\.0\.0:\d{4,5}",
    r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})(?::\d{2,5})?\b",
]

# ── Credential / secret patterns (regex).
#    All patterns are compiled with re.IGNORECASE, so no inline (?i) flags
#    are needed inside the individual patterns.
PROHIBITED_CREDENTIALS = [
    # API keys / tokens (generic shapes)
    r"api[_-]?key\s*[:=]\s*['\"]?[a-z0-9_-]{16,}",
    r"secret\s*[:=]\s*['\"]?[a-z0-9_-]{16,}",
    r"access[_-]?token\s*[:=]\s*['\"]?[a-z0-9_-]{16,}",
    r"password\s*[:=]\s*['\"]?[a-z0-9_!@#$%^&*.-]{12,}",
    r"bearer\s+[a-z0-9_-]{20,}",
    r"gh[pousr]_[a-z0-9]{20,}",
    # AWS keys
    r"AKIA[0-9A-Z]{16}",
    r"aws_secret_access_key\s*[:=]",
    # Private keys
    r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    # Connection strings with credentials
    r"(postgres|mongodb|mysql|redis)://[^:\s]+:[^@\s]+@",
    r"https?://[^:/\s]+:[^@\s]+@",
    r"hooks\.slack\.com/services/[a-z0-9/_-]{20,}",
    # Telegram / Slack bot tokens
    r"[0-9]{8,12}:[a-zA-Z0-9_-]{30,}",
    # Common env-var leaks
    r"OPENAI_API_KEY\s*[:=]\s*['\"]?sk-",
    r"ANTHROPIC_API_KEY\s*[:=]",
    r"XAI_API_KEY\s*[:=]",
]

PROHIBITED_PII = [
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    r"\+\d(?:[\s().-]*\d){7,14}\b",
]


def _is_text_file(path: Path) -> bool:
    """Decide whether a file should be read and scanned as text."""
    if path.suffix in TEXT_EXTENSIONS:
        return True
    if path.name in NOEXT_FILES:
        return True
    # Files like ".gitignore" (name starts with dot, no real extension)
    if path.name.startswith(".") and "." not in path.name[1:]:
        return True
    return False


def _should_skip(path: Path, root: Path) -> bool:
    """Return True for exempt files and files inside skipped directories."""
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        return True

    # Skip any file inside a skipped directory.
    parts = rel.split("/")
    if any(part in SKIP_DIRS for part in parts):
        return True

    if rel in EXEMPT_FILES:
        return True

    return False


def _iter_text_files(root: Path):
    """Yield (relative_path, absolute_path) for every scannable text file."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if _should_skip(path, root):
            continue
        if not _is_text_file(path):
            continue
        yield path.relative_to(root).as_posix(), path


# Pre-compile patterns for speed and to validate at import time.
_TERM_RE = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in PROHIBITED_TERMS) + r")\b",
    re.IGNORECASE,
)
_GTM_RE = re.compile("|".join(PROHIBITED_COMMERCIAL), re.IGNORECASE)
_PATH_RE = re.compile("|".join(PROHIBITED_PATHS), re.IGNORECASE)
_CRED_RE = re.compile("|".join(PROHIBITED_CREDENTIALS), re.IGNORECASE)
_PII_RE = re.compile("|".join(PROHIBITED_PII), re.IGNORECASE)
_ZERO_WIDTH_RE = re.compile("[\u200b\u200c\u200d\u2060\ufeff]")
_CROSS_LINE_TERM_RE = re.compile(
    r"\b(?:qc41-|qc-4-1-|qc_4_1_)\s+pro\b", re.IGNORECASE
)


def scan_file(rel: str, content: str) -> list[dict]:
    """Return a list of violation dicts for a single file's content."""
    violations: list[dict] = []
    normalized_content = _ZERO_WIDTH_RE.sub("", content)

    # Detect a proprietary compound deliberately split across physical lines.
    for m in _CROSS_LINE_TERM_RE.finditer(normalized_content):
        violations.append(
            {
                "type": "prohibited_term",
                "file": rel,
                "line": normalized_content.count("\n", 0, m.start()) + 1,
                "match": re.sub(r"\s+", "", m.group(0)),
                "detail": "proprietary terminology split across lines",
            }
        )

    for i, raw_line in enumerate(normalized_content.splitlines(), start=1):
        # Content is normalized before both whole-file and per-line matching.
        line = raw_line
        # Prohibited terminology (word-boundary match)
        for m in _TERM_RE.finditer(line):
            violations.append(
                {
                    "type": "prohibited_term",
                    "file": rel,
                    "line": i,
                    "match": m.group(0),
                    "detail": "proprietary terminology must not appear",
                }
            )
        # Commercial GTM / upgrade-ladder copy (allowlisted files may carry
        # the two deliberate upgrade URLs — anywhere else is a leak)
        if rel not in GTM_ALLOWLIST:
            for m in _GTM_RE.finditer(line):
                violations.append(
                    {
                        "type": "prohibited_gtm",
                        "file": rel,
                        "line": i,
                        "match": m.group(0),
                        "detail": "commercial or non-OSS copy must not appear in this repository",
                    }
                )
        # Prohibited paths / infrastructure
        for m in _PATH_RE.finditer(line):
            violations.append(
                {
                    "type": "prohibited_path",
                    "file": rel,
                    "line": i,
                    "match": m.group(0),
                    "detail": "private path or endpoint must not appear",
                }
            )
        # Credentials / secrets
        for m in _CRED_RE.finditer(line):
            violations.append(
                {
                    "type": "prohibited_credential",
                    "file": rel,
                    "line": i,
                    "match": m.group(0),
                    "detail": "credential or secret pattern detected",
                }
            )
        # Personally identifiable data
        for m in _PII_RE.finditer(line):
            violations.append(
                {
                    "type": "prohibited_pii",
                    "file": rel,
                    "line": i,
                    "match": m.group(0),
                    "detail": "personal data must not appear in the public package",
                }
            )

    return violations


def audit(root: Path) -> list[dict]:
    """Run the full audit and return a flat list of violation dicts."""
    all_violations: list[dict] = []
    for rel, abspath in _iter_text_files(root):
        try:
            content = abspath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        all_violations.extend(scan_file(rel, content))
    return all_violations


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    if not root.is_dir():
        print(f"ERROR: root directory not found: {root}", file=sys.stderr)
        return 2

    violations = audit(root)

    if not violations:
        print(f"PASS: IP-boundary audit clean ({root})")
        return 0

    print(f"FAIL: {len(violations)} IP-boundary violation(s) found:\n", file=sys.stderr)
    for v in violations:
        print(
            f"  [{v['type']}] {v['file']}:{v['line']} — “{v['match']}” — {v['detail']}",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
