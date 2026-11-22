"""Shared tokenization, BPE-approximation counter, and Hybrid BM25+Vector retriever."""

from __future__ import annotations

import math
import re
from collections import Counter


def bpe_approx_tokens(text: str) -> int:
    """
    Approximate GPT-4 / Claude subword token count accurately in pure stdlib:
    splits words, numbers, and syntax/JSON punctuation tokens.
    """
    if not text:
        return 0
    pieces = re.findall(r"[A-Za-z0-9_]+|[^\sA-Za-z0-9_]", text)
    return max(1, int(round(len(pieces) * 0.92)))


def truncate_to_token_budget(text: str, budget: int) -> str:
    if budget <= 0 or bpe_approx_tokens(text) <= budget:
        return text
    lines = text.splitlines()
    kept = []
    used = 0
    for ln in lines:
        ltok = bpe_approx_tokens(ln)
        if used + ltok > budget:
            if not kept:
                # Truncate single long line cleanly
                approx_chars = max(40, budget * 4)
                return ln[:approx_chars]
            break
        kept.append(ln)
        used += ltok
    return "\n".join(kept)


def norm_tokens(text: str) -> list[str]:
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text).replace("_", " ").replace("-", " ")
    return [t for t in re.findall(r"[a-z0-9]+", f"{text} {expanded}".lower()) if len(t) > 1]


def char_trigrams(text: str) -> Counter:
    cleaned = re.sub(r"\s+", " ", text.lower()).strip()
    if len(cleaned) < 3:
        return Counter({cleaned: 1}) if cleaned else Counter()
    return Counter(cleaned[i : i + 3] for i in range(len(cleaned) - 2))


def cosine_sim(c1: Counter, c2: Counter) -> float:
    if not c1 or not c2:
        return 0.0
    common = set(c1.keys()) & set(c2.keys())
    if not common:
        return 0.0
    dot = sum(c1[k] * c2[k] for k in common)
    n1 = math.sqrt(sum(v * v for v in c1.values()))
    n2 = math.sqrt(sum(v * v for v in c2.values()))
    return dot / (n1 * n2) if n1 > 0 and n2 > 0 else 0.0


class HybridRetriever:
    """Pure Python Okapi BM25 + Character 3-Gram Cosine Vector RRF retriever."""

    def __init__(self, docs: list[str], k1: float = 1.5, b: float = 0.75):
        self.docs = docs
        self.k1 = k1
        self.b = b
        self.doc_toks = [norm_tokens(d) for d in docs]
        self.doc_freqs = [Counter(t) for t in self.doc_toks]
        self.doc_trigrams = [char_trigrams(d) for d in docs]
        self.n = len(docs)
        self.avg_dl = sum(len(t) for t in self.doc_toks) / max(1, self.n)
        self.df = Counter()
        for c in self.doc_freqs:
            for k in c:
                self.df[k] += 1

    def search(self, query: str, top_k: int = 4) -> list[tuple[float, int, str]]:
        q_toks = norm_tokens(query)
        q_tri = char_trigrams(query)

        bm25_scores = []
        vec_scores = []
        for idx in range(self.n):
            dl = len(self.doc_toks[idx])
            tf_map = self.doc_freqs[idx]
            bm = 0.0
            for qt in q_toks:
                tf = tf_map.get(qt, 0)
                if tf == 0:
                    continue
                idf = math.log((self.n - self.df[qt] + 0.5) / (self.df[qt] + 0.5) + 1.0)
                denom = tf + self.k1 * (1.0 - self.b + self.b * (dl / max(1.0, self.avg_dl)))
                bm += idf * ((tf * (self.k1 + 1.0)) / denom)
            bm25_scores.append((bm, idx))
            vec_scores.append((cosine_sim(q_tri, self.doc_trigrams[idx]), idx))

        bm25_rank = {idx: r for r, (_, idx) in enumerate(sorted(bm25_scores, key=lambda x: -x[0]), 1)}
        vec_rank = {idx: r for r, (_, idx) in enumerate(sorted(vec_scores, key=lambda x: -x[0]), 1)}
        bm25_map = {idx: s for s, idx in bm25_scores}
        vec_map = {idx: s for s, idx in vec_scores}

        combined = []
        for idx in range(self.n):
            # Combine RRF with raw BM25 + cosine magnitude so irrelevant queries get low absolute score
            rrf = (1.0 / (20.0 + bm25_rank[idx])) + (1.0 / (20.0 + vec_rank[idx]))
            raw_signal = bm25_map[idx] + vec_map[idx] * 2.5
            combined.append((raw_signal * (1.0 + rrf), idx, self.docs[idx]))

        combined.sort(key=lambda x: -x[0])
        return combined[:top_k]

