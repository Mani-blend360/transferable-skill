"""CSV and Markdown I/O for portfolio performance analysis."""

from decimal import Decimal


def display(value, unit):
    """Format a value for display."""
    if value is None:
        return "n/a"
    suffix = "%" if unit == "%" else ""
    return f"{float(value):.1f}{suffix}"


def markdown(company, period, results, warnings):
    """Generate a Markdown scorecard."""
    lines = [f"# Synthetic monthly scorecard — {company} — {period}", "", "| KPI | Actual | Budget | Variance | Prior month | Materiality | Favorability |", "|---|---:|---:|---:|---:|---|---|"]
    for item in results:
        budget = item["comparisons"]["budget"]
        prior = item["comparisons"]["prior_month"]
        if budget is None:
            bval, variance_text, mat, fav = "n/a", "n/a", "not_assessable", "not_assessable"
        else:
            bval = display(budget["comparison"], item["unit"])
            if item["unit"] == "%":
                variance_text = f"{float(budget['percentage_point_difference']):+.1f}pp / {float(budget['basis_point_difference']):+.0f}bps"
            else:
                pct = budget["percentage_variance"]
                pct_text = "not meaningful" if pct == "not_meaningful" else f"{float(pct):+.1f}%"
                variance_text = f"{float(budget['absolute_variance']):+.1f} ({pct_text})"
            mat, fav = budget["materiality"], budget["favorability"]
        prior_text = "n/a" if prior is None else f"{display(prior['comparison'], item['unit'])}; Δ {float(prior['absolute_variance']):+.1f}"
        lines.append(f"| {item['kpi']} | {display(item['actual'], item['unit'])} | {bval} | {variance_text} | {prior_text} | {mat} | {fav} |")
    lines.extend(["", "## Data-quality warnings", ""])
    lines.extend([f"- {warning}" for warning in warnings] or ["- None."])
    return "\n".join(lines) + "\n"
