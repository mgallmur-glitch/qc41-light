#!/usr/bin/env python3
"""Anonymous usage ping for QC 4.1 Light rendered reports.

Fire-and-forget: never blocks rendering, never raises, collects zero PII.
Only counts that a report was rendered, its language and skill version.
Endpoint: https://gallmur.com/api/qc41-light/ping (204 No Content).
"""
from __future__ import annotations

import json
import os
import socket
import urllib.request


def ping_usage(language: str, version: str = "0.3.5") -> None:
    endpoint = os.environ.get("QC41_LIGHT_PING_URL", "").strip()
    if not endpoint:
        return  # telemetry disabled unless explicitly pointed at our endpoint
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
