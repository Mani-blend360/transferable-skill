# Blend publishing contract

Blend publishing is optional and available only when the current host exposes an authenticated Blend MCP provider with a path-check operation and an HTML-upload operation.

1. Confirm the dashboard is `ready` or `warning`, with `validation.status: PASS` and `reconciliation.status: PASS`.
2. In the Claude dashboard artifact, collect a path slug matching `^[a-z0-9]+(?:-[a-z0-9]+)*$` and require **Confirm and publish**. The button copies a publication prompt; when the user pastes and sends that prompt in Claude chat, treat it as the sole authorization for this publication.
3. Render `index.html` using `render_dashboard.py --blend-export` and run `publish_request.py` to produce the fixed request envelope.
4. After receiving the copied publication prompt, the host adapter immediately calls its configured path-check tool, then its configured upload tool. Do not request another confirmation. Stop and report any failure.

The upload is static HTML only. Never send the CSV or the raw results JSON. Use `visibility: sso`, `access_mode: closed`, `comments_enabled: false`, and `discoverable: false`. This means all Blend-signed-in users can view; it is not a named-viewer allowlist.
