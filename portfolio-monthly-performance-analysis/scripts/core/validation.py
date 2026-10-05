"""CSV validation for portfolio performance analysis."""

import csv
import re
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

REQUIRED = [
    "company", "synthetic", "period", "kpi", "kpi_type", "actual", "budget",
    "prior_month", "prior_year", "current_forecast", "original_investment_case",
    "current_full_year_forecast", "original_investment_case_full_year", "currency",
    "unit", "favorable_direction", "materiality_type", "materiality_threshold",
    "management_driver", "evidence_source", "management_action", "action_owner",
    "expected_completion_date",
]
NUMERIC = {
    "actual", "budget", "prior_month", "prior_year", "current_forecast",
    "original_investment_case", "current_full_year_forecast",
    "original_investment_case_full_year", "materiality_threshold",
}
DIRECTIONS = {"higher_is_favorable", "lower_is_favorable", "neutral"}
MATERIALITY = {"percent", "absolute", "bps"}
KPI_TYPES = {"financial", "operational"}
MONETARY_UNITS = {"USDm", "USD"}
UP_WORDS = re.compile(r"\b(increase[ds]?|rose|higher|above|grew|growth)\b", re.I)
DOWN_WORDS = re.compile(r"\b(decrease[ds]?|fell|lower|below|decline[ds]?)\b", re.I)


def number(value):
    """Parse a numeric field, return Decimal or None."""
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    parsed = Decimal(str(value).strip())
    if not parsed.is_finite():
        raise InvalidOperation
    return parsed


def validate(path):
    """Validate CSV and return (rows, errors, warnings)."""
    errors, warnings = [], []
    try:
        with Path(path).open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            duplicates = sorted({name for name in fieldnames if fieldnames.count(name) > 1})
            if duplicates:
                return [], [f"duplicate columns: {', '.join(duplicates)}"], []
            missing = [c for c in REQUIRED if c not in fieldnames]
            if missing:
                return [], [f"missing required columns: {', '.join(missing)}"], []
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        return [], [f"cannot read CSV: {exc}"], []

    if not rows:
        return [], ["CSV contains headers but no data rows"], []

    seen = set()
    by_kpi = defaultdict(list)
    for line, row in enumerate(rows, 2):
        label = f"row {line}"
        if None in row:
            errors.append(f"{label}: contains more values than header columns")
            row.pop(None, None)
        for field in REQUIRED:
            if row.get(field) is None:
                row[field] = ""
            else:
                row[field] = row[field].strip()
        key = (row["company"], row["period"], row["kpi"])
        if key in seen:
            errors.append(f"{label}: duplicate company/period/KPI key {key}")
        seen.add(key)
        if not row["company"] or not row["kpi"]:
            errors.append(f"{label}: company and kpi are required")
        if row["synthetic"].lower() not in {"true", "false"}:
            errors.append(f"{label}: synthetic must be true or false")
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", row["period"]):
            errors.append(f"{label}: period must use YYYY-MM")
        if row["kpi_type"] not in KPI_TYPES:
            errors.append(f"{label}: invalid kpi_type '{row['kpi_type']}'")
        if row["favorable_direction"] not in DIRECTIONS:
            errors.append(f"{label}: invalid favorable_direction '{row['favorable_direction']}'")
        if row["materiality_type"] not in MATERIALITY:
            errors.append(f"{label}: invalid materiality_type '{row['materiality_type']}'")
        if row["unit"] == "%" and row["materiality_type"] != "bps":
            errors.append(f"{label}: percentage KPI must use bps materiality")
        if row["unit"] in MONETARY_UNITS and not row["currency"]:
            errors.append(f"{label}: monetary KPI requires currency")
        for field in NUMERIC:
            if field in {"actual", "materiality_threshold"} and row[field] == "":
                errors.append(f"{label}: {field} is required")
            try:
                parsed = number(row[field])
                if field == "materiality_threshold" and parsed is not None and parsed < 0:
                    errors.append(f"{label}: materiality_threshold cannot be negative")
            except InvalidOperation:
                errors.append(f"{label}: {field} must be numeric or blank")
        if row["expected_completion_date"]:
            try:
                date.fromisoformat(row["expected_completion_date"])
            except ValueError:
                errors.append(f"{label}: expected_completion_date must use YYYY-MM-DD")
        if row["management_driver"] and not row["evidence_source"]:
            warnings.append(f"{label}: management driver has no evidence source")
        if row["management_action"] and not row["action_owner"]:
            warnings.append(f"{label}: management action has no owner")
        if row["management_action"] and not row["expected_completion_date"]:
            warnings.append(f"{label}: management action has no expected completion date")
        try:
            actual, budget = number(row["actual"]), number(row["budget"])
            driver = row["management_driver"]
            if actual is not None and budget is not None and driver:
                delta = actual - budget
                if delta < 0 and UP_WORDS.search(driver):
                    warnings.append(f"{label}: management driver direction conflicts with actual versus budget")
                elif delta > 0 and DOWN_WORDS.search(driver):
                    warnings.append(f"{label}: management driver direction conflicts with actual versus budget")
        except InvalidOperation:
            pass
        by_kpi[row["kpi"]].append((line, row))

    companies = {row["company"] for row in rows if row["company"]}
    if len(companies) > 1:
        errors.append(f"input contains multiple companies: {', '.join(sorted(companies))}")

    for kpi, items in by_kpi.items():
        currencies = {r["currency"] for _, r in items if r["currency"]}
        units = {r["unit"] for _, r in items if r["unit"]}
        if len(currencies) > 1:
            warnings.append(f"KPI '{kpi}' has inconsistent currencies: {', '.join(sorted(currencies))}")
        if len(units) > 1:
            warnings.append(f"KPI '{kpi}' has inconsistent units: {', '.join(sorted(units))}")
        ordered = sorted(items, key=lambda item: item[1]["period"])
        previous = None
        for line, row in ordered:
            if previous is not None and row["prior_month"]:
                try:
                    if number(row["prior_month"]) != number(previous["actual"]):
                        warnings.append(f"row {line}: prior_month does not match preceding actual for '{kpi}'")
                except InvalidOperation:
                    pass
            previous = row
    return rows, errors, warnings
