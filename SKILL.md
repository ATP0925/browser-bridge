---
name: browser-bridge
description: "Universal live desktop browser bridge for agents. Hooks directly into the user's dedicated Authorized AI Browser (port 9222, profile .authorized_ai_browser) launched via Desktop shortcut. Bypasses agent sandbox restrictions, enables authenticated Gmail/web actions, and enforces the Sensitive Action Permission Protocol."
category: browser-automation
risk: safe
source: custom
date_added: "2026-11-05"
author: "ATP0925"
tags: [browser, cdp, authorized-browser, gmail, sandbox-bypass, windows, permissions]
---

# Browser Bridge — Authorized AI Browser Control & Safety Skill

## 🎯 Purpose & Core Philosophy
`browser-bridge` connects the AI agent directly to a **dedicated Authorized AI Browser instance** (`%USERPROFILE%\.authorized_ai_browser` on CDP port `9222`), launched via the user's desktop shortcut:
`Launch_AI_Authorized_Browser.bat`.

### 🛡️ Two Golden Operational Principles:
1. **Isolated from Everyday Browser**:
   - The AI **never** tampers with or touches the user's personal default everyday browser profile.
   - It only operates inside the dedicated `%USERPROFILE%\.authorized_ai_browser` profile where the user grants authorization.
2. **Autonomous Exploration vs. Sensitive Action Approval**:
   - **Autonomous (No Permission Needed)**: The AI is 100% free to navigate, inspect, extract DOM data, scrape, evaluate JavaScript, take screenshots, and prepare pre-filled form drafts.
   - **Sensitive Action Protocol (MANDATORY Permission Required)**: Before executing any consequential action—such as **clicking "Send" on an email**, **making a payment**, **placing an order**, **deleting data**, or **submitting sensitive credentials**—the AI **MUST stop and ask the user/owner for explicit confirmation**.

---

## ⚡ CLI Reference

```powershell
# 1. Inspect live connection & list active authorized tabs
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py status

# 2. Launch Authorized Browser if offline (via desktop batch file)
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py launch

# 3. Prepare a pre-filled Gmail compose draft (leaves Send button for owner approval)
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py gmail --to "client@example.com" --subject "Review" --body "Draft text..."

# 4. Open any URL in a new tab inside the Authorized Browser
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py open "https://stickitup.xyz"

# 5. Evaluate JavaScript inside an active tab (e.g. read cart state or page title)
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py eval "document.title" --filter "stickitup"
```

---

## 🔒 Sensitive Action Permission Matrix

| Operation Category | Action Examples | Agent Autonomy | Permission Required? |
| :--- | :--- | :--- | :--- |
| **Observation** | Reading page text, inspecting DOM, status checks | ✅ Full Autonomy | ❌ No |
| **Navigation** | Opening URLs, switching tabs, reloading | ✅ Full Autonomy | ❌ No |
| **Drafting** | Pre-filling email body, filling search inputs | ✅ Full Autonomy | ❌ No |
| **Outreach Dispatch** | Clicking "Send" in Gmail or messaging apps | ⚠️ Gated Action | **✅ YES (Owner Approval Required)** |
| **Financial / Cart** | Clicking "Pay", entering CVV, placing orders | ⚠️ Gated Action | **✅ YES (Owner Approval Required)** |
| **Destructive** | Deleting accounts, dropping databases, clearing data| ⚠️ Gated Action | **✅ YES (Owner Approval Required)** |

---

## 📁 Repository Structure

* [`SKILL.md`](file:///C:/Users/atpad/.gemini/config/skills/browser-bridge/SKILL.md) — Agent manifest and permission rules.
* [`README.md`](file:///C:/Users/atpad/.gemini/config/skills/browser-bridge/README.md) — Comprehensive GitHub repository documentation.
* [`scripts/bridge.py`](file:///C:/Users/atpad/.gemini/config/skills/browser-bridge/scripts/bridge.py) — Unified CLI with port 9222 integration and safety gates.
* [`scripts/cdp_engine.py`](file:///C:/Users/atpad/.gemini/config/skills/browser-bridge/scripts/cdp_engine.py) — Resilient WebSocket CDP protocol handler.
