# Interaction contract

Keep filtering and KPI selection local to the generated dashboard. The portable HTML must not depend on a vendor browser API to continue a chat or perform a write.

For an investigation action, construct a prompt containing company, period, selected KPI, actual and comparison values, supplied variance, materiality, favorability, evidence class, driver, evidence source, and management follow-up. Require the host agent to distinguish facts from missing, contradictory, and hypothetical evidence. Do not invent facts, actions, owners, dates, or investment recommendations.

The dashboard may copy this prompt locally. A host adapter may offer a native follow-up action only when that host supports it.

For Blend publication, use the cross-host procedure in [blend-publishing.md](blend-publishing.md). The user supplies the slug and explicitly confirms before the adapter calls any MCP write tool.
