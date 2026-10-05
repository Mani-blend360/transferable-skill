"""Integration test: validate and calculate using synthetic CSV data."""

import json
import sys
import tempfile
from pathlib import Path

scripts_path = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_path))

from core.validation import validate
from core.calculations import calculate, convert_for_json

# Import csv_io from output package
import importlib.util
spec = importlib.util.spec_from_file_location("csv_io_module", scripts_path / "output" / "csv_io.py")
csv_io_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(csv_io_module)
markdown = csv_io_module.markdown


def test_synthetic_csv_validation_and_calculation():
    """Test end-to-end workflow with synthetic CSV."""
    csv_path = Path(__file__).parent.parent / "assets" / "synthetic_monthly_data.csv"

    if not csv_path.exists():
        print(f"SKIP: {csv_path} not found")
        return

    # Validate
    rows, errors, warnings = validate(csv_path)
    assert not errors, f"Validation errors: {errors}"
    assert len(rows) > 0, "No rows read"

    # Calculate
    results = calculate(rows, "2026-03")
    assert len(results) > 0, f"No results for period 2026-03"

    # Check structure of first result
    item = results[0]
    assert "kpi" in item
    assert "actual" in item
    assert "comparisons" in item
    assert "budget" in item["comparisons"]

    # Generate Markdown
    company = next(r["company"] for r in rows if r["period"] == "2026-03")
    md = markdown(company, "2026-03", results, warnings)
    assert "KPI" in md
    assert "Actual" in md
    assert "Budget" in md

    # Verify JSON serialization
    converted = convert_for_json(results)
    json_str = json.dumps(converted, indent=2)
    assert len(json_str) > 100

    print(f"✓ Synthetic CSV test passed: {len(results)} KPIs analyzed, {len(warnings)} warnings")


def test_run_py_integration():
    """Test run.py CLI with synthetic CSV."""
    csv_path = Path(__file__).parent.parent / "assets" / "synthetic_monthly_data.csv"

    if not csv_path.exists():
        print(f"SKIP: {csv_path} not found")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        output_json = Path(tmpdir) / "results.json"
        output_md = Path(tmpdir) / "scorecard.md"

        # Import and run run.py's main
        sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
        from run import main as run_main

        # Mock sys.argv
        old_argv = sys.argv
        try:
            sys.argv = ["run.py", str(csv_path), "--period", "2026-03",
                        "--output-json", str(output_json),
                        "--output-markdown", str(output_md)]
            exit_code = run_main()

            assert exit_code == 0 or exit_code is None, f"Expected exit code 0, got {exit_code}"
            assert output_json.exists(), f"JSON not created at {output_json}"
            assert output_md.exists(), f"Markdown not created at {output_md}"

            # Verify JSON structure
            payload = json.loads(output_json.read_text())
            assert payload["schema_version"] == "1.0"
            assert payload["status"] in ["ready", "warning"]
            assert payload["company"] == "Northstar Components"
            assert payload["period"] == "2026-03"
            assert len(payload["results"]) > 0

            print(f"✓ run.py integration test passed: {len(payload['results'])} results, status={payload['status']}")
        finally:
            sys.argv = old_argv


if __name__ == "__main__":
    test_synthetic_csv_validation_and_calculation()
    test_run_py_integration()
    print("\nAll integration tests passed!")
