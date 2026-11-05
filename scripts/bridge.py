#!/usr/bin/env python3
"""
Browser Bridge CLI — Bridge agent sandbox to user's live desktop browser.
Supports Microsoft Edge & Google Chrome.
"""
import sys
import os
import argparse
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from cdp_engine import CDPEngine, find_active_port

def cmd_status():
    print("=" * 60)
    print(" 🌐 BROWSER BRIDGE — LIVE STATUS")
    print("=" * 60)
    
    port, browser = find_active_port()
    if port:
        print(f"✅ CDP Status   : CONNECTED")
        print(f"📍 Debug Port   : {port}")
        print(f"🚀 Browser      : {browser}")
        
        engine = CDPEngine(port=port)
        tabs = engine.get_tabs()
        page_tabs = [t for t in tabs if t.get("type") == "page"]
        print(f"📑 Open Tabs    : {len(page_tabs)}")
        for i, t in enumerate(page_tabs[:8], 1):
            print(f"   [{i}] {t.get('title', 'Untitled')[:50]} -> {t.get('url', '')[:60]}")
    else:
        print("⚠️ CDP Status   : No direct CDP port attached.")
        print("💡 Native Fallback: ACTIVE (Windows ShellExecute will direct requests to default browser).")
        
        # Check running browsers via tasklist
        r = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True, text=True
        )
        has_edge = "msedge.exe" in r.stdout.lower()
        has_chrome = "chrome.exe" in r.stdout.lower()
        print(f"🔍 Running Browsers: Microsoft Edge: {'YES' if has_edge else 'NO'} | Google Chrome: {'YES' if has_chrome else 'NO'}")

def cmd_gmail(args):
    print("=" * 60)
    print(" ✉️  DISPATCHING GMAIL VIA BROWSER BRIDGE")
    print("=" * 60)
    print(f"To      : {args.to}")
    print(f"Subject : {args.subject}")
    
    engine = CDPEngine()
    success, msg = engine.compose_gmail(args.to, args.subject, args.body)
    if success:
        print(f"\n✅ SUCCESS: {msg}")
        print("👉 Gmail Compose window is now open in your browser ready to review and send!")
    else:
        print(f"\n❌ ERROR: {msg}")

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
    parser = argparse.ArgumentParser(description="Universal Browser Bridge CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Inspect CDP connection and running browser status")

    p_gmail = sub.add_parser("gmail", help="Open pre-filled Gmail compose window")
    p_gmail.add_argument("--to", required=True, help="Recipient email address")
    p_gmail.add_argument("--subject", required=True, help="Email subject")
    p_gmail.add_argument("--body", required=True, help="Email body content")

    p_open = sub.add_parser("open", help="Open a URL in a new browser tab")
    p_open.add_argument("url", help="URL to navigate to")

    p_eval = sub.add_parser("eval", help="Evaluate JavaScript expression in active tab")
    p_eval.add_argument("code", help="JavaScript code to run")
    p_eval.add_argument("--filter", help="URL substring filter to select specific tab")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
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

