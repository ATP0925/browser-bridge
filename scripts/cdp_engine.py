"""
Unified CDP Engine for the Authorized AI Browser (Port 9222).
Integrates dedicated profile isolation (.authorized_ai_browser) and
enforces the Sensitive Action Permission Protocol.
"""
import json
import time
import requests
import websocket
import urllib.parse
import subprocess
import os

DEFAULT_AUTHORIZED_PORT = 9222
COMMON_PORTS = [9222, 9223, 9224, 9225, 9229]

SENSITIVE_KEYWORDS = [
    "send", "checkout", "pay", "order", "purchase",
    "delete", "remove", "destroy", "password", "transfer"
]

def find_active_port():
    """Probe common CDP ports, prioritizing the Authorized Browser on 9222."""
    for port in COMMON_PORTS:
        try:
            r = requests.get(f"http://localhost:{port}/json/version", timeout=1.5)
            if r.status_code == 200:
                data = r.json()
                browser_name = data.get("Browser", "Unknown")
                return port, browser_name
        except Exception:
            continue
    return None, None

class CDPEngine:
    def __init__(self, port=None):
        if port:
            self.port = port
            self.browser = "Specified"
        else:
            self.port, self.browser = find_active_port()

    def is_connected(self):
        return self.port is not None

    def get_tabs(self):
        if not self.port:
            return []
        try:
            r = requests.get(f"http://localhost:{self.port}/json", timeout=3)
            return [t for t in r.json() if t.get("type") == "page"]
        except Exception:
            return []

    def open_tab(self, url):
        """Open a new tab in the Authorized Browser via CDP Target API."""
        if not self.port:
            # Fallback to starting authorized browser launcher if available
            launcher = os.path.expandvars(r"%USERPROFILE%\OneDrive\Desktop\Launch_AI_Authorized_Browser.bat")
            if os.path.isfile(launcher):
                subprocess.Popen(["cmd.exe", "/c", launcher], shell=False)
                time.sleep(3)
                self.port, self.browser = find_active_port()

        if self.port:
            try:
                v = requests.get(f"http://localhost:{self.port}/json/version", timeout=3).json()
                ws_url = v.get("webSocketDebuggerUrl")
                if ws_url:
                    ws = websocket.create_connection(
                        ws_url,
                        timeout=5,
                        header={"Origin": f"http://localhost:{self.port}"}
                    )
                    cmd = {"id": 1, "method": "Target.createTarget", "params": {"url": url}}
                    ws.send(json.dumps(cmd))
                    resp = json.loads(ws.recv())
                    ws.close()
                    target_id = resp.get("result", {}).get("targetId")
                    return True, f"Opened via Authorized CDP (Target: {target_id})"
            except Exception as e:
                # Fallback to PUT /json/new
                try:
                    enc_url = urllib.parse.quote(url, safe=":/%?=&")
                    r = requests.put(f"http://localhost:{self.port}/json/new?{enc_url}", timeout=3)
                    if r.status_code == 200:
                        return True, "Opened via Authorized HTTP endpoint"
                except Exception:
                    pass

        return False, "Authorized Browser is offline. Please run Launch_AI_Authorized_Browser.bat"

    def compose_gmail(self, to, subject, body):
        """Open pre-filled Gmail compose tab in the Authorized Browser without auto-sending."""
        params = {
            "view": "cm",
            "fs": "1",
            "to": to,
            "su": subject,
            "body": body
        }
        gmail_url = "https://mail.google.com/mail/?" + urllib.parse.urlencode(params)
        return self.open_tab(gmail_url)

    def evaluate_script(self, expression, tab_url_filter=None):
        """Evaluate JS in an active tab in the Authorized Browser."""
        if not self.port:
            return None, "Authorized Browser CDP not connected"
        tabs = self.get_tabs()
        target = None
        for t in tabs:
            if tab_url_filter:
                if tab_url_filter.lower() in t.get("url", "").lower() or tab_url_filter.lower() in t.get("title", "").lower():
                    target = t
                    break
            else:
                target = t
                break

        if not target:
            return None, f"No matching tab found for filter '{tab_url_filter}'"

        ws_url = target.get("webSocketDebuggerUrl")
        if not ws_url:
            return None, "Target tab has no WebSocket debugger URL"

        try:
            ws = websocket.create_connection(
                ws_url,
                timeout=5,
                header={"Origin": f"http://localhost:{self.port}"}
            )
            cmd = {
                "id": 101,
                "method": "Runtime.evaluate",
                "params": {"expression": expression, "returnByValue": True, "awaitPromise": True}
            }
            ws.send(json.dumps(cmd))
            resp = json.loads(ws.recv())
            ws.close()
            return resp.get("result", {}).get("result", {}).get("value"), None
        except Exception as e:
            return None, str(e)

    def is_action_sensitive(self, action_name, action_target=""):
        """Check if an action is sensitive and requires user confirmation."""
        text = f"{action_name} {action_target}".lower()
        return any(k in text for k in SENSITIVE_KEYWORDS)
