"""
Unified CDP Engine for the Authorized AI Browser (Port 9222).
Integrates dedicated profile isolation (.authorized_ai_browser),
Semantic ARIA accessibility querying, Hardware Input dispatching,
and enforces the Sensitive Action Permission Protocol with Intent Inheritance.
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

def resolve_launcher_path() -> str:
    """Dynamically resolves Desktop vs OneDrive/Desktop launcher location."""
    candidates = [
        os.path.expandvars(r"%USERPROFILE%\Desktop\Launch_AI_Authorized_Browser.bat"),
        os.path.expandvars(r"%USERPROFILE%\OneDrive\Desktop\Launch_AI_Authorized_Browser.bat")
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return candidates[0]

def find_active_port():
    """Probe common CDP ports, prioritizing the Authorized Browser on 9222."""
    for port in COMMON_PORTS:
        try:
            r = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=1.5)
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
            r = requests.get(f"http://127.0.0.1:{self.port}/json", timeout=3)
            return [t for t in r.json() if t.get("type") == "page"]
        except Exception:
            return []

    def open_tab(self, url):
        """Open a new tab in the Authorized Browser via CDP Target API."""
        if not self.port:
            launcher = resolve_launcher_path()
            if os.path.isfile(launcher):
                subprocess.Popen(["cmd.exe", "/c", launcher], shell=False)
                time.sleep(3)
                self.port, self.browser = find_active_port()

        if self.port:
            try:
                v = requests.get(f"http://127.0.0.1:{self.port}/json/version", timeout=3).json()
                ws_url = v.get("webSocketDebuggerUrl")
                if ws_url:
                    ws = websocket.create_connection(
                        ws_url,
                        timeout=5,
                        suppress_origin=True
                    )
                    cmd = {"id": 1, "method": "Target.createTarget", "params": {"url": url}}
                    ws.send(json.dumps(cmd))
                    resp = json.loads(ws.recv())
                    ws.close()
                    target_id = resp.get("result", {}).get("targetId")
                    return True, f"Opened via Authorized CDP (Target: {target_id})"
            except Exception:
                try:
                    enc_url = urllib.parse.quote(url, safe=":/%?=&")
                    r = requests.put(f"http://127.0.0.1:{self.port}/json/new?{enc_url}", timeout=3)
                    if r.status_code == 200:
                        return True, "Opened via Authorized HTTP endpoint"
                except Exception:
                    pass

        return False, "Authorized Browser is offline. Please run Launch_AI_Authorized_Browser.bat"

    def _get_target_ws(self, tab_url_filter=None):
        """Helper to get WebSocket connection and tab object for a filtered tab."""
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

        if not target or not target.get("webSocketDebuggerUrl"):
            return None, None

        ws = websocket.create_connection(
            target["webSocketDebuggerUrl"],
            timeout=8,
            suppress_origin=True
        )
        return ws, target

    def _cdp_call(self, ws, method, params=None):
        """Send a CDP command and wait strictly for the matching ID response."""
        cmd_id = int(time.time() * 1000) % 10000000
        msg = {"id": cmd_id, "method": method, "params": params or {}}
        ws.send(json.dumps(msg))
        deadline = time.time() + 8
        while time.time() < deadline:
            res = json.loads(ws.recv())
            if res.get("id") == cmd_id:
                return res
        raise TimeoutError(f"CDP command {method} timed out waiting for ID {cmd_id}")

    def capture_screenshot(self, output_path: str = "screenshot.png", tab_url_filter: str = None):
        """Captures active page screenshot via CDP Page.captureScreenshot."""
        import base64
        ws, target = self._get_target_ws(tab_url_filter)
        if not ws:
            return False, "No active tab found"
        try:
            res = self._cdp_call(ws, "Page.captureScreenshot", {"format": "png"})
            ws.close()
            data = res.get("result", {}).get("data")
            if data:
                with open(output_path, "wb") as f:
                    f.write(base64.b64decode(data))
                return True, f"Screenshot saved to {output_path}"
            return False, "No image data returned from CDP"
        except Exception as e:
            return False, str(e)

    def evaluate_script(self, expression, tab_url_filter=None):
        """Evaluate JS in an active tab with robust response ID matching."""
        if not self.port:
            return None, "Authorized Browser CDP not connected"
        ws, target = self._get_target_ws(tab_url_filter)
        if not ws:
            return None, f"No matching tab found for filter '{tab_url_filter}'"

        try:
            res = self._cdp_call(ws, "Runtime.evaluate", {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": True
            })
            ws.close()
            return res.get("result", {}).get("result", {}).get("value"), None
        except Exception as e:
            if ws:
                ws.close()
            return None, str(e)

    def bring_to_front(self, tab_url_filter=None):
        """Bring the specified tab into active view."""
        ws, target = self._get_target_ws(tab_url_filter)
        if not ws:
            return False
        try:
            self._cdp_call(ws, "Page.bringToFront")
            ws.close()
            return True
        except Exception:
            if ws:
                ws.close()
            return False

    def send_hardware_key(self, key, code="KeyF", windows_virtual_key_code=70, tab_url_filter=None):
        """
        Dispatch a genuine hardware keyboard event at the browser engine level.
        Guarantees event.isTrusted === true.
        """
        ws, target = self._get_target_ws(tab_url_filter)
        if not ws:
            return False, "Target tab not found"

        try:
            self._cdp_call(ws, "Input.dispatchKeyEvent", {
                "type": "keyDown",
                "key": key,
                "code": code,
                "windowsVirtualKeyCode": windows_virtual_key_code
            })
            self._cdp_call(ws, "Input.dispatchKeyEvent", {
                "type": "keyUp",
                "key": key,
                "code": code,
                "windowsVirtualKeyCode": windows_virtual_key_code
            })
            ws.close()
            return True, f"Dispatched key '{key}' ({code})"
        except Exception as e:
            if ws:
                ws.close()
            return False, str(e)

    def click_semantic(self, name_or_label, role=None, tab_url_filter=None):
        """
        Click an element based on semantic accessibility properties (ARIA, text)
        instead of fragile CSS class names.
        """
        js = f"""
        (() => {{
            const query = {json.dumps(name_or_label.lower())};
            const role = {json.dumps((role or '').lower())};
            
            // Search order:
            // 1. role + aria-label
            // 2. button/input matching aria-label
            // 3. visible text content
            const allElements = Array.from(document.querySelectorAll('button, a, input[type="submit"], input[type="button"], [role="button"], div, span'));
            let matched = null;

            for (const el of allElements) {{
                const elRole = (el.getAttribute('role') || el.tagName).toLowerCase();
                const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                const text = (el.innerText || el.value || '').trim().toLowerCase();

                if (role && elRole !== role) continue;

                if (aria.includes(query) || text === query || (text.includes(query) && text.length < 50)) {{
                    matched = el;
                    break;
                }}
            }}

            if (matched) {{
                matched.focus();
                matched.dispatchEvent(new MouseEvent('mousedown', {{bubbles: true, cancelable: true, view: window}}));
                matched.dispatchEvent(new MouseEvent('mouseup', {{bubbles: true, cancelable: true, view: window}}));
                matched.click();
                return {{ success: true, tag: matched.tagName, aria: matched.getAttribute('aria-label') || matched.innerText }};
            }}
            return {{ success: false, error: 'Element not found by semantic search' }};
        }})()
        """
        res, err = self.evaluate_script(js, tab_url_filter)
        return res or {"success": False, "error": err}

    def fill_semantic(self, label_pattern, value, tab_url_filter=None, press_enter=True):
        """
        Fill an input element found by semantic label, placeholder, or name.
        """
        js = f"""
        (() => {{
            const query = {json.dumps(label_pattern.lower())};
            const val = {json.dumps(value)};
            const doEnter = {json.dumps(press_enter)};

            const inputs = Array.from(document.querySelectorAll('input, textarea, div[role="textbox"]'));
            let target = null;

            for (const i of inputs) {{
                const aria = (i.getAttribute('aria-label') || '').toLowerCase();
                const name = (i.getAttribute('name') || '').toLowerCase();
                const placeholder = (i.getAttribute('placeholder') || '').toLowerCase();
                const id = (i.id || '').toLowerCase();

                if (aria.includes(query) || name.includes(query) || placeholder.includes(query) || id.includes(query)) {{
                    target = i;
                    break;
                }}
            }}

            if (target) {{
                target.focus();
                if (target.tagName === 'DIV') {{
                    target.textContent = val;
                }} else {{
                    const proto = target instanceof HTMLTextAreaElement ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
                    const descriptor = Object.getOwnPropertyDescriptor(proto, 'value');
                    if (descriptor && descriptor.set) {{
                        descriptor.set.call(target, val);
                    }} else {{
                        target.value = val;
                    }}
                }}
                target.dispatchEvent(new Event('input', {{bubbles: true}}));
                target.dispatchEvent(new Event('change', {{bubbles: true}}));

                if (doEnter) {{
                    target.dispatchEvent(new KeyboardEvent('keydown', {{bubbles: true, keyCode: 13, which: 13, key: 'Enter'}}));
                }}
                return {{ success: true, tag: target.tagName, filled: val }};
            }}
            return {{ success: false, error: 'Input not found by semantic search' }};
        }})()
        """
        res, err = self.evaluate_script(js, tab_url_filter)
        return res or {"success": False, "error": err}

    def detect_captcha(self, tab_url_filter=None):
        """Scan the page for anti-bot challenges (Turnstile, reCAPTCHA, hCaptcha)."""
        js = """
        (() => {
            const iframes = Array.from(document.querySelectorAll('iframe')).map(f => f.src.toLowerCase());
            const hasTurnstile = iframes.some(s => s.includes('turnstile') || s.includes('challenges.cloudflare.com'));
            const hasRecaptcha = iframes.some(s => s.includes('recaptcha') || s.includes('google.com/recaptcha'));
            const hasHcaptcha = iframes.some(s => s.includes('hcaptcha'));
            const hasArkose = iframes.some(s => s.includes('arkoselabs') || s.includes('funcaptcha'));

            const foundType = hasTurnstile ? 'Cloudflare Turnstile'
                            : hasRecaptcha ? 'Google reCAPTCHA'
                            : hasHcaptcha ? 'hCaptcha'
                            : hasArkose ? 'Arkose Labs FunCaptcha'
                            : null;

            return {
                detected: !!foundType,
                type: foundType,
                iframeCount: iframes.length
            };
        })()
        """
        res, err = self.evaluate_script(js, tab_url_filter)
        return res or {"detected": False, "error": err}

    def is_action_sensitive(self, action_name, action_target=""):
        """Check if an action is sensitive and requires user confirmation."""
        text = f"{action_name} {action_target}".lower()
        return any(k in text for k in SENSITIVE_KEYWORDS)
