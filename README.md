# 🌉 Browser Bridge — Authorized AI Browser Operator & Automation Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Windows / Linux / macOS](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-brightgreen.svg)]()
[![Protocol: CDP + ARIA](https://img.shields.io/badge/Engine-CDP%20%2B%20ARIA%20%2B%20TOTP-purple.svg)]()

> Direct desktop browser integration for autonomous AI coding agents (Antigravity / Claude Code / Codex). Bridges sandbox isolation, connects to an isolated browser profile on CDP port `9222`, and implements the **Context-Aware Intent Inheritance (गृहीत कार्यप्रणाली)** protocol.

---

## 🌟 Key Features

1. **Dedicated Profile Isolation (`%USERPROFILE%\.authorized_ai_browser`):**
   - Operates exclusively on port `9222` launched by your desktop batch file (`Launch_AI_Authorized_Browser.bat`).
   - Your primary everyday personal browser is **never touched, closed, or modified**.

2. **Semantic Accessibility (ARIA) Engine:**
   - Clicks and fills inputs using accessible roles, names, and text rather than fragile, minified CSS selectors. Resilient across site redesigns.

3. **Engine-Level Hardware Input Dispatch (`isTrusted === true`):**
   - Dispatches genuine keyboard and mouse events via Chrome DevTools Protocol (`Input.dispatchKeyEvent`). Fullscreen toggles, media keys, and shortcuts execute cleanly without getting blocked by user-activation gates.

4. **Autonomous TOTP 2FA Token Generator:**
   - Pure Python standard library implementation of RFC 6238. Generates 6-digit Authenticator codes on the fly without external dependencies.

5. **Anti-Bot Challenge Detection & 3-Second Audio Handoff:**
   - Detects Cloudflare Turnstile, reCAPTCHA, and hCaptcha iframes. Brings the tab to the foreground and sounds a voice alert for zero-friction human verification before auto-resuming.

6. **Context-Aware Permission Inheritance (Pre-Approved Intent Protocol):**
   - If an action was explicitly requested by the user in chat (e.g. *"send the email"*, *"fill the checkout details"*), the entire execution pipeline runs autonomously without annoying pause prompts.

---

## 🚀 Quick Start CLI

```powershell
# Check connection & list open tabs
python scripts/bridge.py status

# Generate 2FA TOTP code
python scripts/bridge.py totp "JBSWY3DPEHPK3PXP"

# Scan active page for anti-bot challenges
python scripts/bridge.py captcha --filter "login"

# Dispatch genuine hardware key (e.g., toggle fullscreen on video)
python scripts/bridge.py key "f" --code "KeyF" --vk 70 --filter "crunchyroll"

# Click element semantically using ARIA or visible text
python scripts/bridge.py click "Send" --role "button" --filter "mail"

# Fill input semantically
python scripts/bridge.py fill "Search" "One Piece" --enter

# Trigger 3-Second Audio/Visual Human Handoff
python scripts/bridge.py handoff --reason "Payment QR Scan"
```

---

## 🔒 Permission & Safety Architecture

```
User Prompt: "Send 3 emails to X asking for name, age, address"
               │
               ▼
[Intent Analysis]: Explicit user order with full permission?
               │
        ┌──────┴──────┐
       YES            NO
        │              │
        ▼              ▼
[Pre-Approved Mode]  [Interactive Mode]
- Zero intermediate   - Drafts only
  prompts             - Pauses for approval
- Full execution &      before send/checkout
  live proof report
```

---

## 📄 License
MIT License. Created by [ATP0925](https://github.com/ATP0925).
