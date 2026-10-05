#!/usr/bin/env python3
"""Dry-run the shared dashboard and publishing contract for supported hosts."""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOSTS = ("codex", "claude", "cortex")


def command(*parts):
    return subprocess.run([sys.executable, *map(str, parts)], text=True, capture_output=True, check=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_json")
    parser.add_argument("--slug", default="portfolio-review-dry-run")
    args = parser.parse_args()
    validator = command(ROOT / "scripts" / "validate_dashboard_input.py", args.results_json, "--json")
    if validator.returncode:
        print(validator.stdout or validator.stderr, file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "index.html"
        rendered = command(ROOT / "scripts" / "render_dashboard.py", args.results_json, "--blend-export", "--output", output)
        if rendered.returncode:
            print(rendered.stderr, file=sys.stderr)
            return 1
        request = command(ROOT / "scripts" / "publish_request.py", args.results_json, "--html", output, "--slug", args.slug)
        if request.returncode:
            print(request.stderr, file=sys.stderr)
            return 1
        html = output.read_text(encoding="utf-8")
        safe = not any(token in html for token in ("window.openai", "Share on Blend", "Ask Codex"))
        result = {host: {"dashboard": "ready", "blend_adapter": "mocked", "publish_request": "ready" if safe else "blocked"} for host in HOSTS}
        print(json.dumps({"dry_run": "passed" if safe else "failed", "hosts": result}, indent=2))
        return 0 if safe else 1


if __name__ == "__main__":
    sys.exit(main())
