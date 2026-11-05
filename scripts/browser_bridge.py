#!/usr/bin/env python3
"""
Browser Bridge — Main CLI tool.
Bridges agent sandbox to user's running desktop Chrome browser.

Usage:
    python browser_bridge.py status
    python browser_bridge.py enable-cdp
    python browser_bridge.py open-tab <url>
    python browser_bridge.py gmail-compose --to <email> --subject <subj> --body <body>
    python browser_bridge.py type-text <text>
    python browser_bridge.py screenshot [filename]
"""
import sys
import os
import time
import subprocess
import urllib.parse
import argparse

# Add scripts dir to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from cdp_client import CDPClient, is_cdp_available, find_cdp_port
from os_automation import focus_chrome, open_url_in_chrome, type_text_in_browser, take_screenshot


CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEFAULT_CDP_PORT = 9222


def get_chrome_user_data_dir():
    """Find Chrome's user data directory from running process."""
    r = subprocess.run(
        ["Get-CimInstance", "Win32_Process", "-Filter",
         "Name='chrome.exe'"],
        capture_output=True, text=True, shell=False
    )
    # Fallback to default
    default = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    if os.path.isdir(default):
        return default

    # Try parsing from process command line
    try:
        r = subprocess.run(
            ["powershell", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | Select-Object -First 1 -ExpandProperty CommandLine"],
            capture_output=True, text=True
        )
        cmdline = r.stdout.strip()
        if "--user-data-dir=" in cmdline:
            part = cmdline.split("--user-data-dir=")[1]
            if part.startswith('"'):
                return part.split('"')[1]
            return part.split(" ")[0]
    except Exception:
        pass

    return default


def cmd_status():
    """Check Chrome CDP status and browser state."""
    print("=" * 50)
    print("Browser Bridge — Status")
    print("=" * 50)

    # Check if Chrome is running
    r = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq chrome.exe", "/FO", "CSV", "/NH"],
        capture_output=True, text=True
    )
    chrome_count = len([l for l in r.stdout.strip().split("\n") if "chrome.exe" in l.lower()])
    print(f"Chrome processes: {chrome_count}")

    if chrome_count == 0:
        print("STATUS: Chrome is NOT running")
        return False

    # Check for CDP
    port = find_cdp_port()
    if port:
        print(f"CDP: AVAILABLE on port {port}")
        try:
            cdp = CDPClient(port=port)
            tabs = cdp.get_tabs()
            page_tabs = [t for t in tabs if t.get("type") == "page"]
            print(f"Open tabs: {len(page_tabs)}")
            for t in page_tabs[:5]:
                print(f"  - {t.get('title', 'Untitled')[:60]} | {t.get('url', '')[:50]}")
        except Exception as e:
            print(f"CDP connection error: {e}")
        return True
    else:
        print("CDP: NOT available (Chrome running without --remote-debugging-port)")
        print("Run 'browser_bridge.py enable-cdp' to restart Chrome with CDP")

        # Check window title
        r2 = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq chrome.exe", "/V", "/FO", "CSV"],
            capture_output=True, text=True
        )
        for line in r2.stdout.strip().split("\n"):
            if "Google Chrome" in line:
                title = line.split(",")[-1].strip('"')
                print(f"Active tab: {title[:80]}")
        return False


def cmd_enable_cdp():
    """Restart Chrome with CDP debugging enabled."""
    print("Restarting Chrome with CDP enabled...")

    user_data = get_chrome_user_data_dir()
    print(f"User data dir: {user_data}")

    # Kill Chrome gracefully
    print("Closing Chrome (tabs will be restored)...")
    subprocess.run(["taskkill", "/IM", "chrome.exe", "/F"],
                   capture_output=True, text=True)
    time.sleep(2)

    # Relaunch with CDP
    cmd = [
        CHROME_EXE,
        f"--remote-debugging-port={DEFAULT_CDP_PORT}",
        f"--user-data-dir={user_data}",
        "--restore-last-session",
    ]
    print(f"Launching: {' '.join(cmd[:3])}...")
    subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS)
    time.sleep(4)

    # Verify
    if is_cdp_available(port=DEFAULT_CDP_PORT):
        print(f"SUCCESS: Chrome CDP available on port {DEFAULT_CDP_PORT}")
        return True
    else:
        print("WARNING: CDP not responding yet, waiting longer...")
        time.sleep(3)
        if is_cdp_available(port=DEFAULT_CDP_PORT):
            print(f"SUCCESS: Chrome CDP available on port {DEFAULT_CDP_PORT}")
            return True
        print("FAILED: CDP still not available. Chrome may need manual restart.")
        return False


def cmd_open_tab(url):
    """Open a URL in Chrome."""
    port = find_cdp_port()
    if port:
        print(f"Opening via CDP (port {port})...")
        try:
            cdp = CDPClient(port=port)
            cdp.new_tab(url)
            print(f"Opened: {url}")
            return True
        except Exception as e:
            print(f"CDP failed ({e}), falling back to OS automation...")

    # Fallback
    print("Opening via OS automation (pyautogui)...")
    return open_url_in_chrome(url)


def cmd_gmail_compose(to_email, subject, body):
    """Open Gmail compose with pre-filled fields."""
    params = {
        "view": "cm",
        "fs": "1",
        "to": to_email,
        "su": subject,
        "body": body,
    }
    gmail_url = "https://mail.google.com/mail/?" + urllib.parse.urlencode(params)

    port = find_cdp_port()
    if port:
        print(f"Opening Gmail compose via CDP...")
        try:
            cdp = CDPClient(port=port)
            cdp.new_tab(gmail_url)
            print(f"Gmail compose opened. To: {to_email}")
            print("Email is ready to review and send.")
            return True
        except Exception as e:
            print(f"CDP failed ({e}), falling back to OS automation...")

    # Fallback: OS-level
    print("Opening Gmail compose via OS automation...")
    success = open_url_in_chrome(gmail_url)
    if success:
        print(f"Gmail compose opened. To: {to_email}")
        print("Email is ready to review and send.")
    return success


def cmd_type_text(text):
    """Type text into the currently focused browser field."""
    type_text_in_browser(text)
    print(f"Typed {len(text)} characters.")


def cmd_screenshot(filename=None):
    """Take a screenshot."""
    fname = filename or f"screenshot_{int(time.time())}.png"
    result = take_screenshot(fname)
    print(f"Screenshot saved: {result}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Browser Bridge CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Check Chrome CDP status")
    sub.add_parser("enable-cdp", help="Restart Chrome with CDP enabled")

    p_tab = sub.add_parser("open-tab", help="Open URL in Chrome")
    p_tab.add_argument("url", help="URL to open")

    p_gmail = sub.add_parser("gmail-compose", help="Open Gmail compose")
    p_gmail.add_argument("--to", required=True, help="Recipient email")
    p_gmail.add_argument("--subject", required=True, help="Email subject")
    p_gmail.add_argument("--body", required=True, help="Email body")

    p_type = sub.add_parser("type-text", help="Type text in browser")
    p_type.add_argument("text", help="Text to type")

    p_ss = sub.add_parser("screenshot", help="Take screenshot")
    p_ss.add_argument("filename", nargs="?", help="Output filename")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "enable-cdp":
        cmd_enable_cdp()
    elif args.command == "open-tab":
        cmd_open_tab(args.url)
    elif args.command == "gmail-compose":
        cmd_gmail_compose(args.to, args.subject, args.body)
    elif args.command == "type-text":
        cmd_type_text(args.text)
    elif args.command == "screenshot":
        cmd_screenshot(args.filename)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

