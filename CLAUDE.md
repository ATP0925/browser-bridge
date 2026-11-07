# Browser Bridge Rules for Claude Code

@AGENTS.md

## Claude Code Specifics
- Always verify browser readiness via `python scripts/browser_bridge.py status`.
- For form filling and web actions requiring authenticated sessions, prefer CDP on port 9222.
- Run test suite with `python -m pytest tests/ -v`.
