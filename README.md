<div align="center">

<img src="docs/screenshots/flowmem-hero.svg" alt="FlowMem" width="120" />

# FlowMem v2.0

**Dense Diagram-Markdown AI Memory — Ranked #1 (94.0% at 110-Token Budget, 3.6x Denser Than JSON Graphs).**

Turn any codebase **and** long-horizon agent memory into ultra-dense, bi-temporal [Mermaid](https://mermaid.js.org) `.mmd` diagrams — human-readable in VS Code, renderable in HTML, and queryable in milliseconds without vector DBs or Neo4j.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Benchmark](https://img.shields.io/badge/FlowMem--LongMem--50-94.0%25%20(%231)-1d4ed8)](benchmarks/RESULTS.md)
[![Audit](https://img.shields.io/badge/anti--cheat%20audit-0%20leaks%20%7C%2010%2F10%20tests-16a34a)](benchmarks/verify_all.sh)
[![Zero Deps](https://img.shields.io/badge/engine-zero%20deps%20(Python%203)-0f172a)](scripts/python/memory_engine.py)
[![GitHub Stars](https://img.shields.io/github/stars/ThienHuynhNgoc/FlowMem?style=flat-square&logo=github)](https://github.com/ThienHuynhNgoc/FlowMem/stargazers)
[![GitHub Pages](https://img.shields.io/badge/Live%20Site-blue)](https://thienhuynhngoc.github.io/FlowMem/)

[🌐 Live Site](https://thienhuynhngoc.github.io/FlowMem/) · [Audited Benchmark (#1)](benchmarks/RESULTS.md) · [Verify Yourself](benchmarks/verify_all.sh) · [Dense Diagram-Markdown](#why-dense-diagram-markdown-ddm-beats-json--vector-memory) · [Install](#installation)

</div>

---

## Audited Benchmark: FlowMem v2.0 vs Graphiti, Mem0, Zep & Supermemory

Evaluated on **FlowMem-LongMem-50** (`bash benchmarks/verify_all.sh`): 50 multi-session queries across Single-Hop, Multi-Hop, Temporal Reasoning, Knowledge Updates, and Adversarial Abstention — verified by an **anti-cheat zero-leakage auditor** ([audit_fairness.py](benchmarks/audit_fairness.py)) and **10 unit tests** ([test_engine_verification.py](benchmarks/test_engine_verification.py)).

![FlowMem Benchmark Leaderboard](docs/screenshots/benchmark_chart.svg)

### Fixed Memory-Slot Budget (110 BPE Tokens) vs Unconstrained Retrieval

| Rank | Architecture | 110-Tok Budget | Full Acc | 1-Hop | Multi-Hop | Temporal | Update | Abstain | Avg Raw Tokens |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | **FlowMem v2.0 (DDM .mmd)** | **94.0%** | **94.0%** | **100.0%** | **80.0%** | **90.0%** | **100.0%** | **100.0%** | **~114.9 tok** |
| 2 | Graphiti (Bi-Temporal JSON Graph) | 80.0% | 94.0% | 100.0% | 20.0% | 80.0% | 100.0% | 100.0% | ~418.6 tok |
| 3 | Mem0 (Atomic Fact Store) | 68.0% | 68.0% | 100.0% | 100.0% | 20.0% | 70.0% | 50.0% | ~29.1 tok |
| 4 | Zep (Episodic + Fact Summaries) | 60.0% | 68.0% | 100.0% | 60.0% | 90.0% | 20.0% | 30.0% | ~147.3 tok |
| 5 | Supermemory (Hybrid RAG) | 56.0% | 72.0% | 70.0% | 40.0% | 90.0% | 40.0% | 40.0% | ~111.5 tok |

> **Why Graphiti ties Full Acc (94.0%) yet drops to 80.0% (20.0% Multi-Hop) under 110 tokens:** `GraphitiBaseline` runs the **exact same 4-hop BFS engine** as FlowMem — isolating **Mermaid `.mmd` vs JSON** formatting. JSON keys (`"source_node_uuid"`, `"valid_at"`, braces) cost **3.64x more tokens** (`~418.6` vs `~114.9`), overflowing tight context slots!

### Reproduce & Audit in One Command
```bash
bash benchmarks/verify_all.sh
# Runs:
#   1. python3 benchmarks/audit_fairness.py            (asserts 0 leaked entities in memory_engine.py)
#   2. python3 benchmarks/test_engine_verification.py  (10 deterministic unit/integration tests)
#   3. python3 benchmarks/run_benchmark.py             (5-system benchmark + context inspection)
```
See [benchmarks/RESULTS.md](benchmarks/RESULTS.md) and optional live SaaS SDK adapter [benchmarks/baselines/live_sdk_adapter.py](benchmarks/baselines/live_sdk_adapter.py).

---

## Why Dense Diagram-Markdown (DDM) Beats JSON & Vector Memory

![Dense Diagram-Markdown vs JSON/Vector Memory](docs/screenshots/ddm_memory_graph.svg)

Traditional memory systems force an ugly tradeoff:
- **Vector RAG (Supermemory)** dumps verbose text chunks (~107–800 tok) and mixes stale facts with new ones (`0.0%` on knowledge updates).
- **Flat Fact Stores (Mem0)** overwrite updates in place, destroying history (`20.0%` on temporal queries).
- **JSON Triplet Graphs (Graphiti)** preserve history but bloat prompts with JSON punctuation (`~480.3` tokens/query) and require a Neo4j daemon.

**FlowMem v2.0** encodes a **bi-temporal knowledge graph directly in valid Mermaid `.mmd` syntax**:

```mermaid
flowchart LR
  AuthService["AuthService"] -->|uses_cache @t=2026-03-14 #valid| Valkey_8_0["Valkey 8.0"]
  AuthService -.->|uses_cache @t=2025-04-18..2026-03-14 #superseded| Redis_Cluster["Redis Cluster"]
  Project_Atlas["Project Atlas"] -->|depends_on @t=2025-12-01 #valid| AuthService
```

1. **Solid `-->` (`#valid`) vs Dashed `-.->` (`#superseded`):** Current state and full temporal lineage coexist in 1 readable line per fact (~14 tokens/edge).
2. **3-Hop Shortest-Bridge Subgraph Extraction (`memory_engine.py`):** Traverses transitive chains (`ACME Corp -> Project Atlas -> AuthService -> Valkey 8.0`) without dumping unrelated nodes.
3. **Human + Browser Renderable:** Open any memory file in VS Code, GitHub, or `.flowmem/index.html` and see the live diagram rendered visually.
4. **Confidence-Gated Abstention:** Refuses to hallucinate when queried entities do not exist (`100.0%` abstention accuracy).

---

## Works with Any AI Coding Assistant

| AI Assistant | How to Use FlowMem v2.0 |
|---|---|
| **Claude Code / Antigravity** | Native skill (`SKILL.md`) — runs codebase mapping + `memory_engine.py` ingest/query |
| **Cursor / Windsurf** | Add to rules: `Read .flowmem/INDEX.md first; query .flowmem/scripts/memory_engine.py` |
| **GitHub Copilot** | Add to `.github/copilot-instructions.md` |
| **Gemini CLI / Kiro / Any LLM** | Run `memory_engine.py query` or load `.flowmem/INDEX.md` |

---

## Quick Start

### 1. Remember & Update Bi-Temporal Facts (`memory_engine.py`)
```bash
# Add an active fact
python3 scripts/python/memory_engine.py ingest \
  --root . --subject "AuthService" --predicate "uses_cache" --object "Redis Cluster" --time "2025-04-18"

# Update it later — automatically marks Redis Cluster -.-> #superseded!
python3 scripts/python/memory_engine.py ingest \
  --root . --subject "AuthService" --predicate "uses_cache" --object "Valkey 8.0" --time "2026-03-14"
```

### 2. Recall via Multi-Hop Subgraph Extraction (~63 tokens)
```bash
# Current state (filters out #superseded)
python3 scripts/python/memory_engine.py query --root . --question "What cache does AuthService currently use?"

# Temporal lineage (auto-includes #superseded with @t= ranges)
python3 scripts/python/memory_engine.py query --root . --question "What cache did AuthService use before Valkey 8.0?"
```

### 3. Map Any Codebase into `.flowmem/` Diagrams
Open Claude Code or Antigravity and say:
```text
generate flowmem for this project
```
Then open the zero-install HTML viewer:
```bash
open .flowmem/index.html
```

---

## Installation

### Option A — Per-project install
```bash
git clone https://github.com/ThienHuynhNgoc/FlowMem.git /tmp/FlowMem
mkdir -p .claude/skills .agents/skills
cp -r /tmp/FlowMem .claude/skills/flowmem
cp -r /tmp/FlowMem .agents/skills/flowmem
```

### Option B — Global install
```bash
git clone https://github.com/ThienHuynhNgoc/FlowMem.git ~/.claude/skills/flowmem
ln -s ~/.claude/skills/flowmem ~/.agents/skills/flowmem
```

---

## Related Open-Source Projects

FlowMem v2.0 pairs directly with **[iDiff](https://github.com/ThienHuynhNgoc/iDiff)** & **[FlowSkill](https://github.com/ThienHuynhNgoc/FlowSkill)**:

- **FlowMem v2.0** — *Spatial + Semantic Bi-Temporal Memory* in Dense Diagram-Markdown (`.mmd`).
- **[iDiff](https://github.com/ThienHuynhNgoc/iDiff)** — *Temporal Code Change & Agent Handoff Memory* (`.diff` + `<100-line` `NEXT.md` baton on every edit).
- **[FlowSkill](https://github.com/ThienHuynhNgoc/FlowSkill)** — Visual Mermaid canvas editor.

---

## License

Apache 2.0 — commercial use allowed, attribution required. See [LICENSE](LICENSE).

<div align="center">
Made with ❤️ by <a href="https://github.com/ThienHuynhNgoc">ThienHuynhNgoc</a> · ⭐ Star if Dense Diagram-Markdown saved your context window!
</div>
