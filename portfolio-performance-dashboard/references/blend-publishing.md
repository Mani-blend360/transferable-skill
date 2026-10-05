# Blend publishing contract

Blend publishing is optional and available only when the current host exposes an authenticated Blend MCP provider with a path-check operation and an HTML-upload operation.

1. Confirm the dashboard is `ready` or `warning`, with `validation.status: PASS` and `reconciliation.status: PASS`.
2. Ask the user for a path slug matching `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
3. State the final path and ask for one explicit confirmation to publish. Host permission prompts remain under the host's control.
4. Render `index.html` using `render_dashboard.py --blend-export` and run `publish_request.py` to produce the fixed request envelope.
5. The host adapter calls its configured path-check tool, then its configured upload tool. Stop and report any failure.

The upload is static HTML only. Never send the CSV or the raw results JSON. Use `visibility: sso`, `access_mode: closed`, `comments_enabled: false`, and `discoverable: false`. This means all Blend-signed-in users can view; it is not a named-viewer allowlist.
