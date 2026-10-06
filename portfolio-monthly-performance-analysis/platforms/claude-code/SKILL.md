---
name: portfolio-monthly-performance-analysis
description: Analyze monthly portfolio-company performance data from a CSV file, calculate variance against five baselines, assess materiality and favorability, classify evidence, and produce reconciled results in JSON and Markdown. Use for local monthly reviews; do not use for investment recommendations or live-system integrations.
---

# Portfolio Monthly Performance Analysis

Analyze performance metrics against multiple baselines, reconcile results with business context, and produce management-ready output.

## What This Skill Does

1. **Validates** the input CSV against a strict schema with structural, enum, numeric, and cross-field checks
2. **Calculates** variance analysis (absolute and percentage) across five baselines:
   - Budget
   - Prior month
   - Prior year
   - Current forecast
   - Original investment case
3. **Assesses materiality** using per-row thresholds (absolute USD amount, percentage magnitude, or basis-point difference)
4. **Assesses favorability** mechanically: whether a variance is favorable or unfavorable given the KPI direction
5. **Classifies evidence** for each KPI:
   - `calculated_fact`: a purely mechanical result (no management driver provided)
   - `source_supported`: a driver and evidence source are provided and direction is not contradicted
   - `missing_evidence`: a material movement has no driver or no evidence source
   - `contradictory_evidence`: the driver direction contradicts the numerical variance direction
6. **Produces output** as reconciled JSON and optional Markdown scorecard

## How to Use

### Input: CSV File

Prepare a long-form UTF-8 CSV with one row per company/period/KPI. Required columns are:
- `company`: company name (all rows must be single company)
- `synthetic`: `true` or `false`
- `period`: `YYYY-MM`
- `kpi`: KPI name (unique per company/period)
- `kpi_type`: `financial` or `operational`
- `actual`: required, numeric
- `budget`, `prior_month`, `prior_year`, `current_forecast`, `original_investment_case`: numeric or blank
- `current_full_year_forecast`, `original_investment_case_full_year`: numeric or blank (for full-year revision)
- `currency`: required for monetary KPIs; blank for operational KPIs
- `unit`: `USDm`, `USD`, `%`, or other; percentage KPIs use `bps` materiality only
- `favorable_direction`: `higher_is_favorable`, `lower_is_favorable`, or `neutral`
- `materiality_type`: `absolute`, `percent`, or `bps` (use `bps` for % KPIs)
- `materiality_threshold`: numeric, ≥ 0
- `management_driver`: explanation of why actual differs from budget (optional; must pair with evidence_source)
- `evidence_source`: how the driver is substantiated (optional; required if management_driver is present)
- `management_action`: corrective or strategic action (optional; must pair with action_owner and expected_completion_date)
- `action_owner`: who owns the action (optional; required if management_action is present)
- `expected_completion_date`: `YYYY-MM-DD` (optional; required if management_action is present)

See [references/input-schema.md](references/input-schema.md) for detailed field definitions.

### Running the Analysis

Use the `run.py` script with these arguments:

```
python3 scripts/run.py <input.csv> --period YYYY-MM [--output-json RESULTS.json] [--output-markdown SCORECARD.md]
```

- `input.csv`: path to your CSV file (required)
- `--period YYYY-MM`: analysis period (required)
- `--output-json`: path to write reconciled results JSON (optional; default: stdout)
- `--output-markdown`: path to write Markdown scorecard table (optional)

### Output: RESULTS.json

A single JSON file containing:

- **Validation status** and any errors or warnings
- **Reconciliation status** (always PASS for ready/warning states; NOT_RUN for blocked/empty)
- **Results array** with one object per KPI, containing:
  - All input fields
  - Variance calculations for each baseline
  - Materiality and favorability assessment for each variance
  - Evidence classification
  - Full-year forecast revision (if applicable)

