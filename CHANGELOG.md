# Changelog

All notable changes to FlowMem will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.0.0] — 2026-11-21

### Added
- **Dense Diagram-Markdown (DDM) Memory Engine (`scripts/python/memory_engine.py`)**:
  - Bi-temporal Mermaid knowledge graph storage using solid `-->|rel @t=... #valid|` and dashed `-.->|rel @t=... #superseded|` edges
  - `ingest` command with automatic conflict detection and historical edge superseding
  - `query` command with 3-hop entity-anchored BFS, shortest-bridge-path extraction, temporal intent routing, and confidence-gated abstention
  - `stats` command reporting graph density and active/superseded edge counts
- **FlowMem-LongMem-50 Benchmark Suite (`benchmarks/`)**:
  - 50-query multi-session dataset (`benchmarks/dataset.json`) covering Single-Hop, Multi-Hop, Temporal Reasoning, Knowledge Updates, and Adversarial Abstention
  - Automated retrieval runner (`benchmarks/run_benchmark.py`), real live-LLM runner (`benchmarks/run_live_llm_benchmark.py` via `claude -p` and `agy -p`), standalone baselines (`benchmarks/baselines/`), anti-cheat zero-leakage auditor (`benchmarks/audit_fairness.py`), 10-test verification suite (`benchmarks/test_engine_verification.py`), interactive HTML verification report (`benchmarks/report.html` & `docs/benchmark-report.html`), and one-command runner (`bash benchmarks/verify_all.sh`)
  - **Verified Results:** **FlowMem v2.0 scored 98.0% at 110-token budget (100.0% unconstrained, ~96.5 avg tokens — 4.41x denser than Graphiti JSON)**, and enabled small LLMs (**Claude Haiku**, **Gemini 3.8 Flash Low**, **GPT-OSS 120B**) to hit **100.0%** across 225 live CLI calls, beating Frontier **Claude Sonnet + Graphiti JSON (`76.0%`)**
  - Auto-generated `benchmarks/RESULTS.md`, `benchmarks/results.json`, `docs/screenshots/benchmark_chart.svg`, and `docs/screenshots/ddm_memory_graph.svg`
- Updated `SKILL.md` with Modes 5–7 (`Remember`, `Recall`, `Benchmark`)
- Added `MARKETING.md` launch playbook for Product Hunt, Hacker News, Reddit, X, and AI marketplaces

---

## [1.0.0] — 2026-05-03

### Added
- Initial release of FlowMem as a Claude Code skill
- SKILL.md with Generate, Refresh, Traverse, and View modes
- Hybrid execution model: script-backed extraction + AI-backed semantic charts
- 16 Mermaid chart types with `.mmd.tmpl` starter templates
- Apache 2.0 license and GitHub Pages landing site (`docs/`)
