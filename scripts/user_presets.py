"""
User Digital-Twin Workflow Presets.
Enables instant autonomous execution of user's core everyday tasks:
- Academics (Acadflow, Mumbai University Samarth)
- MahaDBT Scholarship tracking
- CampusNotify (Vercel & Firebase App)
- Anime & Media streaming (Crunchyroll)
"""
import sys
import os
import argparse
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from cdp_engine import CDPEngine

PRESET_URLS = {
    "acadflow": "http://acadflow.dpdns.org",
    "samarth": "https://mu.samarth.edu.in",
    "mahadbt": "https://mahadbt2.maharashtra.gov.in",
    "campusnotify": "https://campusnotify-tau.vercel.app",
    "firebase": "https://console.firebase.google.com",
    "github": "https://github.com/ATP0925",
    "figma": "https://www.figma.com/files",
    "crunchyroll": "https://www.crunchyroll.com/watch/GE00350809JAJP/destroy-the-miniature-garden---escape-block-kingdom"
}

def run_preset(name, fullscreen=False):
    eng = CDPEngine()
    if not eng.is_connected():
        print("[!] Authorized Browser is offline. Triggering launch...")
        launcher = os.path.expandvars(r"%USERPROFILE%\OneDrive\Desktop\Launch_AI_Authorized_Browser.bat")
        if os.path.isfile(launcher):
            os.system(f'start "" "{launcher}"')
            time.sleep(3)
            eng = CDPEngine()

    url = PRESET_URLS.get(name.lower())
    if not url:
        print(f"[!] Unknown preset '{name}'. Available: {list(PRESET_URLS.keys())}")
        return

    print(f"[*] Launching Preset '{name}' -> {url}")
    eng.open_tab(url)
    time.sleep(2)

    if fullscreen:
        print("[*] Engaging Full Screen via CDP hardware key...")
        eng.send_hardware_key("f", code="KeyF", windows_virtual_key_code=70, tab_url_filter=name)

def main():
    parser = argparse.ArgumentParser(description="User Digital-Twin Workflow Presets")
    parser.add_argument("preset", choices=list(PRESET_URLS.keys()), help="Target workflow preset")
    parser.add_argument("--fullscreen", action="store_true", help="Toggle full screen on launch")
    args = parser.parse_args()

    run_preset(args.preset, fullscreen=args.fullscreen)

if __name__ == "__main__":
    main()

