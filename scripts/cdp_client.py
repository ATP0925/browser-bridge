"""
Lightweight CDP (Chrome DevTools Protocol) client.
Connects to Chrome via WebSocket and executes commands.
"""
import json
import time
import requests
import websocket
import threading


class CDPClient:
    """Connect to Chrome via CDP WebSocket."""

    def __init__(self, host="localhost", port=9222):
        self.host = host
        self.port = port
        self.ws = None
        self._msg_id = 0
        self._responses = {}
        self._lock = threading.Lock()

    def connect(self, target_url=None):
        """Connect to a Chrome tab. If target_url given, find that tab."""
        endpoint = f"http://{self.host}:{self.port}/json"
        try:
            tabs = requests.get(endpoint, timeout=5).json()
        except Exception as e:
            raise ConnectionError(f"Cannot reach Chrome CDP at {self.host}:{self.port}: {e}")

        target = None
        if target_url:
            for tab in tabs:
                if target_url.lower() in tab.get("url", "").lower():
                    target = tab
                    break
        if not target:
            # Pick first page-type target
            for tab in tabs:
                if tab.get("type") == "page":
                    target = tab
                    break
        if not target:
            raise RuntimeError("No suitable Chrome tab found")

        ws_url = target.get("webSocketDebuggerUrl")
        if not ws_url:
            raise RuntimeError(f"Tab has no WebSocket URL: {target.get('url')}")

        self.ws = websocket.create_connection(ws_url, timeout=10)
        return target

    def send(self, method, params=None):
        """Send a CDP command and wait for response."""
        with self._lock:
            self._msg_id += 1
            msg_id = self._msg_id

        msg = {"id": msg_id, "method": method}
        if params:
            msg["params"] = params
        self.ws.send(json.dumps(msg))

        # Wait for matching response
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                raw = self.ws.recv()
                data = json.loads(raw)
                if data.get("id") == msg_id:
                    if "error" in data:
                        raise RuntimeError(f"CDP error: {data['error']}")
                    return data.get("result", {})
            except websocket.WebSocketTimeoutException:
                continue
        raise TimeoutError(f"CDP command {method} timed out")

    def navigate(self, url):
        """Navigate current tab to URL."""
        return self.send("Page.navigate", {"url": url})

    def evaluate(self, expression):
        """Evaluate JavaScript in the page."""
        result = self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
        })
        return result.get("result", {}).get("value")

    def new_tab(self, url="about:blank"):
        """Open a new tab with given URL."""
        return self.send("Target.createTarget", {"url": url})

    def get_tabs(self):
        """List all open tabs."""
        endpoint = f"http://{self.host}:{self.port}/json"
        return requests.get(endpoint, timeout=5).json()

    def close(self):
        """Close WebSocket connection."""
        if self.ws:
            self.ws.close()
            self.ws = None


def is_cdp_available(host="localhost", port=9222):
    """Check if Chrome CDP is reachable."""
    try:
        r = requests.get(f"http://{host}:{port}/json/version", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def find_cdp_port():
    """Try common CDP ports."""
    for port in [9222, 9223, 9224, 9225, 9229]:
        if is_cdp_available(port=port):
            return port
    return None

