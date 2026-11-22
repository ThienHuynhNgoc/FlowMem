"""Zep-style Dual Episodic + Entity Fact Summary Baseline."""

from __future__ import annotations

from collections import defaultdict
from .common import HybridRetriever, bpe_approx_tokens


class ZepBaseline:
    name = "Zep (Episodic + Fact Summaries)"

    def __init__(self):
        self.docs: list[str] = []
        self.retriever: HybridRetriever | None = None

    def ingest_sessions(self, sessions: list[dict]) -> None:
        entity_timeline: dict[str, list[str]] = defaultdict(list)
        episodes: list[str] = []

        for s in sessions:
            episodes.append(f"Episode {s['session_id']} ({s['date']}): {s['transcript']}")
            for f in s["facts"]:
                line = f"[{f['time']}] {f['subject']} {f['predicate']} -> {f['object']}"
                entity_timeline[f["subject"]].append(line)

        summaries = [
            f"Entity Summary ({ent}): " + " ; ".join(lines)
            for ent, lines in entity_timeline.items()
        ]
        self.docs = summaries + episodes
        self.retriever = HybridRetriever(self.docs)

    def query(self, question: str, top_k: int = 4) -> tuple[str, str, int]:
        assert self.retriever is not None
        hits = self.retriever.search(question, top_k=top_k)
        if not hits or hits[0][0] < 2.2:
            return "ABSTAIN", "", 18
        ctx = "\n".join(txt for _, _, txt in hits)
        return "ANSWERED", ctx, bpe_approx_tokens(ctx)

