# Dashboard UI states

## Ready

Render the full interactive dashboard. Keep reconciliation PASS visible but quiet.

## Warning

Render the full dashboard and a compact warning count. Provide a warnings view or disclosure with the exact messages. Do not visually equate warnings with calculation failure.

## Blocked

Do not render KPI cards or charts. Show a focused validation panel containing:

- “Dashboard unavailable — source validation failed.”
- Error count and exact field or row messages.
- Source filename and requested period when available.
- A concise next step to correct the input and rerun analysis.

## Empty

Do not show zero KPI values. State that no rows exist for the requested period, show that period, and direct the user to select a populated period or update the source.

## Reconciliation failed

Do not show unverified headline values. Show each mismatch, its KPI and field when supplied, and a request to rerun or investigate reconciliation.

## Partial KPI data

- Missing comparison: show an em dash and “Comparison unavailable”; omit its bar.
- Zero comparison: show `percentage variance not meaningful`; use absolute, pp, or bps values when available.
- Missing driver on a material movement: show “Driver not provided; management input required.”
- Missing action, owner, or date: show “Not supplied” for the specific field; do not fabricate a placeholder person or deadline.
- Unknown optional field: omit its UI region rather than leaving a broken or empty card.

## Visual language

Use a quiet modern product surface with strong spacing, a neutral hierarchy, restrained accent color, and semantic favorable/unfavorable colors paired with text. Support light and dark appearance and widths from 320px to 1024px. Keep the full desktop view to one dominant variance section plus one detail panel; stack them on narrow screens.

Match the fixed dark reference palette: deep navy surfaces, off-white text, periwinkle accents, coral unfavorable values, mint favorable values, and amber synthetic or warning labels. Evidence badges use periwinkle text on a dark indigo fill. Use off-white for every non-semantic text element—including metadata, field labels, inactive tabs, secondary descriptions, card labels, and “Evidence-backed commentary”—so no text relies on reduced opacity or a low-contrast gray.
