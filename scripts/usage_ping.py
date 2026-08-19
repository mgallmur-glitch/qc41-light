#!/usr/bin/env python3
"""Anonymous usage ping for QC 4.1 Light rendered reports.

Fire-and-forget: never blocks rendering, never raises, collects zero PII.
Sends only that a report was rendered, its language and skill version.
Opt out with QC41_LIGHT_DISABLE_PING=1 (any non-empty value).
"""
from __future__ import annotations

import json
import os
import urllib.request

DEFAULT_ENDPOINT = "https://gallmur.com/api/qc41-light/ping"


def ping_usage(language: str, version: str = "0.3.5") -> None:
    if os.environ.get("QC41_LIGHT_DISABLE_PING", "").strip():
        return  # explicit opt-out
    endpoint = os.environ.get("QC41_LIGHT_PING_URL", DEFAULT_ENDPOINT).strip()
    if not endpoint or not endpoint.startswith("https://"):
        return
    payload = json.dumps({"lang": language, "v": version}).encode()
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=2)  # noqa: S310
    except Exception:
        pass  # never block the report on telemetry


if __name__ == "__main__":
    lang = os.environ.get("QC41_LIGHT_LANG", "es")
    ping_usage(lang)
    print("ping sent")
