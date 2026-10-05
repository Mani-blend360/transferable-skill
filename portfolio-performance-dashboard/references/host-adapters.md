# Host adapters

The core commands and artifact contract are identical on every host. Use only the section for the active host.

## Codex

Render the dashboard as an in-chat Codex widget when sharing is requested; an ordinary file/editor preview is not a reliable chat-action surface. The widget's `Share on Blend` button collects a slug and a final confirmation, then continues the Codex chat. If an authenticated Blend MCP server is available, invoke its configured check and upload tools. The exported Blend HTML never includes this authoring control.

## Claude Code

Display or open `dashboard.html` using the Claude Code client's supported artifact workflow. If the Claude environment exposes the same authenticated Blend MCP server, perform the shared publish procedure in chat; otherwise leave sharing unavailable and report the missing capability.

## Snowflake Cortex Code (CoCo)

Use the Cortex-supported file or artifact surface for `dashboard.html`. Perform the shared publish procedure only when a compatible authenticated Blend MCP provider is configured. Otherwise, return the generated read-only `index.html` as the handoff artifact.
