#!/usr/bin/env python3
"""
Spawns an independent, detached Brave browser process via Windows WMI/CIM.
Never terminated when parent shell closes.
"""

import os
import sys
import subprocess
import time
import urllib.request
import json

PROFILE_DIR = os.path.expanduser(r"~\.authorized_ai_brave")
BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
PORT = 9222

def clean_locks():
    """Remove only top-level browser lock files that prevent launch. Never recurse into subdirs."""
    if not os.path.exists(PROFILE_DIR):
        return
    # Only clean specific known lock files at the profile root
    lock_files = ["SingletonLock", "SingletonCookie", "SingletonSocket"]
    for lock_name in lock_files:
        lock_path = os.path.join(PROFILE_DIR, lock_name)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
            except Exception:
                pass

def is_live():
    try:
        r = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1.5).read()
        return len(json.loads(r)) > 0
    except Exception:
        return False

def spawn():
    if is_live():
        print(f"[✓] Brave is ALREADY running on port {PORT}")
        return True

    clean_locks()
    
    cmd_line = f'"{BRAVE_EXE}" --user-data-dir="{PROFILE_DIR}" --remote-debugging-port={PORT} --remote-allow-origins=* --no-first-run --no-default-browser-check https://acadflow.dpdns.org/'
    
    # PowerShell CIM Process Creation (escapes job object bounds)
    ps_cmd = f'$cmd = \'{cmd_line}\'; Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{{CommandLine = $cmd}}'
    
    print("[*] Spawning independent Brave process via Win32_Process...")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
    
    for i in range(12):
        time.sleep(1)
        if is_live():
            print(f"[✓] Independent Brave CDP is ONLINE on port {PORT}!")
            return True
            
    print("[!] Timed out waiting for Brave to respond on port 9222.")
    return False

if __name__ == "__main__":
    success = spawn()
    sys.exit(0 if success else 1)

