#!/usr/bin/env python3
"""
Autonomous Decision Engine & Persona Resolver
Empowers the AI Agent to make high-fidelity, autonomous decisions based on
the user's hardware constraints, multi-account routing, git profiles, and project ecosystem.
"""

import os
import sys
import json
import psutil
import subprocess

PROFILE_PATH = r"C:\Users\atpad\.gemini\antigravity\brain\c84b9177-a701-4dd4-8e6b-9175831b4120\scratch\user_developer_profile.json"

class DecisionEngine:
    def __init__(self):
        self.profile = self._load_profile()
        self.identities = {
            "college": {
                "name": "Pratik Atpadkar",
                "email": "vu4f2526072@pvppcoe.ac.in",
                "institution": "PVPPCOE Mumbai",
                "browser": "Chrome",
                "cdp_port": 9222,
                "preferred_domains": ["acadflow.dpdns.org", "mahadbt.maharashtra.gov.in", "classroom.google.com"]
            },
            "primary_dev": {
                "name": "ATP0925",
                "email": "atpadkarpratik00925@gmail.com",
                "browser": "Chrome",
                "cdp_port": 9222,
                "preferred_domains": ["github.com", "vercel.com", "firebase.google.com", "crunchyroll.com"]
            },
            "secondary_personal": {
                "name": "ATP0925",
                "email": "atpadkarmaruti@gmail.com",
                "browser": "Edge",
                "cdp_port": 9225,
                "preferred_domains": ["onedrive.live.com", "microsoft.com", "outlook.live.com"]
            },
            "research_brave": {
                "name": "ATP0925",
                "browser": "Brave",
                "cdp_port": 9226,
                "preferred_domains": ["cloudflare.com", "duckduckgo.com"]
            }
        }

    def _load_profile(self):
        if os.path.exists(PROFILE_PATH):
            try:
                with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def get_hardware_safety_check(self):
        """
        Check memory and CPU headroom to autonomously choose between
        lightweight execution vs warning before running heavy compute.
        """
        mem = psutil.virtual_memory()
        available_gb = mem.available / (1024 ** 3)
        total_gb = mem.total / (1024 ** 3)
        cpu_percent = psutil.cpu_percent(interval=0.1)

        decision = {
            "total_ram_gb": round(total_gb, 2),
            "available_ram_gb": round(available_gb, 2),
            "memory_usage_pct": mem.percent,
            "cpu_usage_pct": cpu_percent,
            "can_run_heavy_local_model": available_gb >= 5.0,
            "preferred_ai_strategy": "Cloud/API" if available_gb < 4.0 else "Local GGUF Hybrid",
            "recommendation": "Use cloud APIs (Gemini/Groq/OpenAI) to preserve user desktop responsiveness" if available_gb < 3.0 else "System healthy for lightweight local tasks"
        }
        return decision

    def resolve_browser_route(self, url_or_domain):
        """
        Autonomously selects the exact browser, port, and identity for any domain.
        """
        target = url_or_domain.lower()
        for role, data in self.identities.items():
            for dom in data.get("preferred_domains", []):
                if dom in target:
                    return {
                        "role": role,
                        "browser": data["browser"],
                        "cdp_port": data["cdp_port"],
                        "email": data.get("email", ""),
                        "reason": f"Domain {dom} matches established user workflow for {role}"
                    }
        # Default fallback
        return {
            "role": "primary_dev",
            "browser": "Chrome",
            "cdp_port": 9222,
            "email": "atpadkarpratik00925@gmail.com",
            "reason": "Default to primary developer Chrome environment"
        }

    def resolve_git_identity(self, project_dir=None):
        """
        Returns appropriate git committer credentials.
        """
        if project_dir and "campusnotify" in str(project_dir).lower():
            return {
                "name": "ATP0925",
                "email": "atpadkarmaruti@gmail.com",
                "branch_default": "main",
                "commit_convention": "Conventional Commits (feat, fix, docs, chore)"
            }
        return {
            "name": "ATP0925",
            "email": "atpadkarmaruti@gmail.com",
            "branch_default": "main",
            "commit_convention": "Conventional Commits (feat, fix, docs, chore)"
        }

    def resolve_project_context(self, project_name):
        """
        Look up scratch projects or repositories by name.
        """
        scratch_base = r"C:\Users\atpad\.gemini\antigravity\scratch"
        target_path = os.path.join(scratch_base, project_name)
        if os.path.exists(target_path):
            files = os.listdir(target_path)[:15]
            return {
                "found": True,
                "name": project_name,
                "path": target_path,
                "sample_files": files
            }
        return {"found": False, "query": project_name}

if __name__ == "__main__":
    engine = DecisionEngine()
    print("=== AUTONOMOUS DECISION ENGINE STATUS ===")
    hw = engine.get_hardware_safety_check()
    print(f"RAM: {hw['available_ram_gb']} GB available / {hw['total_ram_gb']} GB total ({hw['memory_usage_pct']}% used)")
    print(f"Compute Strategy: {hw['preferred_ai_strategy']} ({hw['recommendation']})")
    print("\n--- Domain Routing Examples ---")
    for d in ["acadflow.dpdns.org", "github.com", "onedrive.live.com", "crunchyroll.com"]:
        r = engine.resolve_browser_route(d)
        print(f"Domain: {d:25} -> Browser: {r['browser']} (Port {r['cdp_port']}) | Account: {r.get('email')}")
