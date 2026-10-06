# Platform instruction boundaries

The executable parts of each skill are shared:

- `scripts/`, `schemas/`, `assets/`, and shared root `references/` contain platform-neutral behavior and data contracts.
- `platforms/<platform>/` contains the instructions installed for that platform.

Supported overlays are `claude-code`, `openai-codex`, and `snowflake-cortex-code`. Each installer copies the common skill folder, then replaces `SKILL.md` and any referenced instruction files with the selected overlay.

Edit `platforms/claude-code/` for Claude-only workflow changes. Those changes do not alter the instructions installed for Codex. Edit `platforms/openai-codex/` only when changing Codex behavior intentionally.

The root `SKILL.md` and root references remain a platform-neutral source snapshot; installers do not use them as the final platform instructions.
