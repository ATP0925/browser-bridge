"""Centralized browser configuration for Browser Bridge."""
import os

BRAVE_PORT = 9222
CHROME_PORT = 9223
BRAVE_PROFILE = os.path.expanduser(r"~\.authorized_ai_brave")
CHROME_PROFILE = os.path.expanduser(r"~\.authorized_ai_browser") 
FALLBACK_CHROME_PROFILE = os.path.expanduser(r"~\.authorized_ai_fallback_chrome")
