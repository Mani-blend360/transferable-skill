"""Unit tests for core calculation logic."""

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from core.calculations import variance, materiality, favorability, evidence, calculate
from core.validation import number


def test_variance_absolute():
    """Test absolute variance calculation."""
    actual = Decimal("100")
    comparison = Decimal("90")
    result = variance(actual, comparison, percent_kpi=False)
    assert result["absolute_variance"] == Decimal("10")
    assert result["percentage_variance"] == Decimal("100") / Decimal("9")


def test_variance_zero_comparison():
    """Test that division by zero produces not_meaningful."""
    actual = Decimal("100")
    comparison = Decimal("0")
    result = variance(actual, comparison, percent_kpi=False)
    assert result["percentage_variance"] == "not_meaningful"


def test_variance_percentage_kpi():
    """Test percentage KPI variance calculation."""
    actual = Decimal("50")
    comparison = Decimal("40")
    result = variance(actual, comparison, percent_kpi=True)
    assert result["percentage_point_difference"] == Decimal("10")
    assert result["basis_point_difference"] == Decimal("1000")


def test_variance_none_comparison():
    """Test that None comparison returns None."""
    actual = Decimal("100")
    result = variance(actual, None, percent_kpi=False)
    assert result is None


def test_materiality_absolute():
    """Test absolute materiality assessment."""
    result = {"absolute_variance": Decimal("5")}
    assert materiality(result, "absolute", Decimal("10")) == "non_material"
    assert materiality(result, "absolute", Decimal("5")) == "material"  # equality is material
    assert materiality(result, "absolute", Decimal("4")) == "material"


def test_materiality_percentage():
    """Test percentage materiality assessment."""
    result = {"percentage_variance": Decimal("10")}
    assert materiality(result, "percent", Decimal("5")) == "material"
    assert materiality(result, "percent", Decimal("10")) == "material"
    assert materiality(result, "percent", Decimal("15")) == "non_material"


def test_materiality_bps():
    """Test basis-point materiality assessment."""
    result = {"basis_point_difference": Decimal("500")}
    assert materiality(result, "bps", Decimal("100")) == "material"
    assert materiality(result, "bps", Decimal("500")) == "material"
    assert materiality(result, "bps", Decimal("600")) == "non_material"


def test_materiality_not_meaningful():
    """Test not_meaningful percentage returns not_assessable."""
    result = {"percentage_variance": "not_meaningful", "basis_point_difference": None}
    assert materiality(result, "percent", Decimal("5")) == "not_assessable"


def test_materiality_none():
    """Test that None result returns not_assessable."""
    assert materiality(None, "absolute", Decimal("5")) == "not_assessable"


def test_favorability_higher_is_favorable():
    """Test favorability for higher_is_favorable direction."""
    result_positive = {"absolute_variance": Decimal("10")}
    assert favorability(result_positive, "higher_is_favorable") == "favorable"

    result_negative = {"absolute_variance": Decimal("-10")}
    assert favorability(result_negative, "higher_is_favorable") == "unfavorable"

    result_zero = {"absolute_variance": Decimal("0")}
    assert favorability(result_zero, "higher_is_favorable") == "neutral"


def test_favorability_lower_is_favorable():
    """Test favorability for lower_is_favorable direction."""
    result_positive = {"absolute_variance": Decimal("10")}
    assert favorability(result_positive, "lower_is_favorable") == "unfavorable"

    result_negative = {"absolute_variance": Decimal("-10")}
    assert favorability(result_negative, "lower_is_favorable") == "favorable"


def test_favorability_neutral():
    """Test favorability for neutral direction."""
    result_positive = {"absolute_variance": Decimal("10")}
    assert favorability(result_positive, "neutral") == "neutral"


def test_favorability_none():
    """Test that None result returns not_assessable."""
    assert favorability(None, "higher_is_favorable") == "not_assessable"


def test_evidence_calculated_fact():
    """Test evidence classification: calculated_fact (no driver, non-material)."""
    row = {"management_driver": "", "evidence_source": ""}
    result = evidence(row, None, "non_material")
    assert result == "calculated_fact"


