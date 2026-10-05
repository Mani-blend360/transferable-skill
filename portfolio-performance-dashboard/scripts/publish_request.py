#!/usr/bin/env python3
"""Build a host-neutral Blend publication request without publishing anything."""

import argparse
import json
import re
import sys
from pathlib import Path

from validate_dashboard_input import load, presentation_state, validate

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NOTICE = ("Notice: This dashboard is a sample created solely for testing the MCP "
          "integration. It is not intended for general distribution or operational use.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_json")
    parser.add_argument("--html", required=True, help="Read-only HTML generated with --blend-export")
    parser.add_argument("--slug", required=True)
    args = parser.parse_args()

    if not SLUG.fullmatch(args.slug):
        parser.error("--slug must contain lowercase letters, numbers, and single dashes")
    payload, load_errors = load(args.results_json)
    errors, _ = (load_errors, []) if load_errors else validate(payload)
    if errors or presentation_state(payload, errors) not in {"ready", "warning"}:
        parser.error("results must be a valid ready or warning dashboard")
    if payload["validation"]["status"] != "PASS" or payload["reconciliation"]["status"] != "PASS":
        parser.error("publishing requires PASS validation and reconciliation")
    html = Path(args.html).read_text(encoding="utf-8")
    if "window.openai" in html or "Share on Blend" in html or "Ask Codex" in html:
        parser.error("HTML is not a safe read-only Blend export")
    print(json.dumps({"path": args.slug, "filename": "index.html", "description": NOTICE,
                      "visibility": "sso", "access_mode": "closed", "comments_enabled": False,
                      "discoverable": False, "html": html}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        print(f"publish request failed: {exc}", file=sys.stderr)
        sys.exit(1)