Schema version is `1.0`. Top-level status is one of:
- `ready`: validation and calculation succeeded; all material movements are reconciled
- `warning`: validation and calculation succeeded; warnings are present (see validation.warnings)
- `blocked`: validation failed; results array is empty; no analysis was performed
- `empty`: validation passed but no rows matched the requested period; results array is empty

See [references/results-contract.md](references/results-contract.md) for the full contract.

### Output: SCORECARD.md

An optional Markdown table with KPIs, actual, budget, variance, prior-month comparison, materiality, and favorability. Useful for quick review and embedding in reports.

## Agent Presentation Layer (After Files Are Generated)

After `run.py` produces RESULTS.json and SCORECARD.md, inspect `status` and `reconciliation.status` before presenting results:

- When `status` is `ready` or `warning` and `reconciliation.status` is `PASS`, immediately invoke `$portfolio-performance-dashboard` with the absolute path to `RESULTS.json`. Render and display the Claude artifact before any written analysis, executive summary, scorecard, or follow-up question. Do not ask whether the user wants a dashboard.
- When `status` is `blocked`, `empty`, or reconciliation did not pass, do not invoke the dashboard. Explain the validation or reconciliation state and the corrective next step instead.
- The dashboard handoff renders results only; it must not publish or share them without the user's explicit confirmation.

After the dashboard artifact is displayed, **the agent interprets and presents findings** to the user with business context:

1. **Read RESULTS.json** — Extract status, validation warnings, reconciliation state, and all KPI results
2. **Filter material movements** — Focus on KPIs where `materiality: material` in budget comparison
3. **Assess evidence quality** — Note any `missing_evidence` or `contradictory_evidence` flags
4. **Apply business context** — Interpret favorable/unfavorable in light of company strategy and market conditions
5. **Draft findings** — For each material movement:
   - State the fact (actual vs budget, direction, magnitude)
   - Reference the evidence class (supported / missing / contradictory)
   - Link to management driver if provided
   - Highlight any data conflicts or management clarification needed
6. **Write executive summary** — 2-4 sentences summarizing key movements and themes
7. **Highlight actions** — List any management actions with owner and completion date
8. **Present the scorecard** — Show SCORECARD.md table for quick reference
9. **Surface warnings** — Report validation.warnings and reconciliation mismatches clearly
10. **Ask clarifying questions** — If evidence is missing or contradictory, ask for management input

**Key constraint:** Presentation adds business judgment and context, but does NOT modify the calculated numbers. All presented figures are traceable back to RESULTS.json.

See [references/commentary-guidelines.md](references/commentary-guidelines.md) for presentation style and materiality interpretation.

## Business Rules and Hard Boundaries

Read these before interpreting results:

- **Percentage variance against zero is `not_meaningful`**: never divide by zero. Comparisons of zero produce `not_assessable` materiality.
- **Percentage KPIs use basis-point difference for materiality**: use `materiality_type: bps` for all `%` units.
- **Equality with threshold is material**: materiality ≥ threshold, not > threshold.
- **A missing driver for a material movement must say**: "Driver not provided; management input required."
- **If commentary conflicts with data, identify the contradiction and ask for clarification**: do not present hypotheses as facts.
- **Do not**: modify source financials, invent drivers, recommend an investment, send results to external systems, or distribute the report.
- **Single company only**: input must contain exactly one company; multi-company input is an error.

See [references/materiality-rules.md](references/materiality-rules.md), [references/evidence-rules.md](references/evidence-rules.md), and [references/calculation-rules.md](references/calculation-rules.md) for detailed rules.

## Example

Use the synthetic data to test the skill:

```bash
python3 scripts/run.py assets/synthetic_monthly_data.csv --period 2026-03 \
  --output-json synthetic-results.json \
  --output-markdown synthetic-scorecard.md
```

See [assets/synthetic_company_profile.md](assets/synthetic_company_profile.md) for company context.

## When to Use This Skill

