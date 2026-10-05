#!/usr/bin/env python3
"""Run portfolio analysis + dashboard orchestration (Analysis → Validation → Dashboard)."""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ANALYSIS_SKILL = ROOT / "portfolio-monthly-performance-analysis"
DASHBOARD_SKILL = ROOT / "portfolio-performance-dashboard"


def run_command(command, description):
    """Run a command and report status."""
    print(f"\n[1/3] {description}...")
    result = subprocess.run(command, text=True, capture_output=False)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(ANALYSIS_SKILL / "assets" / "synthetic_monthly_data.csv"),
                        help="Input CSV file")
    parser.add_argument("--period", default="2026-08", help="Analysis period (YYYY-MM)")
    parser.add_argument("--output-dir", default=str(ROOT / "analysis-results"),
                        help="Output directory for results")
    parser.add_argument("--destination", choices=("browser", "inline"), default="inline",
                        help="Output destination: browser (HTML) or inline (Codex chat)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    results_json = output_dir / "RESULTS.json"
    scorecard_md = output_dir / "SCORECARD.md"
    dashboard_html = output_dir / "dashboard.html"

    # Step 1: Run Analysis
    analysis_cmd = [
        sys.executable,
        str(ANALYSIS_SKILL / "scripts" / "run.py"),
        str(Path(args.input).resolve()),
        "--period", args.period,
        "--output-json", str(results_json),
        "--output-markdown", str(scorecard_md),
    ]

    if not run_command(analysis_cmd, "Running portfolio analysis"):
        print("[FAILED] Analysis failed - dashboard skipped", file=sys.stderr)
        return 1

    if not results_json.exists():
        print(f"[FAILED] RESULTS.json not found at {results_json}", file=sys.stderr)
        return 1

    # Step 2: Validate Dashboard Input
    validate_cmd = [
        sys.executable,
        str(DASHBOARD_SKILL / "scripts" / "validate_dashboard_input.py"),
        str(results_json),
    ]

    if not run_command(validate_cmd, "Validating dashboard input"):
        print("[WARNING] Dashboard validation issue (analysis succeeded)", file=sys.stderr)

    # Step 3: Render Dashboard
    render_cmd = [
        sys.executable,
        str(DASHBOARD_SKILL / "scripts" / "render_dashboard.py"),
        str(results_json),
        "--output", str(dashboard_html),
    ]

    if not run_command(render_cmd, "Rendering interactive dashboard"):
        print("[WARNING] Dashboard rendering issue (analysis succeeded)", file=sys.stderr)

    # Report Results
    print("\n" + "="*60)
    print("ANALYSIS + DASHBOARD COMPLETE")
    print("="*60)
    print(f"\nGenerated files:")
    print(f"  Results:   {results_json}")
    if scorecard_md.exists():
        print(f"  Scorecard: {scorecard_md}")
    if dashboard_html.exists():
        print(f"  Dashboard: {dashboard_html}")

    if args.destination == "browser":
        print(f"\nServe locally with:")
        print(f"  python3 -m http.server 8765 --directory {output_dir}")
        print(f"  Then open: http://127.0.0.1:8765/dashboard.html")
    else:
        print(f"\nFor inline Codex chat rendering:")
        print(f"  Copy the dashboard HTML from {dashboard_html}")
        print(f"  Paste into Codex chat for interactive visualization")

    return 0


if __name__ == "__main__":
    sys.exit(main())
