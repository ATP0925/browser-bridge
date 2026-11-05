"""
Unified CDP Engine for Microsoft Edge and Google Chrome.
Handles discovery, WebSockets, origin headers, and command execution.
"""
import json
import time
import requests
import websocket
import urllib.parse
import subprocess

COMMON_PORTS = [9222, 9223, 9224, 9225, 9229]

def find_active_port():
    """Probe common CDP ports to find an active Edge or Chrome instance."""
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
            return r.json()
        except Exception:
            return []

    def open_tab(self, url):
        """Open a new tab via CDP Target API, or fallback to Windows default browser."""
        if self.port:
            try:
                # 1. Try Target.createTarget via browser-level WebSocket
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
                    return True, f"Opened via CDP (Target: {target_id})"
            except Exception as e:
                # Fallback to PUT /json/new
                try:
                    enc_url = urllib.parse.quote(url, safe=":/%?=&")
                    r = requests.put(f"http://localhost:{self.port}/json/new?{enc_url}", timeout=3)
                    if r.status_code == 200:
                        return True, "Opened via HTTP endpoint"
                except Exception:
                    pass

        # Native OS Fallback: uses Windows default browser (Edge or Chrome) seamlessly
        try:
            subprocess.Popen(["cmd.exe", "/c", "start", "", url], shell=False)
            return True, "Opened via Windows ShellExecute (Default Browser)"
        except Exception as e:
            return False, f"Failed to open tab: {e}"

    def compose_gmail(self, to, subject, body):
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
        if not self.port:
            return None, "CDP not connected"
        tabs = self.get_tabs()
        target = None
        for t in tabs:
            if t.get("type") == "page":
                if tab_url_filter:
                    if tab_url_filter.lower() in t.get("url", "").lower():
                        target = t
                        break
                else:
                    target = t
                    break

        if not target:
            return None, "No matching page tab found"

        ws_url = target.get("webSocketDebuggerUrl")
        if not ws_url:
            return None, "Tab lacks WebSocket URL"

        try:
            ws = websocket.create_connection(
                ws_url,
                timeout=5,
                header={"Origin": f"http://localhost:{self.port}"}
            )
            cmd = {
                "id": 100,
                "method": "Runtime.evaluate",
                "params": {"expression": expression, "returnByValue": True}
            }
            ws.send(json.dumps(cmd))
            resp = json.loads(ws.recv())
            ws.close()
            return resp.get("result", {}).get("result", {}).get("value"), None
        except Exception as e:
            return None, str(e)

