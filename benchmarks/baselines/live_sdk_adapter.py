"""
Optional Live SDK Adapter for benchmarking real SaaS / local SDK backends
(Mem0, Zep, Supermemory, Graphiti) when packages and API keys are provided.
"""

from __future__ import annotations

import os


def detect_live_backends() -> dict[str, dict]:
    status = {}
    checks = [
        ("mem0", "MEM0_API_KEY", "pip install mem0ai"),
        ("zep_cloud", "ZEP_API_KEY", "pip install zep-cloud"),
        ("supermemory", "SUPERMEMORY_API_KEY", "pip install supermemory"),
        ("graphiti_core", "OPENAI_API_KEY", "pip install graphiti-core"),
    ]
    for pkg, env_key, hint in checks:
        installed = False
        try:
            __import__(pkg)
            installed = True
        except ImportError:
            pass
        has_key = bool(os.environ.get(env_key))
        status[pkg] = {
            "installed": installed,
            "env_key": env_key,
            "has_key": has_key,
            "ready": installed and has_key,
            "install_hint": hint,
        }
    return status

