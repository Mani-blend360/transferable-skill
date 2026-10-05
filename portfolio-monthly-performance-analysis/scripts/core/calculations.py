"""Core calculation logic for portfolio performance analysis."""

from decimal import Decimal
from .validation import number

BASELINES = ["budget", "prior_month", "prior_year", "current_forecast", "original_investment_case"]


def variance(actual, comparison, percent_kpi):
    """Calculate absolute and percentage variance."""
    if comparison is None:
        return None
    absolute = actual - comparison
    percentage = "not_meaningful" if comparison == 0 else absolute / abs(comparison) * Decimal("100")
    result = {"comparison": comparison, "absolute_variance": absolute, "percentage_variance": percentage}
    if percent_kpi:
        result["percentage_point_difference"] = absolute
        result["basis_point_difference"] = absolute * Decimal("100")
    return result


def materiality(result, kind, threshold):
    """Assess materiality of a variance."""
    if result is None:
        return "not_assessable"
    if kind == "absolute":
        measure = abs(result["absolute_variance"])
    elif kind == "bps":
        measure = abs(result["basis_point_difference"])
    else:
        if result["percentage_variance"] == "not_meaningful":
            return "not_assessable"
        measure = abs(result["percentage_variance"])
    return "material" if measure >= threshold else "non_material"


def favorability(result, direction):
    """Assess favorability of a variance."""
    if result is None:
        return "not_assessable"
    delta = result["absolute_variance"]
    if delta == 0 or direction == "neutral":
        return "neutral"
    favorable = delta > 0 if direction == "higher_is_favorable" else delta < 0
    return "favorable" if favorable else "unfavorable"


def evidence(row, budget_result, budget_materiality):
    """Classify evidence quality for a KPI."""
    driver, source = row["management_driver"].strip(), row["evidence_source"].strip()
    if not driver:
        return "missing_evidence" if budget_materiality == "material" else "calculated_fact"
    if not source:
        return "missing_evidence"
    delta = budget_result["absolute_variance"] if budget_result else Decimal("0")
    lowered = driver.lower()
    up = any(word in lowered for word in ("increase", "increased", "higher", "above", "grew", "growth"))
    down = any(word in lowered for word in ("decrease", "decreased", "lower", "below", "fell", "decline"))
    if (delta < 0 and up) or (delta > 0 and down):
        return "contradictory_evidence"
    return "source_supported"


def calculate(rows, period):
    """Calculate all metrics for a given period."""
    selected = [r for r in rows if r["period"] == period]
    output = []
    for row in selected:
        actual = number(row["actual"])
        percent_kpi = row["unit"] == "%"
        comparisons = {name: variance(actual, number(row[name]), percent_kpi) for name in BASELINES}
        threshold = number(row["materiality_threshold"])
        for name, result in comparisons.items():
            if result is not None:
                result["materiality"] = materiality(result, row["materiality_type"], threshold)
                result["favorability"] = favorability(result, row["favorable_direction"])
        budget = comparisons["budget"]
        budget_mat = budget["materiality"] if budget else "not_assessable"
        fy_actual, fy_case = number(row["current_full_year_forecast"]), number(row["original_investment_case_full_year"])
        fy_revision = variance(fy_actual, fy_case, percent_kpi) if fy_actual is not None and fy_case is not None else None
        item = {
            "kpi": row["kpi"], "kpi_type": row["kpi_type"], "actual": actual,
            "currency": row["currency"], "unit": row["unit"], "direction": row["favorable_direction"],
            "materiality_type": row["materiality_type"], "materiality_threshold": threshold,
            "comparisons": comparisons, "full_year_forecast_revision": fy_revision,
            "evidence_class": evidence(row, budget, budget_mat), "management_driver": row["management_driver"],
            "evidence_source": row["evidence_source"], "management_action": row["management_action"],
            "action_owner": row["action_owner"], "expected_completion_date": row["expected_completion_date"],
        }
        output.append(item)
    return output


def convert_for_json(obj):
    """Convert Decimals to floats for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_for_json(v) for v in obj]
    return obj
