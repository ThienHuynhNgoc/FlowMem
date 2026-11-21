"""Mem0-style Atomic Fact Store Baseline (ADD/UPDATE overwrites prior facts + 2-stage retrieval)."""

from __future__ import annotations

from .common import HybridRetriever, bpe_approx_tokens, norm_tokens


class Mem0Baseline:
    name = "Mem0 (Atomic Fact Store)"

    def __init__(self):
        self.store: dict[tuple[str, str], dict] = {}
        self.docs: list[str] = []
        self.facts: list[dict] = []
        self.retriever: HybridRetriever | None = None

    def ingest_sessions(self, sessions: list[dict]) -> None:
        # Mem0 extracts atomic facts and performs ADD / UPDATE (overwriting stale values in place)
        for s in sessions:
            for f in s["facts"]:
                key = (f["subject"], f["predicate"])
                self.store[key] = {
                    "subject": f["subject"],
                    "predicate": f["predicate"],
                    "object": f["object"],
                    "updated_at": f["time"],
                }
        self.facts = list(self.store.values())
        self.docs = [f"{r['subject']} {r['predicate'].replace('_', ' ')} {r['object']}" for r in self.facts]
        self.retriever = HybridRetriever(self.docs)

    def query(self, question: str, top_k: int = 5) -> tuple[str, str, int]:
        assert self.retriever is not None
        hits = self.retriever.search(question, top_k=top_k)
        if not hits or hits[0][0] < 2.1:
            return "ABSTAIN", "", 15

        # 2-stage entity expansion from top-2 matched facts (gives Mem0 fair multi-hop shot)
        selected_indices = [idx for _, idx, _ in hits[:3]]
        seed_entities = set()
        for idx in selected_indices:
            seed_entities.add(self.facts[idx]["subject"])
            seed_entities.add(self.facts[idx]["object"])

        q_toks = set(norm_tokens(question))
        for idx, fact in enumerate(self.facts):
            if idx in selected_indices:
                continue
            if fact["subject"] in seed_entities or fact["object"] in seed_entities:
                ftoks = set(norm_tokens(self.docs[idx]))
                if q_toks & ftoks:
                    selected_indices.append(idx)
            if len(selected_indices) >= 6:
                break

        ctx = "\n".join(f"- {self.docs[i]}" for i in selected_indices)
        return "ANSWERED", ctx, bpe_approx_tokens(ctx)
