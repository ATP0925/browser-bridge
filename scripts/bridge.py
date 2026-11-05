#!/usr/bin/env python3
"""
Browser Bridge CLI — Authorized AI Browser Operator.
Directs AI actions to the user's dedicated Authorized Browser (.authorized_ai_browser)
and enforces the Sensitive Action Permission Protocol.
"""
import sys
import os
import argparse
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from cdp_engine import CDPEngine, find_active_port

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
        print(f"🔒 Safety Protocol   : ENFORCED (Sensitive actions require owner approval)")
        
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
        # Fallback to direct launch with dedicated profile
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

    success, msg = engine.compose_gmail(args.to, args.subject, args.body)
    if success:
        print(f"\n✅ {msg}")
        print("👉 Pre-filled draft is ready in your Authorized Browser.")
        print("⚠️ SAFETY GUARD: AI will NOT auto-click Send without your explicit permission.")
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

def main():
    parser = argparse.ArgumentParser(description="Authorized AI Browser Bridge CLI")
    sub = parser.parse_args if False else parser.add_subparsers(dest="command")

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

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "launch":
        cmd_launch()
    elif args.command == "gmail":
        cmd_gmail(args)
    elif args.command == "open":
        cmd_open(args)
    elif args.command == "eval":
        cmd_eval(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
