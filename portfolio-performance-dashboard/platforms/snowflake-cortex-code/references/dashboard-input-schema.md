# Dashboard input schema

The dashboard consumes `RESULTS.json` from the portfolio analysis workflow. Require `schema_version`, `status`, `period`, `source`, `validation`, `reconciliation`, and `results`.

## Accepted top-level states

- `ready`: valid, reconciled results without warnings.
- `warning`: valid, reconciled results with warnings.
- `blocked`: source validation failed.
- `empty`: source was valid but the requested period produced no results.

## Successful KPI object

Each item requires `kpi`, `kpi_type`, `actual`, `unit`, `direction`, `materiality_type`, `materiality_threshold`, `comparisons`, and `evidence_class`. `currency`, full-year revision, driver, source, action, owner, and date may be empty.

Each comparison key may be `null`. A populated comparison requires `comparison`, `absolute_variance`, `percentage_variance`, `materiality`, and `favorability`. Percentage KPIs also carry percentage-point and basis-point differences.

`percentage_variance` may be numeric or `not_meaningful`. Missing values are never inferred.

Run the validator before rendering. It checks structural types, state consistency, duplicate KPI names, recognized enums, successful-state gates, and comparison shapes.
