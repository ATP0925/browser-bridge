# Browser Bridge Guidelines for AI Agents (Claude Code, Codex, Cursor, Cowork, ChatGPT Work)

Browser Bridge links agent sessions directly to the user's running desktop browser (Brave, Chrome, or Edge) via Chrome DevTools Protocol (CDP) or native OS automation.

## Supported Multi-Agent Workflows
- **Check Status**: `python scripts/browser_bridge.py status`
- **Enable CDP Debug Port**: `python scripts/browser_bridge.py enable-cdp`
- **Open URL in User Browser**: `python scripts/browser_bridge.py open-tab <url>`
- **Desktop Focus**: `python scripts/os_automation.py`
- **Compose Gmail**: `python scripts/browser_bridge.py gmail-compose --to <email> --subject <subj> --body <body>`
- **Take Screenshot**: `python scripts/browser_bridge.py screenshot`

## Multi-Agent Compatibility
- **Claude Code & Codex**: Execute `python scripts/browser_bridge.py <command>` directly in terminal.
- **Claude Cowork / ChatGPT Work**: Attach to running desktop session via CDP (`http://127.0.0.1:9222`) or spawn headless/interactive daemon using `scripts/launch_brave_daemon.py`.
