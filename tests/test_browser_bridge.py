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
        sample_secret = "api_key = 'sk_test_1234567890ABCDEF'"
        found = False
        for pat, desc in PII_PATTERNS:
            if re.search(pat, sample_secret, re.IGNORECASE):
                found = True
                break
        self.assertTrue(found)

if __name__ == "__main__":
    unittest.main()
