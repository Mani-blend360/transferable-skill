#!/usr/bin/env python3
"""Render a Claude Code dashboard artifact with a copy-to-chat Blend handoff."""

import argparse
import sys
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
for scripts_dir in (THIS_FILE.parent, THIS_FILE.parents[3] / "scripts"):
    if (scripts_dir / "render_dashboard.py").is_file():
        sys.path.insert(0, str(scripts_dir))
        break

from render_dashboard import load, presentation_state, render, validate


FALLBACK = """else{const publishPrompt=`Publish this explicitly user-confirmed dashboard to Blend at path ${slug}. Render the read-only Blend export with scripts/render_dashboard.py and call the configured Blend MCP path check followed by upload. Do not upload raw CSV or RESULTS.json. Use visibility sso, access_mode closed, comments_enabled false, and discoverable false. Report the final URL or error.`;try{await navigator.clipboard.writeText(publishPrompt)}catch{const area=document.createElement('textarea');area.value=publishPrompt;document.body.appendChild(area);area.select();document.execCommand('copy');area.remove()}shareError.textContent='Publish request copied. Paste it into Claude chat and send it to publish.';shareError.hidden=false;shareSubmit.disabled=false;shareCancel.disabled=false}})}"""


def normalize(payload, errors):
    """Keep the shared dashboard surface renderable when Claude receives a partial payload."""
    if not isinstance(payload, dict):
        return {
            "company": "Portfolio review", "period": "Unavailable", "synthetic": False,
            "status": "blocked",
            "validation": {"status": "FAIL", "errors": errors, "warnings": []},
            "reconciliation": {"status": "NOT_RUN", "mismatches": []}, "results": [],
        }
    payload.setdefault("company", "Portfolio review")
    payload.setdefault("period", "Unavailable")
    payload.setdefault("synthetic", False)
    payload.setdefault("results", [])
    validation = payload.setdefault("validation", {})
    validation.setdefault("status", "FAIL" if errors else "PASS")
    validation.setdefault("errors", errors)
    validation.setdefault("warnings", [])
    reconciliation = payload.setdefault("reconciliation", {})
    reconciliation.setdefault("status", "NOT_RUN" if errors else "PASS")
    reconciliation.setdefault("mismatches", [])
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    payload, load_errors = load(args.results_json)
    errors, _ = (load_errors, []) if load_errors else validate(payload)
    state = presentation_state(payload, errors)
    payload = normalize(payload, errors)

    document = render(payload, state)
    needle = "else{shareError.textContent='This action must run from an interactive Codex chat dashboard.';shareError.hidden=false;shareSubmit.disabled=false;shareCancel.disabled=false}})}"
    if needle not in document:
        parser.error("dashboard renderer does not contain the expected Claude fallback")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document.replace(needle, FALLBACK), encoding="utf-8")
    print(output.resolve())
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
