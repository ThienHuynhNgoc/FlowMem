# FlowMem v2.0 Benchmark Results (`FlowMem-LongMem-50`)

Reproducible 50-query evaluation comparing **FlowMem v2.0 Dense Diagram-Markdown (DDM)** against architectural baselines modeled on **Graphiti**, **Zep**, **Mem0**, and **Supermemory (Vector RAG)**.

## Leaderboard

| Rank | Architecture | Overall | Single-Hop | Multi-Hop | Temporal | Knowledge Update | Abstention | Avg Context Tokens |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | **FlowMem v2.0 (DDM)** | **98.0%** | 100.0% | 90.0% | 100.0% | 100.0% | 100.0% | ~63.3 tok |
| 2 | Mem0 (Flat Fact Store) | 70.0% | 100.0% | 70.0% | 20.0% | 60.0% | 100.0% | ~34.9 tok |
| 3 | Zep (Session + Facts) | 66.0% | 70.0% | 80.0% | 90.0% | 0.0% | 90.0% | ~98.1 tok |
| 4 | Supermemory (Vector RAG) | 66.0% | 80.0% | 80.0% | 90.0% | 0.0% | 80.0% | ~106.6 tok |
| 5 | Graphiti (JSON Graph) | 60.0% | 60.0% | 30.0% | 80.0% | 30.0% | 100.0% | ~480.3 tok |

## Why FlowMem DDM Wins
1. **Bi-Temporal Edges (`-->` `#valid` vs `-.->` `#superseded`):** Preserves historical lineage for temporal queries without polluting current-state knowledge updates.
2. **3-Hop Graph Traversal:** Traverses transitive dependencies (`ACME Corp -> Project Atlas -> AuthService -> Valkey 8.0`) that flat vector/fact stores miss.
3. **Ultra-Dense Token Footprint:** Mermaid syntax encodes entity + relation + timestamp + state in ~14 tokens per fact—fewer tokens than JSON triplets or prose transcripts.
4. **Confidence-Gated Abstention:** Refuses to hallucinate when seed entities do not exist in the graph.

Run yourself: `python3 benchmarks/run_benchmark.py`
