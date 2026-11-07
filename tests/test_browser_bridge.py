import unittest
import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from cdp_engine import resolve_launcher_path, find_active_port
import totp_helper
from pii_guard import PII_PATTERNS
import re

class TestBrowserBridge(unittest.TestCase):
    def test_totp_rfc6238_generation(self):
        # RFC 6238 test vector secret
        secret = "JBSWY3DPEHPK3PXP"
        code = totp_helper.generate_totp(secret)
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    def test_launcher_path_resolution(self):
        path = resolve_launcher_path()
        self.assertTrue(path.endswith("Launch_AI_Authorized_Browser.bat"))

    def test_pii_patterns_match(self):
        sample_secret = "api_key = '" + "sk_test_" + "1234567890ABCDEF'"
        found = False
        for pat, desc in PII_PATTERNS:
            if re.search(pat, sample_secret, re.IGNORECASE):
                found = True
                break
        self.assertTrue(found)

    def test_profile_manager_no_raw_pii(self):
        import profile_manager
        self.assertIn("edge_default", profile_manager.PROFILES_DEF)
        self.assertIn("edge_maruti", profile_manager.PROFILES_DEF)
        # Verify no hardcoded email addresses or PII in profile_manager source code
        src = Path(profile_manager.__file__).read_text(encoding="utf-8")
        self.assertNotIn("atpadkar", src.lower())
        self.assertNotIn("pvppcoe", src.lower())

    def test_cdp_engine_fill_semantic_uses_safe_dom(self):
        import inspect
        from cdp_engine import CDPEngine
        src = inspect.getsource(CDPEngine.fill_semantic)
        self.assertNotIn("innerHTML", src)
        self.assertIn("textContent", src)

    def test_config_centralization(self):
        import config
        self.assertEqual(config.BRAVE_PORT, 9222)
        self.assertEqual(config.CHROME_PORT, 9223)
        self.assertTrue(config.BRAVE_PROFILE.endswith(".authorized_ai_brave"))
        self.assertTrue(config.CHROME_PROFILE.endswith(".authorized_ai_browser"))
        self.assertTrue(config.FALLBACK_CHROME_PROFILE.endswith(".authorized_ai_fallback_chrome"))

    def test_cdp_engine_websocket_exception_handling(self):
        from unittest.mock import patch
        import websocket
        from cdp_engine import CDPEngine

        engine = CDPEngine(port=9222)
        with patch.object(engine, "get_tabs", return_value=[{"url": "http://example.com", "webSocketDebuggerUrl": "ws://dummy"}]):
            with patch("websocket.create_connection", side_effect=websocket.WebSocketException("Connection refused")):
                ws, err = engine._get_target_ws()
                self.assertIsNone(ws)
                self.assertIn("WebSocket connection failed", err)

    def test_cdp_engine_evaluate_script_exception_details(self):
        from unittest.mock import patch, MagicMock
        from cdp_engine import CDPEngine

        engine = CDPEngine(port=9222)
        mock_ws = MagicMock()
        with patch.object(engine, "_get_target_ws", return_value=(mock_ws, {"url": "http://test"})):
            with patch.object(engine, "_cdp_call", return_value={
                "id": 1,
                "result": {
                    "result": {"type": "undefined"},
                    "exceptionDetails": {
                        "text": "Uncaught ReferenceError: foo is not defined",
                        "exception": {"description": "ReferenceError: foo is not defined"}
                    }
                }
            }):
                val, err = engine.evaluate_script("foo()")
                self.assertIsNone(val)
                self.assertIn("JavaScript error: Uncaught ReferenceError", err)

    def test_cdp_engine_null_result_safety(self):
        from unittest.mock import patch, MagicMock
        from cdp_engine import CDPEngine

        engine = CDPEngine(port=9222)
        mock_ws = MagicMock()
        # CDP response where "result" is None
        with patch.object(engine, "_get_target_ws", return_value=(mock_ws, {"url": "http://test"})):
            with patch.object(engine, "_cdp_call", return_value={"id": 1, "result": None}):
                val, err = engine.evaluate_script("1 + 1")
                self.assertIsNone(val)
                self.assertIsNone(err)

    def test_gmail_url_encoding(self):
        import urllib.parse
        to_addr = "test@example.com"
        subject = "Hello & Welcome = World"
        body = "Line 1\nLine 2 & more"
        params = urllib.parse.urlencode({
            "view": "cm", "fs": "1",
            "to": to_addr, "su": subject, "body": body
        })
        self.assertIn("su=Hello+%26+Welcome+%3D+World", params)
        self.assertIn("body=Line+1%0ALine+2+%26+more", params)

    def test_os_automation_multi_browser_detection(self):
        from os_automation import find_chrome_window, focus_chrome
        pid, title = find_chrome_window()
        self.assertTrue(pid is None or isinstance(pid, int))
        focused = focus_chrome()
        self.assertIsInstance(focused, bool)

    def test_get_chrome_user_data_dir_no_crash(self):
        from scripts.browser_bridge import get_chrome_user_data_dir
        res = get_chrome_user_data_dir()
        self.assertIsInstance(res, str)
        self.assertTrue(len(res) > 0)

if __name__ == "__main__":
    unittest.main()
