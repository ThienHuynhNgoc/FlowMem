# FlowMem v2.0 Live-LLM Benchmark Results (`claude` + `agy`, 110-Token Budget, n=25)

Genuine end-to-end LLM evaluations executed live via `claude -p` (`haiku`, `sonnet`) and `agy -p` (`gemini-3.8-flash-low`, `gpt-oss-120b-medium`).

| Rank | Model + Memory System | Accuracy | 1-Hop | Multi-Hop | Temporal | Update | Abstain | Avg Raw Tok | Avg Latency |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | **Claude Haiku + FlowMem v2.0 (DDM)** | **100.0%** | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | ~95.0 tok | 0.77s |
| 2 | **Gemini 3.8 Flash Low + FlowMem v2.0** | **100.0%** | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | ~95.0 tok | 2.63s |
| 3 | **GPT-OSS 120B + FlowMem v2.0** | **100.0%** | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | ~95.0 tok | 2.78s |
| 4 | **Claude Sonnet + FlowMem v2.0 (DDM)** | **100.0%** | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | ~95.0 tok | 1.48s |
| 5 | Claude Haiku + Zep (Summaries) | 80.0% | 100.0% | 20.0% | 80.0% | 100.0% | 100.0% | ~139.0 tok | 0.81s |
| 6 | Claude Sonnet + Graphiti (JSON) | 76.0% | 100.0% | 0.0% | 80.0% | 100.0% | 100.0% | ~417.4 tok | 1.52s |
| 7 | Claude Haiku + Mem0 (Atomic) | 72.0% | 100.0% | 60.0% | 0.0% | 100.0% | 100.0% | ~28.8 tok | 0.81s |
| 8 | Claude Haiku + Supermemory (RAG) | 68.0% | 80.0% | 0.0% | 100.0% | 60.0% | 100.0% | ~109.0 tok | 0.83s |
| 9 | Claude Haiku + Graphiti (JSON) | 64.0% | 80.0% | 0.0% | 40.0% | 100.0% | 100.0% | ~417.4 tok | 0.98s |
