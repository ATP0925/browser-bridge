# 🌐 Browser Bridge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-0078D6.svg)](https://microsoft.com/windows)
[![Architecture: Dedicated Profile](https://img.shields.io/badge/Profile-.authorized__ai__browser-orange.svg)](https://github.com/ATP0925/browser-bridge)
[![Safety: Context Permission Inheritance](https://img.shields.io/badge/Safety-Pre--Approved%20Intent%20Protocol-success.svg)](https://github.com/ATP0925/browser-bridge)

> **Dedicated desktop browser bridge for AI coding agents.** Connects sandboxed AI assistants directly to an **Authorized AI Browser** (`%USERPROFILE%\.authorized_ai_browser` on CDP port `9222`) while keeping your personal everyday browser completely isolated and enforcing a smart **Context-Aware Permission Inheritance Protocol**.

---

## 🛡️ Core Operational Architecture

`browser-bridge` operates on three foundational principles:

1. **Dedicated AI-Authorized Profile (`.authorized_ai_browser`)**:
   - The AI interacts exclusively with a dedicated browser instance launched via your desktop shortcut (`Launch_AI_Authorized_Browser.bat`).
   - Your primary personal browser, everyday tabs, and personal profiles are **never** touched.
2. **Context-Aware Permission Inheritance (गृहीत / Pre-Approved Rule)**:
   - **Explicit Upfront Intent = Full Automated Execution:** If the user has already requested or approved an action in the chat (e.g. *"client ko email compose karke bhej de"*, *"submit this test form"*), the AI treats that category of actions as **pre-authorized (gruhit dharla jaayel)**.
   - The agent executes the entire pipeline end-to-end without stopping for redundant micro-confirmations.
   - **When Does It Stop?** Only when an action is truly out-of-scope, destructive (unsolicited account/data deletion), or involves unexpected real financial charges not mentioned in the prompt.
3. **Full Autonomous Exploration**:
   - Web scraping, DOM inspection, research, and screenshot verification run 100% autonomously.

---

## ⚡ Architecture Flow

```mermaid
flowchart TD
    UserPrompt["User Prompt: 'Client ko email compose karke bhej de'"] --> ScopeCheck{Intent Explicitly Authorized\nin Chat Context?}
    ScopeCheck -->|Yes: Pre-Approved / Gruhit| DirectExec[Full End-to-End Autonomous Execution\nFill -> Click Send -> Verify Delivery]
    ScopeCheck -->|No: Unrequested Sensitive Action| UserConfirm[Stop & Request Owner Confirmation]
    DirectExec --> AuthBrowser[Authorized AI Browser\nPort: 9222 | Profile: .authorized_ai_browser]
    UserConfirm -->|Confirmed| AuthBrowser
```

---

## 🔒 Permission Matrix: Intent vs Prompt Scope

| User Prompt Context | Target Action | Execution Mode |
| :--- | :--- | :--- |
| *"Client ko email bhej do"* | Gmail compose & Send | 🚀 **Automatic End-to-End (Pre-approved)** |
| *"Draft banao / check karo"* | Gmail compose only | 📝 **Draft only, await review** |
| *"Website audit karo"* | Navigation, scraping, eval | 🚀 **Full Autonomy** |
| Unexpected Real Charge / Delete (not in prompt) | Financial / destructive | ⚠️ **Pause & Ask for Confirmation** |

---

## 🚀 Quick Start

### 1. Launching the Authorized Browser
Double-click your desktop shortcut:
```text
C:\Users\atpad\OneDrive\Desktop\Launch_AI_Authorized_Browser.bat
```

### 2. CLI Usage

```powershell
# Check Connection & List Active Tabs
python scripts/bridge.py status

# Dispatch Email
python scripts/bridge.py gmail \
  --to "client@example.com" \
  --subject "Project Findings" \
  --body "Review text..."

# Open Any URL
python scripts/bridge.py open "https://stickitup.xyz"

# Evaluate JavaScript inside tab
python scripts/bridge.py eval "document.title" --filter "stickitup"
```

---

## 📁 Repository Structure

```text
browser-bridge/
├── SKILL.md              # Agent skill manifest & permission inheritance rules
├── README.md             # Complete open source documentation
├── LICENSE               # MIT License
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Package & CLI metadata
└── scripts/
    ├── bridge.py         # Unified CLI (Edge & Chrome via Port 9222)
    ├── cdp_engine.py     # Resilient CDP WebSocket protocol client
    ├── cdp_client.py     # Low-level DevTools protocol client
    └── os_automation.py  # Native UI automation fallback helpers
```

---

## 🛡️ License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

Developed with ❤️ by [ATP0925](https://github.com/ATP0925).
