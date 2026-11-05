"""
Multi-Browser Profile Manager for Browser Bridge.
Maps and connects official Chrome and Edge profiles to the AI agent:
1. Edge Default -> atpadkarmaruti@gmail.com
2. Chrome Profile 2 -> vu4f2526072@pvppcoe.ac.in (College)
3. Chrome Default -> atpadkarpratik00925@gmail.com (Personal)
4. Authorized AI Browser -> Isolated 9222 profile
"""
import os
import json
import shutil
import subprocess

PROFILES_DEF = {
    "brave_personal": {
        "name": "Brave (Personal & AcadFlow)",
        "browser": "brave",
        "port": 9226,
        "exe": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        "data_dir": os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data"),
        "profile_dir": "Default",
        "ai_clone_dir": os.path.expandvars(r"%USERPROFILE%\.authorized_ai_brave"),
        "launcher": os.path.expandvars(r"%USERPROFILE%\OneDrive\Desktop\Launch_AI_Authorized_Brave.bat")
    },
    "edge_maruti": {
        "name": "Edge (atpadkarmaruti@gmail.com)",
        "browser": "edge",
        "port": 9225,
        "exe": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "data_dir": os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data"),
        "profile_dir": "Default",
        "ai_clone_dir": os.path.expandvars(r"%USERPROFILE%\.authorized_ai_edge"),
        "launcher": os.path.expandvars(r"%USERPROFILE%\OneDrive\Desktop\Launch_AI_Authorized_Edge.bat")
    },
    "chrome_college": {
        "name": "Chrome College (vu4f2526072@pvppcoe.ac.in)",
        "browser": "chrome",
        "port": 9224,
        "exe": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "data_dir": os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
        "profile_dir": "Profile 2",
        "ai_clone_dir": os.path.expandvars(r"%USERPROFILE%\.authorized_ai_college")
    },
    "chrome_personal": {
        "name": "Chrome Personal (atpadkarpratik00925@gmail.com)",
        "browser": "chrome",
        "port": 9223,
        "exe": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "data_dir": os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
        "profile_dir": "Default",
        "ai_clone_dir": os.path.expandvars(r"%USERPROFILE%\.authorized_ai_personal")
    },
    "ai_browser": {
        "name": "Dedicated AI Browser (.authorized_ai_browser)",
        "browser": "chrome",
        "port": 9222,
        "exe": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "data_dir": os.path.expandvars(r"%USERPROFILE%\.authorized_ai_browser"),
        "profile_dir": "Default",
        "ai_clone_dir": os.path.expandvars(r"%USERPROFILE%\.authorized_ai_browser")
    }
}

def list_profiles():
    print("=" * 70)
    print(" 🌐 DETECTED USER BROWSER PROFILES & LINKED IDENTITIES")
    print("=" * 70)
    for key, info in PROFILES_DEF.items():
        exists = os.path.isdir(info["data_dir"])
        print(f"[{key}]")
        print(f"  * Identity : {info['name']}")
        print(f"  * Engine   : {info['browser'].upper()} (CDP Port: {info['port']})")
        print(f"  * Path     : {info['data_dir']}")
        print(f"  * Status   : {'Available on disk' if exists else 'Not found'}")
        print()

def sync_data(source_key="edge_maruti", dest_dir=None):
    """
    Safely clone session state, history, and preferences from official browser
    to AI profile directory without locking.
    """
    if source_key not in PROFILES_DEF:
        print(f"Unknown source profile '{source_key}'")
        return False

    src_info = PROFILES_DEF[source_key]
    src_profile_path = os.path.join(src_info["data_dir"], src_info["profile_dir"])
    
    if not dest_dir:
        dest_dir = os.path.join(src_info["ai_clone_dir"], "Default")

    print(f"[*] Syncing official data from {src_info['name']} -> {dest_dir} ...")
    os.makedirs(dest_dir, exist_ok=True)

    # Core files to safely sync
    sync_files = ["Bookmarks", "History", "Preferences", "Web Data", "Favicons"]
    synced = 0
    for f in sync_files:
        src_file = os.path.join(src_profile_path, f)
        dest_file = os.path.join(dest_dir, f)
        if os.path.isfile(src_file):
            try:
                shutil.copy2(src_file, dest_file)
                synced += 1
            except Exception as e:
                print(f"  [-] Could not copy {f}: {e}")

    # Also sync Network/Cookies if available
    src_net = os.path.join(src_profile_path, "Network")
    dest_net = os.path.join(dest_dir, "Network")
    if os.path.isdir(src_net):
        os.makedirs(dest_net, exist_ok=True)
        for net_file in ["Cookies", "Cookies-journal"]:
            sf = os.path.join(src_net, net_file)
            df = os.path.join(dest_net, net_file)
            if os.path.isfile(sf):
                try:
                    shutil.copy2(sf, df)
                    synced += 1
                except Exception:
                    pass

    print(f"[✓] Successfully synced {synced} data elements from {src_info['name']}!")
    return True

def launch_profile(profile_key="edge_maruti"):
    """Launch the chosen official browser profile with CDP debugging enabled."""
    if profile_key not in PROFILES_DEF:
        print(f"Unknown profile '{profile_key}'")
        return

    p = PROFILES_DEF[profile_key]
    sync_data(profile_key, os.path.join(p["ai_clone_dir"], "Default"))

    launcher = p.get("launcher")
    if launcher and os.path.isfile(launcher):
        print(f"[*] Triggering desktop launcher: {launcher} ...")
        subprocess.Popen(["cmd.exe", "/c", launcher], shell=False)
        print(f"[✓] Spawned {p['name']} via desktop launcher on port {p['port']}!")
        return

    cmd = [
        p["exe"],
        f"--remote-debugging-port={p['port']}",
        f"--user-data-dir={p['ai_clone_dir']}",
        "--remote-allow-origins=*",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    print(f"[*] Launching {p['name']} on port {p['port']}...")
    subprocess.Popen(cmd, shell=False)
    print(f"[✓] Spawned {p['name']} with full user credentials!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "launch":
        key = sys.argv[2] if len(sys.argv) > 2 else "edge_maruti"
        launch_profile(key)
    elif len(sys.argv) > 1 and sys.argv[1] == "sync":
        key = sys.argv[2] if len(sys.argv) > 2 else "edge_maruti"
        sync_data(key)
    else:
        list_profiles()

