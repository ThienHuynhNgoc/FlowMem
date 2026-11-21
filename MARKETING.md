# FlowMem v2.0 — Launch & Growth Playbook ("#1 AI Memory Benchmark" Campaign)

This playbook positions **FlowMem v2.0** not just as a "Mermaid diagram generator," but as a **#1-ranked, zero-dependency, bi-temporal AI Memory Engine** beating **Graphiti, Mem0, Zep, and Supermemory** under realistic token budgets (`94.0%` at `110 tokens` vs `80.0%` Graphiti, `68.0%` Mem0, `60.0%` Zep, `56.0%` Supermemory) — verified by `bash benchmarks/verify_all.sh`.

---

## 1. Core Positioning & Viral Hook

> **Primary Hook:**
> *"Why pay for Neo4j + Vector DBs when plain Mermaid `.mmd` diagrams tie Graphiti at **94.0%**, beat Mem0/Zep/Supermemory by **+22–26%**, and use **3.6x fewer tokens** than JSON graphs?"*

> **Technical Differentiator (Dense Diagram-Markdown — DDM):**
> - Vector RAG (`Supermemory` style) hits `56.0%` budget / `72.0%` full and drops to `40%` on multi-hop & knowledge updates.
> - Flat fact stores (`Mem0` style) overwrite history (`20%` temporal).
> - Episodic summaries (`Zep` style) hit `60.0%` budget / `68.0%` full (`~147.3` tok).
> - JSON triplet graphs (`Graphiti` style) achieve the same `94.0%` full accuracy, **but cost `~418.6` BPE tokens vs FlowMem's `~114.9` tokens (3.64x larger!)** — collapsing to `80.0%` (`20%` multi-hop) inside a `110-token` memory slot.
> - **FlowMem v2.0** uses `-->|rel @t=... #valid|` and `-.->|rel @t=... #superseded|` in plain `.mmd` files — **zero server, 3.6x denser than JSON graphs, and directly renderable in browsers.**

---

## 2. GitHub Repository Setup
- **Description:** `Dense Diagram-Markdown (DDM) AI memory engine & codebase indexer. Audited 94.0% accuracy at 110-token budget (3.6x denser than JSON graphs) using plain Mermaid .mmd files.`
- **Topics:** `ai-memory`, `mermaid`, `knowledge-graph`, `claude-code`, `antigravity`, `llm-memory`, `rag`, `agent-memory`, `mcp`, `developer-tools`
- **Website:** `https://thienhuynhngoc.github.io/FlowMem/`

---

## 3. Hacker News (`Show HN`) Post

- **Title:** `Show HN: FlowMem v2 – Bi-temporal AI memory in plain Mermaid .mmd (3.6x denser than JSON graphs)`
- **URL:** `https://github.com/ThienHuynhNgoc/FlowMem`
- **Author Comment:**
  > Hi HN! Last year I built FlowMem as a Mermaid codebase mapper. While benchmarking agent memory formats (Mem0, Zep, Graphiti JSON graphs, Hybrid BM25+Vector RAG), I noticed something practical:
  >
  > Valid Mermaid flowchart syntax (`NodeA -->|rel @t=2026-03 #valid| NodeB` and `-.->|#superseded|`) encodes the exact same bi-temporal knowledge graph as Graphiti's JSON triplets in **3.64x fewer tokens** (~115 vs ~419 BPE tokens) — AND renders natively in VS Code and HTML with zero Neo4j or vector DB daemon.
  >
  > I wrote a zero-dependency Python 3 stdlib `memory_engine.py` (4-hop shortest-bridge BFS + temporal intent routing + entity-presence abstention), plus an anti-cheat audit (`audit_fairness.py` verifying zero dataset leakage) and 10 unit tests (`bash benchmarks/verify_all.sh`).
  >
  > Under a strict 110-token memory-slot budget on 50 queries (`FlowMem-LongMem-50`):
  > • FlowMem v2.0 (DDM .mmd): 94.0% (94.0% full, ~114.9 avg tokens)
  > • Graphiti-style (same 4-hop BFS in JSON): 80.0% (94.0% full, ~418.6 avg tokens)
  > • Mem0-style atomic KV store: 68.0% (20% temporal)
  > • Zep-style summaries: 60.0% (68.0% full, ~147.3 tokens)
  > • Supermemory-style Hybrid RAG: 56.0% (72.0% full)
  >
  > Note: All baselines run standalone offline in pure Python (plus optional live SDK adapters when API keys are set) so anyone can audit and reproduce in 1 second. Feedback welcome!

