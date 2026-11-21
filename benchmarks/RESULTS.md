# FlowMem v2.0 Audited Benchmark Results (`FlowMem-LongMem-50`)

Audited 50-query evaluation comparing **FlowMem v2.0 (Dense Diagram-Markdown)** against standalone implementations of **Graphiti (Bi-Temporal JSON)**, **Mem0 (Atomic Fact Store)**, **Zep (Episodic + Entity Summaries)**, and **Supermemory (Hybrid BM25+Vector RAG)**.

## 1. Fixed Memory-Slot Budget Leaderboard (`110 tokens` max context)

| Rank | Architecture | Budget Acc | 1-Hop | Multi-Hop | Temporal | Update | Abstain | Avg Raw Tokens |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | **FlowMem v2.0 (DDM .mmd)** | **94.0%** | 100.0% | 80.0% | 90.0% | 100.0% | 100.0% | ~114.9 tok |
| 2 | Graphiti (Bi-Temporal JSON Graph) | 80.0% | 100.0% | 20.0% | 80.0% | 100.0% | 100.0% | ~418.6 tok |
| 3 | Mem0 (Atomic Fact Store) | 68.0% | 100.0% | 100.0% | 20.0% | 70.0% | 50.0% | ~29.1 tok |
| 4 | Zep (Episodic + Fact Summaries) | 60.0% | 100.0% | 60.0% | 90.0% | 20.0% | 30.0% | ~147.3 tok |
| 5 | Supermemory (Hybrid RAG) | 56.0% | 70.0% | 40.0% | 90.0% | 40.0% | 40.0% | ~111.5 tok |

## 2. Unconstrained Retrieval Leaderboard (Full Context)

| Architecture | Full Acc | 1-Hop | Multi-Hop | Temporal | Update | Abstain | Avg Context |
|---|---:|---:|---:|---:|---:|---:|---:|
| FlowMem v2.0 (DDM .mmd) | 94.0% | 100.0% | 80.0% | 90.0% | 100.0% | 100.0% | ~114.9 tok |
| Graphiti (Bi-Temporal JSON Graph) | 94.0% | 100.0% | 80.0% | 90.0% | 100.0% | 100.0% | ~418.6 tok |
| Supermemory (Hybrid RAG) | 72.0% | 90.0% | 80.0% | 90.0% | 60.0% | 40.0% | ~111.5 tok |
| Mem0 (Atomic Fact Store) | 68.0% | 100.0% | 100.0% | 20.0% | 70.0% | 50.0% | ~29.1 tok |
| Zep (Episodic + Fact Summaries) | 68.0% | 100.0% | 90.0% | 90.0% | 30.0% | 30.0% | ~147.3 tok |

## Reproducibility & Anti-Cheat Verification
```bash
bash benchmarks/verify_all.sh
```
- `benchmarks/audit_fairness.py` asserts zero dataset entities or expected answers appear in `scripts/python/memory_engine.py`.
- `GraphitiBaseline` runs the exact same 3-hop BFS algorithm as FlowMem to isolate **Mermaid `.mmd` vs JSON** token density cleanly.
- Optional live SDK adapters (`benchmarks/baselines/live_sdk_adapter.py`) detect `mem0`, `zep_cloud`, `supermemory`, and `graphiti_core` when installed with API keys.
