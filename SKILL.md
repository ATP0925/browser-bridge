---
name: browser-bridge
description: "Universal live desktop browser bridge for agents. Hooks directly into the user's dedicated Authorized AI Browser (port 9222, profile .authorized_ai_browser) launched via Desktop shortcut. Bypasses agent sandbox restrictions, enables authenticated Gmail/web actions, TOTP 2FA code generation, Semantic ARIA interaction, hardware keyboard/mouse dispatch, anti-bot challenge detection, and enforces Context-Aware Permission Inheritance (Pre-Approved Intent Protocol)."
category: browser-automation
risk: safe
source: custom
date_added: "2026-11-05"
author: "ATP0925"
tags: [browser, cdp, authorized-browser, gmail, sandbox-bypass, windows, permissions, intent-inheritance, totp, aria, hardware-input]
---

# Browser Bridge — Authorized AI Browser Control & Permission Inheritance

## 🎯 Purpose & Core Philosophy
`browser-bridge` connects the AI agent directly to a **dedicated Authorized AI Browser instance** (`%USERPROFILE%\.authorized_ai_browser` on CDP port `9222`), launched via the user's desktop shortcut:
`Launch_AI_Authorized_Browser.bat`.

---

## 🛡️ Three Golden Operational Principles:

### 1. Dedicated & Isolated Environment
- The AI **never** touches or alters the user's personal default everyday browser profile.
- All actions execute inside `%USERPROFILE%\.authorized_ai_browser` via CDP port `9222`.

### 2. Context-Aware Permission Inheritance (गृहीत / Pre-Approval Rule)
- **Upfront Intent = Pre-Approved Execution:** Agar user ne chat prompt me pehle hi kisi action ka order ya permission de di hai (e.g., *"client ko email compose karke bhej de"*, *"form submit kar do"*, *"order test proceed karo"*), to us category ke poore workflow ke liye permission **automatically GRUHIT (pre-approved) maani jayegi**.
- AI baar-baar redundant confirmation pooch kar user ka time waste nahi karega. Wo end-to-end execute karega aur direct proof/result deliver karega.
- **Re-Prompt Kab Hoga?** Sirf tab jab koi action:
  - User ke diye gaye scope se bahar ho (out-of-scope),
  - Unanticipated real financial deduction involve kare jo prompt me mention na ho,
  - Irreversible account/data deletion kare jo user ne nahi maanga ho.

### 3. Full Autonomous Exploration
- Web research, navigation, DOM inspection, data scraping, DOM filling, aur screenshot verification bina kisi permission ke 100% autonomous rahenge.

---

## ⚡ CLI Reference

```powershell
# 1. Inspect live connection & list active authorized tabs
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py status

# 2. Launch Authorized Browser if offline (via desktop batch file)
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py launch

# 3. Direct Gmail Dispatch (Pre-approved or drafted)
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py gmail --to "client@example.com" --subject "Review" --body "Draft text..."

# 4. Open any URL in a new tab inside the Authorized Browser
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py open "https://stickitup.xyz"

# 5. Evaluate JavaScript inside an active tab
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py eval "document.title" --filter "stickitup"

# 6. Click elements semantically using ARIA / Text (resilient to redesigns)
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py click "Send" --role "button" --filter "mail"

# 7. Fill inputs semantically by label, placeholder, or name
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py fill "Search" "One Piece" --enter --filter "crunchyroll"

# 8. Dispatch genuine hardware keyboard events (isTrusted === true)
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py key "f" --code "KeyF" --vk 70 --filter "crunchyroll"

# 9. Autonomous 6-digit TOTP 2FA Generation (Zero Dependencies)
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py totp "JBSWY3DPEHPK3PXP"

# 10. Scan active tab for anti-bot challenges (Turnstile, reCAPTCHA, hCaptcha)
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py captcha --filter "login"

# 11. Trigger 3-Second Audio / Visual Human Handoff Checkpoint
python C:\Users\atpad\.gemini\config\skills\browser-bridge\scripts\bridge.py handoff --reason "Payment QR Scan" --filter "checkout"
```

---

## 🔒 Smart Permission Matrix: Intent vs Prompt Scope

| User Prompt State | Action Type | AI Behavior |
| :--- | :--- | :--- |
| User said: *"Email bhej do"* / *"Send it"* | Sending email | 🚀 **Direct Send (Pre-Approved / Gruhit)** |
| User said: *"Draft bana ke dikha"* | Drafting email | 📝 **Draft only, wait for review** |
| User said: *"Store audit karo"* | Browsing / scraping | 🚀 **Direct Autonomy** |
| Interactive CAPTCHA or Payment QR | Gate detected | 🔔 **3-Sec Audio Handoff (`Page.bringToFront`)** |
| Action involves: *Real Card Payment / Delete* (not mentioned in chat) | Sensitive action | ⚠️ **Stop & Ask for Owner Approval** |

---

## 📁 Repository Structure

* [`SKILL.md`](file:///C:/Users/atpad/.gemini/config/skills/browser-bridge/SKILL.md) — Agent manifest and permission inheritance rules.
* [`README.md`](file:///C:/Users/atpad/.gemini/config/skills/browser-bridge/README.md) — GitHub documentation and architecture guide.
* [`scripts/bridge.py`](file:///C:/Users/atpad/.gemini/config/skills/browser-bridge/scripts/bridge.py) — Unified CLI with port 9222 integration and pre-approval handling.
* [`scripts/cdp_engine.py`](file:///C:/Users/atpad/.gemini/config/skills/browser-bridge/scripts/cdp_engine.py) — Resilient WebSocket CDP protocol handler with Semantic ARIA & hardware input dispatch.
* [`scripts/totp_helper.py`](file:///C:/Users/atpad/.gemini/config/skills/browser-bridge/scripts/totp_helper.py) — Pure standard-library RFC 6238 2FA token generator.
* [`scripts/handoff.py`](file:///C:/Users/atpad/.gemini/config/skills/browser-bridge/scripts/handoff.py) — 3-Second visual and audio human-in-the-loop checkpoint runner.
