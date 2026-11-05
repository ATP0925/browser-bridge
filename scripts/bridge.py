#!/usr/bin/env python3
"""
Browser Bridge CLI — Authorized AI Browser Operator.
Directs AI actions to the user's dedicated Authorized Browser (.authorized_ai_browser)
and enforces the Sensitive Action Permission Protocol with Intent Inheritance.
"""
import sys
import os
import argparse
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from cdp_engine import CDPEngine, find_active_port
import totp_helper
from handoff import execute_handoff_checkpoint

LAUNCHER_PATH = os.path.expandvars(r"%USERPROFILE%\OneDrive\Desktop\Launch_AI_Authorized_Browser.bat")

def cmd_status():
    print("=" * 65)
    print(" 🛡️  AUTHORIZED AI BROWSER BRIDGE — LIVE STATUS")
    print("=" * 65)
    
    port, browser = find_active_port()
    if port:
        print(f"✅ Connection Status : ACTIVE & CONNECTED")
        print(f"📍 Authorized Port   : {port}")
        print(f"🚀 Browser Engine    : {browser}")
        print(f"📁 Isolated Profile  : %USERPROFILE%\\.authorized_ai_browser")
        print(f"🔒 Safety Protocol   : ENFORCED (Pre-Approved Intent Protocol active)")
        
        engine = CDPEngine(port=port)
        tabs = engine.get_tabs()
        print(f"\n📑 Active Authorized Tabs ({len(tabs)}):")
        for i, t in enumerate(tabs, 1):
            title = t.get('title', 'Untitled')[:45]
            url = t.get('url', '')[:65]
            print(f"   [{i}] {title:<46} | {url}")
    else:
        print("❌ Status: Authorized AI Browser is NOT currently running.")
        print(f"💡 To start it, run your desktop shortcut:")
        print(f"   {LAUNCHER_PATH}")
        print("   or execute: python bridge.py launch")

def cmd_launch():
    print(f"Launching Authorized AI Browser via: {LAUNCHER_PATH} ...")
    if os.path.isfile(LAUNCHER_PATH):
        subprocess.Popen(["cmd.exe", "/c", LAUNCHER_PATH], shell=False)
        print("✅ Launcher triggered. Waiting 3 seconds for port 9222...")
    else:
        profile = os.path.expandvars(r"%USERPROFILE%\.authorized_ai_browser")
        chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        cmd = [
            chrome_exe,
            "--remote-debugging-port=9222",
            f"--user-data-dir={profile}",
            "--remote-allow-origins=*",
            "https://mail.google.com"
        ]
        subprocess.Popen(cmd, shell=False)
        print(f"✅ Direct spawn triggered with profile: {profile}")

def cmd_gmail(args):
    print("=" * 65)
    print(" ✉️  PREPARING GMAIL IN AUTHORIZED AI BROWSER")
    print("=" * 65)
    print(f"To      : {args.to}")
    print(f"Subject : {args.subject}")
    
    engine = CDPEngine()
    if not engine.is_connected():
        print("⚠️ Authorized Browser offline. Launching it now...")
        cmd_launch()
        import time
        time.sleep(3)
        engine = CDPEngine()

    success, msg = engine.open_tab(f"https://mail.google.com/mail/u/0/?view=cm&fs=1&to={args.to}&su={args.subject}&body={args.body}")
    if success:
        print(f"\n✅ {msg}")
        print("👉 Pre-filled draft is ready in your Authorized Browser.")
    else:
        print(f"\n❌ Error: {msg}")

def cmd_open(args):
    engine = CDPEngine()
    success, msg = engine.open_tab(args.url)
    print(f"Status: {msg}")

def cmd_eval(args):
    engine = CDPEngine()
    result, err = engine.evaluate_script(args.code, args.filter)
    if err:
        print(f"Error: {err}")
    else:
        print(f"Result: {result}")

def cmd_click(args):
    engine = CDPEngine()
    res = engine.click_semantic(args.name, role=args.role, tab_url_filter=args.filter)
    print("Semantic Click:", res)

def cmd_fill(args):
    engine = CDPEngine()
    res = engine.fill_semantic(args.label, args.value, tab_url_filter=args.filter, press_enter=args.enter)
    print("Semantic Fill:", res)