def test_evidence_missing_evidence_material():
    """Test evidence classification: missing_evidence (material but no driver)."""
    row = {"management_driver": "", "evidence_source": ""}
    result = evidence(row, None, "material")
    assert result == "missing_evidence"


def test_evidence_missing_evidence_no_source():
    """Test evidence classification: missing_evidence (driver but no source)."""
    row = {"management_driver": "Revenue declined", "evidence_source": ""}
    result = evidence(row, None, "non_material")
    assert result == "missing_evidence"


def test_evidence_source_supported():
    """Test evidence classification: source_supported (consistent direction)."""
    row = {"management_driver": "Revenue increased due to market expansion", "evidence_source": "Sales report"}
    budget_result = {"absolute_variance": Decimal("10")}  # positive variance
    result = evidence(row, budget_result, "non_material")
    assert result == "source_supported"


def test_evidence_contradictory_evidence_up_down():
    """Test evidence classification: contradictory_evidence (driver up, variance down)."""
    row = {"management_driver": "Revenue increased sharply", "evidence_source": "Sales report"}
    budget_result = {"absolute_variance": Decimal("-10")}  # negative variance
    result = evidence(row, budget_result, "material")
    assert result == "contradictory_evidence"


def test_evidence_contradictory_evidence_down_up():
    """Test evidence classification: contradictory_evidence (driver down, variance up)."""
    row = {"management_driver": "Costs declined due to efficiency", "evidence_source": "Operations"}
    budget_result = {"absolute_variance": Decimal("10")}  # positive variance
    result = evidence(row, budget_result, "material")
    assert result == "contradictory_evidence"


def test_number_parsing():
    """Test number parsing with Decimal."""
    assert number("100.5") == Decimal("100.5")
    assert number("") is None
    assert number(None) is None
    assert number("  -50.25  ") == Decimal("-50.25")


def test_calculate_basic():
    """Test basic calculation workflow."""
    rows = [
        {
            "company": "TestCo",
            "synthetic": "true",
            "period": "2026-01",
            "kpi": "Revenue",
            "kpi_type": "financial",
            "actual": "100",
            "budget": "90",
            "prior_month": "95",
            "prior_year": "80",
            "current_forecast": "110",
            "original_investment_case": "85",
            "current_full_year_forecast": "1200",
            "original_investment_case_full_year": "1000",
            "currency": "USD",
            "unit": "USDm",
            "favorable_direction": "higher_is_favorable",
            "materiality_type": "percent",
            "materiality_threshold": "5",
            "management_driver": "Market expansion",
            "evidence_source": "Sales report",
            "management_action": "",
            "action_owner": "",
            "expected_completion_date": "",
        }
    ]
    results = calculate(rows, "2026-01")
    assert len(results) == 1
    item = results[0]
    assert item["kpi"] == "Revenue"
    assert item["actual"] == Decimal("100")
    assert item["comparisons"]["budget"]["absolute_variance"] == Decimal("10")
    assert item["comparisons"]["budget"]["materiality"] == "material"
    assert item["comparisons"]["budget"]["favorability"] == "favorable"
    assert item["evidence_class"] == "source_supported"
    assert item["full_year_forecast_revision"]["absolute_variance"] == Decimal("200")


def test_calculate_empty_period():
    """Test calculate with no rows for period."""
    rows = [{"period": "2026-01"}]
    results = calculate(rows, "2026-02")
    assert results == []


if __name__ == "__main__":
    test_variance_absolute()
    test_variance_zero_comparison()
    test_variance_percentage_kpi()
    test_variance_none_comparison()
    test_materiality_absolute()
    test_materiality_percentage()
    test_materiality_bps()
    test_materiality_not_meaningful()
    test_materiality_none()
    test_favorability_higher_is_favorable()
    test_favorability_lower_is_favorable()
    test_favorability_neutral()
    test_favorability_none()
    test_evidence_calculated_fact()
    test_evidence_missing_evidence_material()
    test_evidence_missing_evidence_no_source()
    test_evidence_source_supported()
    test_evidence_contradictory_evidence_up_down()
    test_evidence_contradictory_evidence_down_up()
    test_number_parsing()
    test_calculate_basic()
    test_calculate_empty_period()
    print("All tests passed!")
