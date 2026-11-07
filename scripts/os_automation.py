"""
OS-level browser automation fallback using pyautogui.
Used when CDP is not available.
"""
import time
import subprocess
import pyautogui
import pyperclip


# Safety: don't move mouse to corner to abort
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


def find_chrome_window():
    """Finds Brave, Chrome, or Edge main window PID and title via tasklist."""
    target_images = ["brave.exe", "chrome.exe", "msedge.exe"]
    for img in target_images:
        r = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {img}", "/V", "/FO", "CSV"],
            capture_output=True, text=True
        )
        for line in r.stdout.strip().split("\n"):
            if line and "N/A" not in line.split(",")[-1]:
                parts = line.strip('"').split('","')
                if len(parts) >= 2:
                    try:
                        pid = int(parts[1])
                        title = parts[-1].strip('"')
                        if title and title != "N/A":
                            return pid, title
                    except ValueError:
                        continue
    return None, None


def focus_chrome():
    """Bring Brave, Chrome, or Edge to foreground reliably using SwitchToThisWindow."""
    import os, ctypes
    user32 = ctypes.windll.user32

    # Attach to interactive user desktop
    try:
        h_desk = user32.OpenDesktopW("default", 0, False, 0x01FF)
        if h_desk:
            user32.SetThreadDesktop(h_desk)
    except Exception:
        h_desk = None

    target_pid, _ = find_chrome_window()
    if not target_pid:
        return False

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    target_hwnd = [None]

    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value == target_pid:
                target_hwnd[0] = hwnd
                return False
        return True

    cb_func = WNDENUMPROC(cb)
    if h_desk:
        user32.EnumDesktopWindows(h_desk, cb_func, 0)
    else:
        user32.EnumWindows(cb_func, 0)

    if target_hwnd[0]:
        try:
            user32.AllowSetForegroundWindow(-1)
            user32.SwitchToThisWindow(target_hwnd[0], True)
            user32.SetForegroundWindow(target_hwnd[0])
            time.sleep(0.1)
            return True
        except Exception:
            pass
    return False


def open_url_in_chrome(url):
    """Open a URL in Brave/Chrome using Ctrl+T then pasting URL."""
    import os
    if not focus_chrome():
        # Fallback: check Brave first (default for Browser Bridge), then system default
        brave_path = os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe")
        if os.path.isfile(brave_path):
            subprocess.Popen([brave_path, url])
        else:
            subprocess.Popen(["start", url], shell=True)
        time.sleep(2)
        return True

    time.sleep(0.3)
    # Open new tab
    pyautogui.hotkey("ctrl", "t")
    time.sleep(0.5)

    # Paste URL into address bar (Ctrl+L focuses it)
    pyautogui.hotkey("ctrl", "l")
    time.sleep(0.3)

    # Use clipboard to paste URL (avoids special char issues)
    pyperclip.copy(url)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.2)
    pyautogui.press("enter")
    time.sleep(1)
    return True


def type_text_in_browser(text):
    """Type text into the currently focused field in the browser."""
    focus_chrome()
    time.sleep(0.3)
    # Use clipboard for reliability
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.2)


def take_screenshot(filename="browser_screenshot.png"):
    """Take a screenshot of the screen."""
    focus_chrome()
    time.sleep(0.5)
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    return filename