def cmd_key(args):
    engine = CDPEngine()
    ok, msg = engine.send_hardware_key(args.key, code=args.code, windows_virtual_key_code=args.vk, tab_url_filter=args.filter)
    print(f"Key Dispatch ({ok}): {msg}")

def cmd_totp(args):
    code = totp_helper.generate_totp(args.secret)
    rem = totp_helper.get_remaining_seconds()
    print(f"Generated 2FA TOTP: {code} (Valid for {rem}s)")

def cmd_captcha(args):
    engine = CDPEngine()
    status = engine.detect_captcha(tab_url_filter=args.filter)
    print("Anti-Bot Scan:", status)

def cmd_handoff(args):
    engine = CDPEngine()
    ok = execute_handoff_checkpoint(engine, reason=args.reason, tab_filter=args.filter)
    print(f"Handoff Outcome: {'Completed' if ok else 'Timed Out'}")

def main():
    parser = argparse.ArgumentParser(description="Authorized AI Browser Bridge CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Inspect Authorized Browser connection and active tabs")
    sub.add_parser("launch", help="Launch the Authorized AI Browser using desktop launcher")

    p_gmail = sub.add_parser("gmail", help="Open pre-filled Gmail compose tab")
    p_gmail.add_argument("--to", required=True, help="Recipient email address")
    p_gmail.add_argument("--subject", required=True, help="Email subject")
    p_gmail.add_argument("--body", required=True, help="Email body content")

    p_open = sub.add_parser("open", help="Open a URL in a new Authorized Browser tab")
    p_open.add_argument("url", help="URL to navigate to")

    p_eval = sub.add_parser("eval", help="Evaluate JavaScript expression in active tab")
    p_eval.add_argument("code", help="JavaScript code to run")
    p_eval.add_argument("--filter", help="URL or title substring filter to select specific tab")

    p_click = sub.add_parser("click", help="Click an element using semantic ARIA / text matching")
    p_click.add_argument("name", help="Aria-label, text, or identifier substring")
    p_click.add_argument("--role", help="ARIA role (button, link, checkbox)")
    p_click.add_argument("--filter", help="Target tab filter")

    p_fill = sub.add_parser("fill", help="Fill an input using semantic label matching")
    p_fill.add_argument("label", help="Input label, placeholder, or name")
    p_fill.add_argument("value", help="Text value to enter")
    p_fill.add_argument("--enter", action="store_true", help="Press Enter after filling")
    p_fill.add_argument("--filter", help="Target tab filter")

    p_key = sub.add_parser("key", help="Dispatch genuine hardware keyboard event via CDP")
    p_key.add_argument("key", help="Key character (e.g. f, k, Enter)")
    p_key.add_argument("--code", default="KeyF", help="Key code (e.g. KeyF, Space, Enter)")
    p_key.add_argument("--vk", type=int, default=70, help="Windows Virtual Key Code")
    p_key.add_argument("--filter", help="Target tab filter")

    p_totp = sub.add_parser("totp", help="Generate RFC 6238 6-digit TOTP 2FA code")
    p_totp.add_argument("secret", help="Base32 2FA Secret Key")

    p_captcha = sub.add_parser("captcha", help="Scan active page for CAPTCHA/Turnstile challenges")
    p_captcha.add_argument("--filter", help="Target tab filter")

    p_handoff = sub.add_parser("handoff", help="Trigger 3-second audio/visual human handoff")
    p_handoff.add_argument("--reason", default="Manual checkpoint", help="Reason for handoff")
    p_handoff.add_argument("--filter", help="Target tab filter")

    args = parser.parse_args()

    dispatch = {
        "status": cmd_status,
        "launch": cmd_launch,
        "gmail": lambda: cmd_gmail(args),
        "open": lambda: cmd_open(args),
        "eval": lambda: cmd_eval(args),
        "click": lambda: cmd_click(args),
        "fill": lambda: cmd_fill(args),
        "key": lambda: cmd_key(args),
        "totp": lambda: cmd_totp(args),
        "captcha": lambda: cmd_captcha(args),
        "handoff": lambda: cmd_handoff(args)
    }

    if args.command in dispatch:
        dispatch[args.command]()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
