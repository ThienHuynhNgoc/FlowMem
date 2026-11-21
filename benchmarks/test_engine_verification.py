#!/usr/bin/env python3
"""
FlowMem v2.0 — test_engine_verification.py
Deterministic unit and integration tests for `scripts/python/memory_engine.py`.
Run: python3 benchmarks/test_engine_verification.py -v
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts", "python"))

import memory_engine as fm  # noqa: E402


class TestMemoryEngine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.gpath = os.path.join(self.tmp.name, "test_memory.mmd")

    def tearDown(self):
        self.tmp.cleanup()

    def test_01_valid_mermaid_header_created(self):
        fm.ingest_fact(self.gpath, "CoreAPI", "uses_db", "SQLite", "2026-01-01")
        with open(self.gpath, "r", encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("%% FlowMem |", text)
        self.assertIn("flowchart LR", text)
        self.assertIn("#valid", text)

    def test_02_conflict_auto_supersedes(self):
        fm.ingest_fact(self.gpath, "CoreAPI", "uses_db", "SQLite", "2026-01-01")
        res = fm.ingest_fact(self.gpath, "CoreAPI", "uses_db", "PostgreSQL", "2026-06-15")
        self.assertEqual(res["superseded_previous"], 1)
        _, edges = fm.load_mmd_graph([self.gpath])
        states = {e["dst"]: e["state"] for e in edges}
        self.assertEqual(states["SQLite"], "superseded")
        self.assertEqual(states["PostgreSQL"], "valid")

    def test_03_no_supersede_preserves_multi_valued(self):
        fm.ingest_fact(self.gpath, "WebApp", "depends_on", "Gateway", "2026-01-01", supersede_existing=False)
        res = fm.ingest_fact(self.gpath, "WebApp", "depends_on", "Mailer", "2026-01-02", supersede_existing=False)
        self.assertEqual(res["superseded_previous"], 0)
        _, edges = fm.load_mmd_graph([self.gpath])
        self.assertTrue(all(e["state"] == "valid" for e in edges))

    def test_04_single_hop_current_excludes_superseded(self):
        fm.ingest_fact(self.gpath, "PaymentSvc", "uses_cache", "Memcached", "2025-01-01")
        fm.ingest_fact(self.gpath, "PaymentSvc", "uses_cache", "Dragonfly", "2026-02-01")
        res = fm.query_graph([self.gpath], "What cache does PaymentSvc currently use?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("Dragonfly", res["subgraph_mmd"])
        self.assertNotIn("Memcached", res["subgraph_mmd"])

    def test_05_temporal_query_includes_superseded_history(self):
        fm.ingest_fact(self.gpath, "PaymentSvc", "uses_cache", "Memcached", "2025-01-01")
        fm.ingest_fact(self.gpath, "PaymentSvc", "uses_cache", "Dragonfly", "2026-02-01")
        res = fm.query_graph([self.gpath], "What cache did PaymentSvc use before Dragonfly?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertTrue(res["include_history"])
        self.assertIn("Memcached", res["subgraph_mmd"])
        self.assertIn("#superseded", res["subgraph_mmd"])

    def test_06_three_hop_bridge_chain(self):
        fm.ingest_fact(self.gpath, "ClientZ", "subscribes_to", "PlatformX", "2026-01-01", supersede_existing=False)
        fm.ingest_fact(self.gpath, "PlatformX", "calls", "IdentityHub", "2026-01-01", supersede_existing=False)
        fm.ingest_fact(self.gpath, "IdentityHub", "uses_db", "CockroachDB", "2026-01-01", supersede_existing=False)
        res = fm.query_graph([self.gpath], "What database backs IdentityHub used by ClientZ's platform?", hops=3)
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("CockroachDB", res["subgraph_mmd"])

    def test_07_abstains_on_unknown_entity(self):
        fm.ingest_fact(self.gpath, "OrderSvc", "written_in", "Go", "2026-01-01")
        res = fm.query_graph([self.gpath], "What database does UnknownPhantomService use?")
        self.assertEqual(res["status"], "ABSTAIN")

    def test_08_camelcase_splitting_matches_generic_query(self):
        fm.ingest_fact(self.gpath, "OrderSvc", "search_via", "SearchRouter", "2026-01-01")
        fm.ingest_fact(self.gpath, "SearchRouter", "written_in", "Zig", "2026-01-01")
        res = fm.query_graph([self.gpath], "What language is the search router written in?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("Zig", res["subgraph_mmd"])

    def test_09_compact_node_declaration_dedup(self):
        fm.ingest_fact(self.gpath, "AlphaService", "uses_db", "MySQL", "2026-01-01", supersede_existing=False)
        fm.ingest_fact(self.gpath, "AlphaService", "runs_on", "Linux", "2026-01-01", supersede_existing=False)
        res = fm.query_graph([self.gpath], "What does AlphaService use and run on?")
        self.assertEqual(res["subgraph_mmd"].count('["AlphaService"]'), 1)

    def test_10_ingest_text_svo_extraction(self):
        facts = fm.extract_facts_from_text("WorkerNode migrated from RabbitMQ to NATS JetStream.")
        self.assertEqual(len(facts), 1)
        subj, pred, obj, sup = facts[0]
        self.assertEqual(subj, "WorkerNode")
        self.assertEqual(obj, "NATS JetStream")
        self.assertTrue(sup)


if __name__ == "__main__":
    unittest.main(verbosity=2)
