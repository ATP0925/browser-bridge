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
    """Find Chrome's main window PID and title via tasklist."""
    r = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq chrome.exe", "/V", "/FO", "CSV"],
        capture_output=True, text=True
    )
    for line in r.stdout.strip().split("\n"):
        if "Google Chrome" in line and "N/A" not in line.split(",")[-1]:
            parts = line.strip('"').split('","')
            pid = int(parts[1])
            title = parts[-1].strip('"')
            return pid, title
    return None, None


def focus_chrome():
    """Bring Chrome to the foreground using Alt+Tab fallback."""
    import ctypes
    import ctypes.wintypes as w

    user32 = ctypes.windll.user32

    # Find Chrome window handle via tasklist PID approach
    r = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq chrome.exe", "/V", "/FO", "CSV"],
        capture_output=True, text=True
    )
    target_pid = None
    for line in r.stdout.strip().split("\n"):
        if "Google Chrome" in line:
            parts = line.strip('"').split('","')
            target_pid = int(parts[1])
            break

    if target_pid:
        # Use PowerShell to activate window by PID
        ps_cmd = f"""
        Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices;
        public class Win {{ [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
        [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); }}'
        $p = Get-Process -Id {target_pid} -ErrorAction SilentlyContinue
        if ($p -and $p.MainWindowHandle -ne [IntPtr]::Zero) {{
            [Win]::ShowWindow($p.MainWindowHandle, 9)
            [Win]::SetForegroundWindow($p.MainWindowHandle)
        }}
        """
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
        time.sleep(0.5)
        return True
    return False


def open_url_in_chrome(url):
    """Open a URL in Chrome using Ctrl+T then pasting URL."""
    if not focus_chrome():
        # Fallback: use start command
        subprocess.Popen(["start", "chrome", url], shell=True)
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