- You have a CSV file of monthly performance data with actuals and baselines.
- You want variance analysis and materiality assessment without manual spreadsheet work.
- You need a reconciled, machine-readable results file for downstream tools or dashboards.
- You are performing a formal monthly review and need to document evidence and actions.

## When NOT to Use This Skill

- You are making investment recommendations or trading decisions; this skill produces analysis only, not advice.
- You need to connect to live financial systems or databases; this skill works with local CSV files.
- You need real-time dashboards; this skill produces static JSON and Markdown.
- Your data is not structured as a long-form CSV; prepare it first.

## Platform Support

This skill runs on:
- **Claude Code** (Claude agent via the terminal)
- **OpenAI Codex** (Codex agent; legacy support)
- **Snowflake Cortex Code** (Cortex Code agent)

Each platform loads the skill from a folder containing this `SKILL.md` and the `scripts/` directory. See the platform-specific `README.md` section below for install instructions.

## Testing

Run the test suite to verify correctness:

```bash
python3 tests/test_core.py              # Unit tests (core calculations)
python3 tests/test_smoke_csv.py         # Integration tests (with synthetic CSV)
```

All tests should pass. If running on a new platform, run `test_smoke_csv.py` to confirm end-to-end functionality.

---

## Install Instructions by Platform

### Claude Code (Claude + VS Code / JetBrains / CLI)

1. Clone or copy the skill folder to your local Claude Code skills directory:
   - **Local project**: `.claude/skills/portfolio-monthly-performance-analysis/`
   - **Global**: `~/.claude/skills/portfolio-monthly-performance-analysis/`

2. Verify Python 3.7+ is available: `python3 --version`

3. Test the skill:
   ```bash
   cd portfolio-monthly-performance-analysis
   python3 scripts/run.py assets/synthetic_monthly_data.csv --period 2026-03 --output-json test.json
   cat test.json
   ```

4. In Claude Code, invoke the skill naturally:
   ```
   Analyze the monthly portfolio performance from this CSV file.
   ```
   Claude will discover and use the skill.

### OpenAI Codex (Legacy)

1. Check your Codex skills directory (e.g., `~/.codex-skills/` or project-local `.codex/skills/`; consult Codex docs for current path).

2. Copy the skill folder there:
   ```bash
   cp -r portfolio-monthly-performance-analysis ~/.codex-skills/
   ```

3. Verify via Codex's skill listing command.

4. Invoke with the skill name and provide a CSV file path.

### Snowflake Cortex Code (CoCo)

1. Check Cortex Code's skill directory (e.g., `~/.snowflake/cortex/skills/` or `.cortex/skills/`; consult Cortex docs for current path).

2. Copy the skill folder:
   ```bash
   cp -r portfolio-monthly-performance-analysis ~/.snowflake/cortex/skills/
   ```

3. Or use the Cortex CLI to register:
   ```bash
   cortex skill add portfolio-monthly-performance-analysis
   ```

4. Invoke with `$portfolio-monthly-performance-analysis` or natural language. Cortex will pass data to the skill's `run.py` entry point.

5. Results are returned as JSON and displayed inline.

---

## Reference Material

- [references/input-schema.md](references/input-schema.md) — CSV columns, enums, validation rules
- [references/calculation-rules.md](references/calculation-rules.md) — variance, percentage, basis-point formulas
- [references/materiality-rules.md](references/materiality-rules.md) — materiality assessment and favorability
- [references/evidence-rules.md](references/evidence-rules.md) — evidence classification framework
- [references/results-contract.md](references/results-contract.md) — RESULTS.json schema and presentation gates
- [config.yaml](config.yaml) — evidence keywords and materiality patterns

## Maintenance and Feedback

For issues, suggestions, or contributions, contact the skill maintainer. Behavioral tests are in `evals/` (if present). For CI/CD integration, ensure Python 3.7+, then run `test_core.py` and `test_smoke_csv.py`.