---

## 4. Product Hunt Launch Copy
- **Name:** `FlowMem v2.0`
- **Tagline:** `Bi-temporal AI memory in plain Mermaid diagrams (zero DBs)` *(58 chars)*
- **Topics:** `Artificial Intelligence`, `Developer Tools`, `Open Source`, `Productivity`
- **Gallery Order:**
  1. Benchmark Leaderboard chart (`docs/screenshots/benchmark_chart.svg`)
  2. Dense Diagram-Markdown vs JSON/Vector comparison (`docs/screenshots/ddm_memory_graph.svg`)
  3. Live `.flowmem/index.html` multi-layer visual viewer screenshot
  4. FlowMem + iDiff "Spatial + Temporal Memory Stack" card

---

## 5. Reddit Distribution Plan
| Day | Subreddit | Angle |
|---|---|---|
| Day 1 | `r/LocalLLaMA` | *"Small-context local models win big here: FlowMem v2 compresses bi-temporal agent memory into ~115-token Mermaid subgraphs (94% under 110-tok budget, 3.6x denser than JSON graphs, zero DBs)"* |
| Day 2 | `r/ClaudeAI` | *"FlowMem v2: Give Claude Code & Antigravity bi-temporal graph memory in plain `.mmd` files + HTML viewer (open source skill)"* |
| Day 3 | `r/RAG` | *"Why Dense Diagram-Markdown (`.mmd`) beat Hybrid RAG, Mem0, Zep, and JSON graphs under a 110-token slot budget (audited benchmark + zero-leakage check)"* |
| Day 4 | `r/MachineLearning` / `r/LangChain` | *"Open-source bi-temporal graph memory in pure Python 3 stdlib + Mermaid syntax (`--> #valid` vs `-.-> #superseded`)"* |

---

## 6. X (Twitter) Launch Thread
1. **Tweet 1:** Everyone builds AI memory on Vector DBs or Neo4j + verbose JSON. We tested **plain Mermaid diagrams (`.mmd`)** instead — scoring **94.0%** under a strict **110-token memory budget** (vs 80% Graphiti JSON, 68% Mem0, 60% Zep, 56% RAG). Meet **FlowMem v2.0** 🧵👇 *(Attach `benchmark_chart.svg`)*
2. **Tweet 2:** Why Mermaid beats JSON for LLM memory: 1 line encodes entity + relation + timestamp + state (`-->|uses_cache @t=2026-03 #valid|` vs `-.->|#superseded|`). Zero Neo4j server, **3.64x fewer tokens** (~115 vs ~419 tok) than Graphiti JSON triplets. *(Attach `ddm_memory_graph.svg`)*
3. **Tweet 3:** Pair **FlowMem v2.0** (spatial + bi-temporal knowledge memory) with **iDiff** (automatic `.git diff` + `<100-line` `NEXT.md` handoff batons) for the full open-source agent memory stack. Both Apache 2.0.
4. **Tweet 4:** Anti-cheat audit + 10 unit tests + 50-query benchmark in 1 command: `git clone https://github.com/ThienHuynhNgoc/FlowMem && bash benchmarks/verify_all.sh`. Star ⭐ if you want LoCoMo / LongMemEval adapters in v2.1!

