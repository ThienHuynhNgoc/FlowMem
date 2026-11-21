"""Supermemory / Hybrid Vector RAG Baseline (BM25 + Vector RRF over dated chunks)."""

from __future__ import annotations

from .common import HybridRetriever, bpe_approx_tokens


class SupermemoryBaseline:
    name = "Supermemory (Hybrid RAG)"

    def __init__(self):
        self.chunks: list[str] = []
        self.dates: list[str] = []
        self.retriever: HybridRetriever | None = None

    def ingest_sessions(self, sessions: list[dict]) -> None:
        self.chunks = [f"[{s['date']} {s['session_id']}] {s['transcript']}" for s in sessions]
        self.dates = [s["date"] for s in sessions]
        self.retriever = HybridRetriever(self.chunks)

    def query(self, question: str, top_k: int = 4) -> tuple[str, str, int]:
        assert self.retriever is not None
        hits = self.retriever.search(question, top_k=top_k)
        # Abstain if strongest semantic + lexical hit is weak
        if not hits or hits[0][0] < 2.2:
            return "ABSTAIN", "", 15
        # Sort retrieved chunks chronologically so newer knowledge overrides older chunks cleanly
        selected = sorted([(self.dates[idx], txt) for _, idx, txt in hits], key=lambda x: x[0])
        ctx = "\n".join(txt for _, txt in selected)
        return "ANSWERED", ctx, bpe_approx_tokens(ctx)
