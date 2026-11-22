---
name: flowmem
description: >
  FlowMem v2.0 is a Dense Diagram-Markdown (DDM) AI memory system for both codebases and
  long-horizon agent memory. Every fact, entity relationship, architectural flow, and temporal
  state transition becomes a compact Mermaid `.mmd` diagram — human-readable in VS Code,
  renderable in HTML, and queryable via k-hop subgraph extraction at ~63 tokens per query.

  TRIGGER when the user says any of:
  - "generate flowmem", "build flowmem memory", "create mermaid memory for this repo"
  - "index this codebase", "map this project", "chart this codebase"
  - "remember this", "ingest fact into flowmem", "update flowmem memory"
  - "recall from flowmem", "query flowmem memory", "what does flowmem remember about..."
  - "run flowmem benchmark", "compare flowmem vs mem0/zep/graphiti/supermemory"
  - "show me the flowmem index", "traverse flowmem", "refresh flowmem charts"
  - "open the memory viewer", "show html viewer", "open flowmem html"

  FlowMem uses a 3-pillar model:
  - Script-backed codebase charts: deterministic bash/python/node scripts extract AST, imports, TODOs, git
  - AI-backed architectural charts: semantic reasoning generates sequences, C4, ER, and state machines
  - Bi-temporal Dense Diagram-Markdown (DDM) engine (`memory_engine.py`): stores evolving facts with
    `-->|rel @t=... #valid|` and `-.->|rel @t=... #superseded|` edges and answers multi-hop & temporal
    queries at 98.0% (110-tok budget) / 100.0% unconstrained (`~96.5` avg tok, `100.0%` live LLM on Haiku/Flash/Sonnet).
---

# FlowMem v2.0 — Dense Diagram-Markdown (DDM) AI Memory

Transform any codebase **or** long-term agent knowledge stream into a dense, navigable Mermaid `.mmd` memory system — readable in VS Code, browsable in HTML, and queryable via bi-temporal multi-hop subgraph extraction.

## When FlowMem is Triggered

Detect which mode based on user intent and `.flowmem/`:
1. **Generate** — Build a fresh FlowMem memory for a project (no `.flowmem/INDEX.md` yet)
2. **Refresh** — Re-run extraction scripts and regenerate stale charts
3. **Traverse** — Navigate existing `.flowmem/` charts to answer codebase questions
4. **View** — Rebuild and open `.flowmem/index.html`
5. **Remember (Ingest)** — Store a new bi-temporal fact (`memory_engine.py ingest`) into `.flowmem/charts/data/knowledge_graph.mmd`, automatically superseding conflicting prior facts
6. **Recall (Query)** — Run k-hop BFS + temporal routing (`memory_engine.py query`) to retrieve a compact Mermaid subgraph (~63 tokens)
7. **Benchmark** — Run `python3 benchmarks/run_benchmark.py` to evaluate FlowMem v2.0 vs Mem0, Zep, Graphiti, and Supermemory

---

## Mode 1: Generate (Codebase Indexing)

### Phase 1 — Classify
Read `README.md`, top-level files (`find . -maxdepth 2 -type f`), main source folders, and manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`).

| If the project has... | Generate these charts |
|---|---|
| Python source files | `classDiagram` (`scan_ast.py`), `flowchart` (`scan_imports.py`) |
| JS/TS source files | `classDiagram` (`scan_ts_exports.js`), `flowchart` (`scan_packages.js`) |
| Any source files | `mindmap` (`scan_todos.py`), `pie` (`scan_files.sh`) |
| Git history | `gitGraph` + `timeline` (`scan_git.sh`) |
| API routes or handlers | `sequenceDiagram` (AI) |
| State machines or lifecycle | `stateDiagram-v2` (AI) |
| Database models / SQL | `erDiagram` (AI) |
| Evolving project/team facts | `flowchart LR` bi-temporal graph (`memory_engine.py`) |

Always generate at minimum:
- `structure/modules.mmd` (`flowchart`)
- `quality/debt.mmd` (`mindmap`)
- `project/overview.mmd` (`C4Context` or `flowchart`)

### Phase 2 — Extract
Copy all scripts from the skill's `scripts/` into `.flowmem/scripts/` and run:
```bash
python3 .flowmem/scripts/scan_ast.py > .flowmem/.cache/ast.json
python3 .flowmem/scripts/scan_imports.py > .flowmem/.cache/imports.json
python3 .flowmem/scripts/scan_todos.py > .flowmem/.cache/todos.json
python3 .flowmem/scripts/scan_metrics.py > .flowmem/.cache/metrics.json
node .flowmem/scripts/scan_packages.js > .flowmem/.cache/packages.json
node .flowmem/scripts/scan_ts_exports.js > .flowmem/.cache/ts_exports.json
bash .flowmem/scripts/scan_git.sh > .flowmem/.cache/git.txt
bash .flowmem/scripts/scan_files.sh > .flowmem/.cache/files.txt
```

### Phase 3 — Chart Generation
Every `.mmd` file MUST start with:
```mermaid
%%{init: {'theme': 'default'}}%%
%% FlowMem | type=<TYPE> | layer=<LAYER> | method=<script|ai|engine> | refresh=<path|none> | last-updated=<YYYY-MM-DD> %%
<DIAGRAM_TYPE>
    ...content...
