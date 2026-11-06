#!/usr/bin/env python3
"""
Primary Authorized AI Browser Launcher (Brave on Port 9222)
Launches Brave with dedicated profile and CDP port 9222.
"""

import os
import sys
import subprocess
import time
import urllib.request
import json

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
PROFILE_DIR = os.path.expanduser(r"~\.authorized_ai_brave")
DEFAULT_URL = "https://www.youtube.com/watch?v=M4NOQlNgfpE&list=RDMMM4NOQlNgfpE&start_radio=1"

def is_brave_running():
    try:
        r = urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=1).read()
        data = json.loads(r)
        return "Brave" in data.get("Browser", "") or "Chrome" in data.get("Browser", "")
    except Exception:
        return False

def launch():
    if is_brave_running():
        print("[✓] Primary Authorized Browser is ALREADY running on port 9222.")
        return True

    print(f"[*] Starting Brave as Primary AI Browser (Port 9222)...")
    os.makedirs(PROFILE_DIR, exist_ok=True)
    cmd = [
        BRAVE_EXE,
        "--remote-debugging-port=9222",
        f"--user-data-dir={PROFILE_DIR}",
        "--remote-allow-origins=*",
        "--no-first-run",
        "--no-default-browser-check",
        DEFAULT_URL
    ]
    subprocess.Popen(cmd)
    
    for _ in range(15):
        time.sleep(1)
        if is_brave_running():
            print("[✓] Brave is now ONLINE on Port 9222 as the Primary Authorized AI Browser!")
            return True
            
    print("[!] Failed to verify Brave on port 9222.")
    return False

if __name__ == "__main__":
    success = launch()
    sys.exit(0 if success else 1)

