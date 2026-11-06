#!/usr/bin/env python3
"""
Persistent Daemon Launcher for Authorized Brave Browser (Port 9222)
Runs completely detached from PowerShell or Python parent processes.
"""

import os
import sys
import subprocess
import time
import urllib.request
import json

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
PROFILE_DIR = os.path.expanduser(r"~\.authorized_ai_brave")
PORT = 9222

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

def is_cdp_live():
    try:
        r = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1.5).read()
        return len(json.loads(r)) > 0
    except Exception:
        return False

def start_brave_persistent(target_url="https://acadflow.dpdns.org/"):
    if is_cdp_live():
        print(f"[✓] Authorized Brave Browser is ALREADY live on port {PORT}")
        return True

    print(f"[*] Spawning persistent detached Brave instance on port {PORT}...")
    os.makedirs(PROFILE_DIR, exist_ok=True)
    
    cmd = [
        BRAVE_EXE,
        f"--user-data-dir={PROFILE_DIR}",
        f"--remote-debugging-port={PORT}",
        "--remote-allow-origins=*",
        "--no-first-run",
        "--no-default-browser-check",
        target_url
    ]
    
    flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(
        cmd,
        creationflags=flags,
        close_fds=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    for i in range(12):
        time.sleep(1)
        if is_cdp_live():
            print(f"[✓] Persistent Brave CDP is ONLINE on port {PORT}!")
            return True
            
    print("[!] Timed out waiting for Brave CDP.")
    return False

if __name__ == "__main__":
    success = start_brave_persistent()
    sys.exit(0 if success else 1)