```

### Phase 4 — Index, Traversal Guide & HTML Viewer
Generate `.flowmem/INDEX.md`, `.flowmem/TRAVERSE.md`, `.flowmem/.gitignore` (`.cache/`), and `.flowmem/index.html`.

---

## Mode 2: Refresh
1. Read `.flowmem/INDEX.md`
2. Run `bash .flowmem/scripts/refresh_all.sh`
3. Regenerate script-backed `.mmd` charts and rebuild `.flowmem/index.html`

---

## Mode 3: Traverse (Codebase Q&A)
1. Read `.flowmem/INDEX.md` first (never load all charts at once).
2. Match question to layer (`structure`, `behavior`, `data`, `project`, `quality`).
3. Refresh script-backed charts before reading.
4. Answer using specific node/edge names from the loaded chart.

---

## Mode 4: View
Rebuild `.flowmem/index.html` embedding every `.mmd` inside `<div class="mermaid">...</div>` and tell the user to run `open .flowmem/index.html`.

---

## Mode 5: Remember — Ingest Bi-Temporal Facts (`memory_engine.py`)

When the user asks you to remember decisions, architecture changes, people/ownership, preferences, or evolving project state, store them in **Dense Diagram-Markdown (DDM)** format using `memory_engine.py`:

```bash
python3 .flowmem/scripts/memory_engine.py ingest \
  --root . \
  --subject "AuthService" \
  --predicate "uses_cache" \
  --object "Valkey 8.0" \
  --time "2026-11-21"
```

### How Conflict Resolution Works
- Active facts use solid arrows tagged `#valid`:
  `AuthService["AuthService"] -->|uses_cache @t=2026-11-21 #valid| Valkey_8_0["Valkey 8.0"]`
- When a new value arrives for the same `(subject, predicate)`, `memory_engine.py` automatically converts the prior active edge into a dashed historical edge tagged `#superseded`:
  `AuthService["AuthService"] -.->|uses_cache @t=2025-04..2026-11-21 #superseded| Redis_Cluster["Redis Cluster"]`
- Add `--no-supersede` when recording multi-valued facts (e.g., `depends_on`).

---

## Mode 6: Recall — Subgraph Query (`memory_engine.py`)

When answering multi-hop, temporal, or current-state questions across `.flowmem/` graphs:

```bash
python3 .flowmem/scripts/memory_engine.py query \
  --root . \
  --question "Which cache did AuthService use before Valkey 8.0?" \
  --hops 3
```

### Query Routing Behavior
- **Current-state questions:** Traverses `#valid` edges up to 3 hops and extracts only the shortest relevant bridge paths (~63 tokens avg).
- **Temporal/history questions** (`before`, `previously`, `when`, `used to`, `migrated from`): Automatically includes `#superseded` historical edges with `@t=` ranges.
- **Unmentioned entities:** Emits `"status": "ABSTAIN"` instead of guessing.
- **Stats:** `python3 .flowmem/scripts/memory_engine.py stats --root .`

---

## Mode 7: Benchmark & Anti-Cheat Verification (`FlowMem-LongMem-50`)

Run the audited 3-stage verification suite (anti-cheat zero-leakage audit + 10 unit tests + 50-query benchmark across FlowMem, Graphiti, Mem0, Zep, and Supermemory baselines):

```bash
bash benchmarks/verify_all.sh
```

Outputs `benchmarks/RESULTS.md`, `benchmarks/results.json`, and SVG charts in `docs/screenshots/`.

---

## Quality Rules
1. **Use real codebase & entity names** — never generic placeholders.
2. **One chart = one focused concept** (or split if >40 nodes).
3. **Never skip `#valid` / `#superseded` tags** on evolving bi-temporal edges.
4. **Always run `memory_engine.py query`** before guessing on multi-hop or temporal questions; abstain cleanly when `status == "ABSTAIN"`.
5. **100% standalone & offline** — zero external runtime dependencies beyond Python 3 stdlib and Bash.
