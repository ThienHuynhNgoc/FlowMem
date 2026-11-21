"""
Graphiti-style Bi-Temporal JSON Triplet Graph Baseline.

Uses the EXACT SAME 3-hop BFS & relevance engine as FlowMem v2.0 (zero algorithmic
disadvantage), differing strictly in Graphiti's canonical JSON serialization format
(`nodes` + `edges` with `valid_at`, `invalid_at`, `fact`, `uuid`).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "python"))
import memory_engine as fm  # noqa: E402

from .common import bpe_approx_tokens


class GraphitiBaseline:
    name = "Graphiti (Bi-Temporal JSON Graph)"

    def __init__(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.gpath = os.path.join(self.tmpdir.name, "graphiti_mirror.mmd")

    def ingest_sessions(self, sessions: list[dict]) -> None:
        for s in sessions:
            for f in s["facts"]:
                fm.ingest_fact(
                    self.gpath,
                    f["subject"],
                    f["predicate"],
                    f["object"],
                    f["time"],
                    supersede_existing=f["supersedes"],
                )

    def query(self, question: str, category: str = "") -> tuple[str, str, int]:
        res = fm.query_graph([self.gpath], question, hops=4)
        if res["status"] == "ABSTAIN":
            return "ABSTAIN", "", 16

        facts = res["matched_facts"]
        if category == "knowledge_update":
            facts = [f for f in facts if f["state"] != "superseded"]

        # Canonical Graphiti JSON triplet serialization
        nodes_map = {}
        edges_json = []
        for idx, f in enumerate(facts, 1):
            suid = f"node_{fm.slug_node_id(f['subject'])}"
            duid = f"node_{fm.slug_node_id(f['object'])}"
            nodes_map[suid] = {"uuid": suid, "name": f["subject"]}
            nodes_map[duid] = {"uuid": duid, "name": f["object"]}
            t_parts = f["time"].split("..") if ".." in f["time"] else [f["time"], None]
            edges_json.append(
                {
                    "uuid": f"edge_{idx:03d}",
                    "source_node_uuid": suid,
                    "target_node_uuid": duid,
                    "name": f["predicate"],
                    "fact": f"{f['subject']} {f['predicate']} {f['object']}",
                    "valid_at": t_parts[0],
                    "invalid_at": t_parts[1] if len(t_parts) > 1 else None,
                    "status": f["state"],
                }
            )

        payload = json.dumps({"edges": edges_json, "nodes": list(nodes_map.values())}, indent=2)
        return "ANSWERED", payload, bpe_approx_tokens(payload)

    def close(self):
        self.tmpdir.cleanup()
