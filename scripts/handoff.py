"""
Zero-Friction Human Handoff Engine for Browser Bridge.
Provides clean visual and audio handoff when an interactive barrier
(CAPTCHA challenge, Payment OTP/QR, Passkey tap) requires human touch.
"""
import time
import os
import subprocess
from cdp_engine import CDPEngine

def trigger_audio_alert(message: str):
    """Trigger voice alert using Live Voice Responder or system speech fallback."""
    voice_script = os.path.expandvars(r"C:\Users\atpad\.gemini\config\skills\live-voice-responder\neural_speak.py")
    if os.path.isfile(voice_script):
        try:
            subprocess.Popen(["python", voice_script, message])
            return
        except Exception:
            pass
    # Windows native SAPI fallback
    try:
        ps_code = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{message}")'
        subprocess.Popen(["powershell", "-Command", ps_code])
    except Exception:
        print(f"\a[AUDIO ALERT]: {message}")

def execute_handoff_checkpoint(engine: CDPEngine, reason: str = "Interactive checkpoint detected", tab_filter=None, timeout_sec: int = 45) -> bool:
    """
    Bring tab into view, alert the user via voice, and wait for the challenge to clear.
    """
    print(f"\n=======================================================")
    print(f"[!] HUMAN-IN-THE-LOOP CHECKPOINT: {reason}")
    print(f"=======================================================")

    # 1. Bring tab to front
    engine.bring_to_front(tab_filter)

    # 2. Audio Alert
    trigger_audio_alert("Bhai, screen par checkpoint aaya hai. Ek second ke liye verify kardo.")

    # 3. Wait for clearance
    print(f"[*] Waiting for user action (Timeout: {timeout_sec}s)...")
    start = time.time()
    while time.time() - start < timeout_sec:
        time.sleep(2)
        captcha_status = engine.detect_captcha(tab_filter)
        if not captcha_status.get("detected"):
            print("[✓] Checkpoint cleared! Resuming autonomous workflow...")
            trigger_audio_alert("Shukriya, resume kar raha hu.")
            return True

    print("[!] Handoff timed out.")
    return False

if __name__ == "__main__":
    eng = CDPEngine()
    if eng.is_connected():
        status = eng.detect_captcha()
        print("Initial CAPTCHA Scan:", status)
        if status.get("detected"):
            execute_handoff_checkpoint(eng, f"Detected {status.get('type')}")
        else:
            print("No active challenge detected on current tab.")
    else:
        print("Authorized Browser not running.")

