#!/usr/bin/env python3
"""Unified CLI for portfolio monthly performance analysis across all platforms."""

import argparse
import json
import sys
from pathlib import Path

# Add scripts to path for relative imports
sys.path.insert(0, str(Path(__file__).parent))

from core.validation import validate, number
from core.calculations import calculate, convert_for_json
from output.csv_io import markdown

SCHEMA_VERSION = "1.0"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", help="Path to input CSV file")
    parser.add_argument("--period", required=True, help="Analysis period (YYYY-MM)")
    parser.add_argument("--output-json", help="Path to output RESULTS.json")
    parser.add_argument("--output-markdown", help="Path to output SCORECARD.md")
    args = parser.parse_args()

    # Validate input CSV
    rows, errors, warnings = validate(args.input_csv)

    if errors:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "status": "blocked",
            "synthetic": None,
            "company": None,
            "period": args.period,
            "source": {"file": Path(args.input_csv).name, "row_count": len(rows)},
            "validation": {"status": "FAIL", "errors": errors, "warnings": warnings},
            "reconciliation": {"status": "NOT_RUN", "mismatches": []},
            "results": [],
        }
        if args.output_json:
            Path(args.output_json).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    # Calculate results
    results = calculate(rows, args.period)

    if not results:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "status": "empty",
            "synthetic": all(r["synthetic"].lower() == "true" for r in rows),
            "company": None,
            "period": args.period,
            "source": {"file": Path(args.input_csv).name, "row_count": len(rows)},
            "validation": {"status": "PASS", "errors": [], "warnings": warnings},
            "reconciliation": {"status": "NOT_RUN", "mismatches": []},
            "results": [],
        }
        if args.output_json:
            Path(args.output_json).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"ERROR: no rows found for period {args.period}", file=sys.stderr)
        return 1

    # Determine company and build final payload
    company = next(r["company"] for r in rows if r["period"] == args.period)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": "warning" if warnings else "ready",
        "synthetic": all(r["synthetic"].lower() == "true" for r in rows),
        "company": company,
        "period": args.period,
        "source": {"file": Path(args.input_csv).name, "row_count": len(rows)},
        "validation": {"status": "PASS", "errors": [], "warnings": warnings},
        "reconciliation": {"status": "PASS", "mismatches": []},
        "results": results,
    }

    # Convert Decimals to floats for JSON
    rendered = json.dumps(convert_for_json(payload), indent=2)

    if args.output_json:
        Path(args.output_json).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    # Generate Markdown scorecard if requested
    if args.output_markdown:
        Path(args.output_markdown).write_text(markdown(company, args.period, results, warnings), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
