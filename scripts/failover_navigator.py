#!/usr/bin/env python3
"""
Intelligent Dual-Browser Failover Navigator
Primary Engine   : Brave Browser (Port 9222, Shields & Ad-Blocking, Isolated Profile)
Secondary Fallback: Google Chrome (Port 9223, Standard Chromium Renderer, Fallback)

Rules:
1. Always attempts navigation in Brave first.
2. Checks for network errors, DNS blocks, ERR_BLOCKED_BY_CLIENT, or render failures.
3. Automatically triggers seamless failover to Google Chrome if Brave fails.
"""

import os
import sys
import time
import json
import urllib.request
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import cdp_engine
import spawn_brave_independent

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_PROFILE = os.path.expanduser(r"~\.authorized_ai_browser")
CHROME_PORT = 9223

BRAVE_PORT = 9222

ERROR_INDICATORS = [
    "chrome-error://",
    "dns_probe_finished",
    "err_connection_refused",
    "err_name_not_resolved",
    "err_blocked_by_client",
    "err_connection_timed_out",
    "site can't be reached",
    "this site can’t be reached",
    "403 forbidden",
    "access denied",
    "page not available"
]

def is_port_active(port):
    try:
        r = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1.5).read()
        return len(json.loads(r)) > 0
    except Exception:
        return False

def ensure_brave():
    if not is_port_active(BRAVE_PORT):
        print("[*] Brave is offline. Spawning Primary Brave Engine...")
        spawn_brave_independent.spawn()
    return is_port_active(BRAVE_PORT)

def ensure_chrome():
    if is_port_active(CHROME_PORT):
        return True

    print(f"[*] Spawning Secondary Fallback Browser: Chrome on port {CHROME_PORT}...")
    os.makedirs(CHROME_PROFILE, exist_ok=True)
    
    cmd_line = f'"{CHROME_EXE}" --user-data-dir="{CHROME_PROFILE}" --remote-debugging-port={CHROME_PORT} --remote-allow-origins=* --no-first-run --no-default-browser-check about:blank'
    ps_cmd = f'$cmd = \'{cmd_line}\'; Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{{CommandLine = $cmd}}'
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
    
    for _ in range(12):
        time.sleep(1)
        if is_port_active(CHROME_PORT):
            print(f"[✓] Secondary Chrome Engine is ONLINE on port {CHROME_PORT}!")
            return True
    return False

def check_tab_health(client, tab_url_filter=None):
    """
    Evaluates current tab URL and document state to detect navigation failures.
    """
    js = """
    (() => {
        return {
            url: window.location.href,
            title: document.title,
            readyState: document.readyState,
            bodyText: document.body ? document.body.innerText.slice(0, 500) : ''
        };
    })()
    """
    val, err = client.evaluate_script(js, tab_url_filter=tab_url_filter)
    if err or not isinstance(val, dict):
        return False, f"Evaluation failed: {err} (val={val})"

    curr_url = val.get("url", "").lower()
    curr_title = val.get("title", "").lower()
    body_snippet = val.get("bodyText", "").lower()

    for item in ERROR_INDICATORS:
        if item in curr_url or item in curr_title or item in body_snippet:
            return False, f"Detected error state matching '{item}' in page"

    return True, val

def navigate_with_fallback(url, bring_to_front=True):
    """
    Primary attempt in Brave; Automatic fallback to Chrome if failed.
    """
    print(f"\n=======================================================")
    print(f" 🌐 NAVIGATION REQUEST: {url}")
    print(f"=======================================================")
    
    # 1. Primary Attempt: Brave
    print(f"[1/2] Attempting navigation in PRIMARY Browser: Brave (Port {BRAVE_PORT})...")
    if ensure_brave():
        try:
            brave_client = cdp_engine.CDPEngine(port=BRAVE_PORT)
            tab = brave_client.open_tab(url)
            time.sleep(3) # Wait for initial response
            
            # Check if page is healthy
            healthy, detail = check_tab_health(brave_client, tab_url_filter=url)
            if healthy:
                print(f"[✓] PRIMARY SUCCESS: Loaded successfully in Brave!")
                print(f"    Title: {detail.get('title')}")
                print(f"    URL  : {detail.get('url')}")
                if bring_to_front:
                    brave_client.bring_to_front(tab_url_filter=url)
                return {
                    "success": True,
                    "engine": "Brave (Primary)",
                    "port": BRAVE_PORT,
                    "title": detail.get("title"),
                    "url": detail.get("url")
                }
            else:
                print(f"[!] Brave Warning: {detail}. Triggering Secondary Fallback...")
        except Exception as e:
            print(f"[!] Brave Navigation Exception: {e}. Triggering Secondary Fallback...")
    else:
        print("[!] Brave failed to respond. Triggering Secondary Fallback...")

    # 2. Secondary Attempt: Chrome
    print(f"\n[2/2] ⚠️ INITIATING SECONDARY PRIORITY FALLOVER: Google Chrome (Port {CHROME_PORT})...")
    if ensure_chrome():
        try:
            chrome_client = cdp_engine.CDPEngine(port=CHROME_PORT)
            tab = chrome_client.open_tab(url)
            time.sleep(3)
            
            healthy, detail = check_tab_health(chrome_client, tab_url_filter=url)
            print(f"[✓] SECONDARY SUCCESS: Successfully recovered and loaded in Google Chrome!")
            print(f"    Title: {detail.get('title') if isinstance(detail, dict) else 'Unknown'}")
            print(f"    URL  : {detail.get('url') if isinstance(detail, dict) else url}")
            if bring_to_front:
                chrome_client.bring_to_front(tab_url_filter=url)
            return {
                "success": True,
                "engine": "Google Chrome (Secondary Fallback)",
                "port": CHROME_PORT,
                "fallback_triggered": True,
                "title": detail.get("title") if isinstance(detail, dict) else "",
                "url": detail.get("url") if isinstance(detail, dict) else url
            }
        except Exception as e:
            print(f"[!] Secondary Chrome Exception: {e}")
            return {"success": False, "error": f"Both Brave and Chrome failed: {e}"}
            
    return {"success": False, "error": "Both Brave and Chrome were unavailable"}

if __name__ == "__main__":
    test_target = sys.argv[1] if len(sys.argv) > 1 else "https://campusnotify-tau.vercel.app/"
    result = navigate_with_fallback(test_target)
    print("\nResult Summary:", json.dumps(result, indent=2))
