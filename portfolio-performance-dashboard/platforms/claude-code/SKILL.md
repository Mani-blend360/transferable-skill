---
name: portfolio-performance-dashboard
description: Present reconciled monthly portfolio-company results as an interactive dashboard and optional read-only share artifact. Use after portfolio performance analysis has produced RESULTS.json; do not calculate from raw CSVs or render unverified results.
---

# Portfolio Performance Dashboard

Render the exact reconciled `RESULTS.json` supplied by the analysis workflow. The Python renderer and exported HTML are platform-neutral; the current chat host is responsible for displaying the artifact and for any follow-up actions.

## Workflow

1. Use the supplied results path exactly. Run `python3 scripts/validate_dashboard_input.py /absolute/path/to/RESULTS.json --json`. Do not render normal KPI values if validation or reconciliation does not pass.
2. Read [dashboard-input-schema.md](references/dashboard-input-schema.md) and [ui-states.md](references/ui-states.md). Render the returned state: `ready`, `warning`, `blocked`, `empty`, or `reconciliation_failed`.
3. For `ready` and `warning`, generate the Claude artifact: `python3 scripts/render_claude_dashboard.py RESULTS.json --output dashboard.html`. Display or open `dashboard.html` through Claude Code's artifact workflow before any written analysis of the results. Claude Code renders dashboards as artifacts, not as a Codex-style in-chat widget.
4. The artifact's **Share on Blend** button collects a lowercase path slug and, after **Confirm and publish**, copies a complete publication prompt. Tell the user to paste and send that prompt in Claude chat. Then follow [blend-publishing.md](references/blend-publishing.md) and [host-adapters.md](references/host-adapters.md): render the read-only export, validate its request with `scripts/publish_request.py`, and call the configured Blend path-check followed by upload.

## Boundaries

- Consume reconciled JSON, never raw CSV.
- Display `null`, unavailable, and `not_meaningful` distinctly; never coerce them to zero.
- Preserve percentage, percentage-point, basis-point, currency, and unit semantics.
- Label synthetic data clearly and retain evidence tags with commentary.
- Do not assume an MCP server, a browser bridge, or write permission exists. If the host cannot publish through Blend MCP, report that limitation after rendering the dashboard.
