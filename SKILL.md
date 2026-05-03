---
name: flowmem
description: >
  FlowMem generates a Mermaid-based AI memory system for any codebase, library, or documentation set.
  Every piece of knowledge becomes a plain .mmd file — human-readable in VS Code with the Mermaid Preview
  extension, renderable in any browser via the generated HTML viewer, traversable by any AI coding assistant.

  TRIGGER when the user says any of:
  - "generate flowmem", "build flowmem memory", "create mermaid memory for this repo"
  - "index this codebase", "map this project", "chart this codebase"
  - "create memory charts", "generate mermaid charts for memory"
  - "show me the flowmem index", "what charts do we have", "load flowmem"
  - "traverse flowmem", "use flowmem memory", "refresh flowmem charts"
  - "update the memory", "regenerate charts", "re-index the codebase"
  - "open the memory viewer", "show html viewer", "open flowmem html"

  FlowMem uses a hybrid model:
  - Script-backed charts: deterministic bash/python/node scripts produce live, always-fresh data
  - AI-backed charts: semantic reasoning generates architectural, behavioral, and planning diagrams

  Output: a .flowmem/ directory at the project root with organized .mmd files, INDEX.md,
  TRAVERSE.md, and index.html — a self-contained browser viewer for fast visual browsing.

  FlowMem is 100% standalone. It does not require or depend on any external editor or app.
  All tools, scripts, and viewers are self-contained within the generated .flowmem/ directory.
---

# FlowMem

Transform any codebase into a rich, navigable Mermaid memory system. Every feature, architecture
decision, API flow, and data model becomes a `.mmd` chart — readable by humans in VS Code,
browsable in the generated HTML viewer, and traversable by AI without custom tooling.

## When FlowMem is Triggered

Detect which mode by checking whether `.flowmem/INDEX.md` already exists:
1. **Generate** — Build a fresh FlowMem memory for a new or existing repo
2. **Refresh** — Re-run scripts and regenerate stale charts
3. **Traverse** — Navigate existing `.flowmem/` memory to answer questions
4. **View** — Open or rebuild `.flowmem/index.html` for visual browsing

---

## Mode 1: Generate (no .flowmem/ exists yet)

### Phase 1 — Classify

Read these in order to understand the project:
1. `README.md` (or `README.rst`, `README.txt`)
2. Top-level directory listing (`find . -maxdepth 2 -type f`)
3. Main source directory (`src/`, `lib/`, `app/`, or equivalent)
4. Any `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`

Then decide which chart types are relevant. Use this selection matrix:

| If the project has... | Generate these charts |
|---|---|
| Python source files | classDiagram (scan_ast.py), flowchart (scan_imports.py) |
| JS/TS source files | classDiagram (scan_ts_exports.js), flowchart (scan_packages.js) |
| Any source files | mindmap (scan_todos.py), pie (scan_files.sh) |
| Git history | gitGraph + timeline (scan_git.sh) |
| API routes or handlers | sequenceDiagram (AI) |
| State machines or lifecycle | stateDiagram-v2 (AI) |
| Database models / ORM / SQL | erDiagram (AI, read schema files) |
| README with roadmap/features | gantt + kanban (AI) |
| Docker / infra / cloud config | architecture-beta + C4Context (AI) |
| Test files | radar (AI, read test coverage if available) |
| CHANGELOG or version history | timeline (AI + scan_git.sh) |
| Requirements or specs | requirementDiagram (AI) |
| Complex data flows | sankey (AI) |

Always generate at minimum:
- `structure/modules.mmd` (flowchart — file/import dependencies)
- `quality/debt.mmd` (mindmap — TODO/FIXME map)
- `project/overview.mmd` (C4Context or flowchart — system overview)

### Phase 2 — Extract (Script-backed charts)

Copy all scripts from the skill's `scripts/` directory into `.flowmem/scripts/` first, then run them.

Scripts to run:
```bash
# Python projects
python3 .flowmem/scripts/scan_ast.py > .flowmem/.cache/ast.json
python3 .flowmem/scripts/scan_imports.py > .flowmem/.cache/imports.json
python3 .flowmem/scripts/scan_todos.py > .flowmem/.cache/todos.json
python3 .flowmem/scripts/scan_metrics.py > .flowmem/.cache/metrics.json

# Node/TS projects
node .flowmem/scripts/scan_packages.js > .flowmem/.cache/packages.json
node .flowmem/scripts/scan_ts_exports.js > .flowmem/.cache/ts_exports.json

# Any project (git + filesystem)
bash .flowmem/scripts/scan_git.sh > .flowmem/.cache/git.txt
bash .flowmem/scripts/scan_files.sh > .flowmem/.cache/files.txt
```

Create `.flowmem/.cache/` to hold raw script output. Add `.flowmem/.cache/` to `.gitignore`.

### Phase 3 — Chart Generation

For each chart, generate the `.mmd` content using this structure:

```
%%{init: {'theme': 'default'}}%%
%% FlowMem | type=<TYPE> | layer=<LAYER> | method=<script|ai> | refresh=<script_path_or_none> | last-updated=<DATE> %%
<DIAGRAM_TYPE>
    ...diagram content...
```

**Layer assignments:**
- `structure` — code organization, dependencies, class hierarchy
- `behavior` — sequences, state machines, execution flows
- `data` — schemas, entity relationships, data models
- `project` — timelines, roadmaps, kanban, requirements
- `quality` — tech debt, coverage, complexity metrics

**Generating script-backed charts:**
Read the JSON from `.flowmem/.cache/` and synthesize into Mermaid syntax.

Example — classDiagram from `ast.json`:
```
classDiagram
    class UserStore {
        +login(email, password) bool
        +logout() void
        +currentUser User
    }
    UserStore --> AuthService : uses
```

**Generating AI-backed charts:**
Reason about the codebase from what you've read. Be specific — name real functions, modules,
and concepts from the project rather than using generic placeholders.

### Phase 4 — Index Generation

Create `.flowmem/INDEX.md`:

```markdown
# FlowMem Index — <project-name>
Generated: <date>

## Structure Layer
| Chart | Type | Method | Description |
|-------|------|--------|-------------|
| [modules.mmd](charts/structure/modules.mmd) | flowchart LR | script | Module import dependency graph |
| [classes.mmd](charts/structure/classes.mmd) | classDiagram | script | Class/interface hierarchy |

## Behavior Layer
...

## Data Layer
...

## Project Layer
...

## Quality Layer
...

## How to use this memory
1. For architecture questions: read `structure/` charts first
2. For API/flow questions: read `behavior/` charts
3. For data model questions: read `data/` charts
4. For planning context: read `project/` charts
5. To refresh stale charts: run `.flowmem/scripts/refresh_all.sh`
6. To view charts visually: open `.flowmem/index.html` in a browser
7. To regenerate AI charts: re-trigger FlowMem with "regenerate charts"
```

Create `.flowmem/TRAVERSE.md` from the template in `templates/TRAVERSE.md.tmpl`,
customized with this project's actual chart names and key entry points.

### Phase 5 — Finalize

1. Copy all scripts from skill's `scripts/` into `.flowmem/scripts/`
2. Create `.flowmem/.gitignore` containing `.cache/`
3. Report to user:
   - Number of charts generated, by layer
   - How to view: `open .flowmem/index.html` (browser viewer, no install needed)
   - VS Code: install Mermaid Preview extension, open any `.mmd` file
   - How to refresh: `bash .flowmem/scripts/refresh_all.sh`

### Phase 5b — HTML Viewer Generation

After all `.mmd` files are generated, create `.flowmem/index.html` — a self-contained browser
viewer that renders every chart using the mermaid.js CDN. This requires NO installation.

**Structure of the generated HTML viewer:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>FlowMem — {PROJECT_NAME}</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    /* Blue/white theme — clean, readable */
    body { font-family: Inter, sans-serif; background: #f0f7ff; color: #111827; margin: 0; }
    nav { background: #1e40af; color: white; padding: 0 24px; height: 56px; display: flex;
          align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 10; }
    .nav-title { font-weight: 700; font-size: 18px; }
    .nav-meta { font-size: 13px; opacity: 0.8; }
    .toc { width: 220px; flex-shrink: 0; padding: 24px 16px; }
    .toc-layer { font-weight: 600; color: #1e40af; font-size: 12px; text-transform: uppercase;
                 letter-spacing: .08em; margin: 16px 0 6px; }
    .toc a { display: block; font-size: 13px; color: #374151; text-decoration: none;
             padding: 4px 8px; border-radius: 6px; margin: 2px 0; }
    .toc a:hover { background: #dbeafe; color: #1e40af; }
    .main { flex: 1; padding: 32px; max-width: 960px; }
    .layer-section { margin-bottom: 48px; }
    .layer-title { font-size: 20px; font-weight: 700; color: #1e40af; border-bottom: 2px solid #bfdbfe;
                   padding-bottom: 8px; margin-bottom: 24px; }
    .chart-card { background: white; border: 1px solid #bfdbfe; border-radius: 12px;
                  margin-bottom: 24px; overflow: hidden; }
    .chart-header { background: #eff6ff; padding: 12px 20px; display: flex; align-items: center;
                    gap: 12px; border-bottom: 1px solid #bfdbfe; }
    .chart-name { font-weight: 600; color: #1e3a8a; font-size: 15px; }
    .badge { padding: 2px 10px; border-radius: 9999px; font-size: 11px; font-weight: 600; }
    .badge-script { background: #dbeafe; color: #1e40af; }
    .badge-ai { background: #ede9fe; color: #5b21b6; }
    .badge-layer { background: #f0fdf4; color: #15803d; }
    .chart-meta { font-size: 12px; color: #9ca3af; margin-left: auto; }
    .chart-body { padding: 24px; overflow-x: auto; }
    .chart-body .mermaid { display: flex; justify-content: center; }
    .layout { display: flex; }
    .search-bar { width: 100%; padding: 10px 16px; border: 1px solid #bfdbfe; border-radius: 8px;
                  font-size: 14px; margin-bottom: 24px; outline: none; }
    .search-bar:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
    footer { text-align: center; padding: 24px; color: #9ca3af; font-size: 13px;
             border-top: 1px solid #e5e7eb; background: white; }
  </style>
</head>
<body>
  <nav>
    <div class="nav-title">🧠 FlowMem — {PROJECT_NAME}</div>
    <div class="nav-meta">Generated {DATE} · {CHART_COUNT} charts · {LAYER_COUNT} layers</div>
  </nav>
  <div class="layout">
    <aside class="toc">
      {TOC_HTML}
    </aside>
    <main class="main">
      <input class="search-bar" type="text" placeholder="Search charts..." id="search"
             oninput="filterCharts(this.value)" />
      {LAYER_SECTIONS_HTML}
    </main>
  </div>
  <footer>FlowMem v1.0 · <a href="https://github.com/YOUR_REPO/flowmem" style="color:#2563eb">GitHub</a> · Apache 2.0</footer>
  <script>
    mermaid.initialize({ startOnLoad: true, theme: 'default', securityLevel: 'loose' });
    function filterCharts(q) {
      document.querySelectorAll('.chart-card').forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = q && !text.includes(q.toLowerCase()) ? 'none' : '';
      });
    }
  </script>
</body>
</html>
```

**How to build the HTML viewer:**

For each layer (structure, behavior, data, project, quality):
1. Read every `.mmd` file in `.flowmem/charts/<layer>/`
2. Strip the two FlowMem metadata comment lines from the top
3. Embed the remaining Mermaid code inside `<div class="mermaid">...</div>`
4. Create a chart card with: chart filename, type badge, method badge, layer badge, last-updated
5. Group cards into layer sections

Write the complete rendered HTML to `.flowmem/index.html`.

**Example chart card HTML block:**
```html
<div class="chart-card" id="modules-flowchart" data-layer="structure">
  <div class="chart-header">
    <span class="chart-name">modules.mmd</span>
    <span class="badge badge-layer">structure</span>
    <span class="badge badge-script">script</span>
    <span class="badge" style="background:#fef3c7;color:#92400e;font-family:monospace">flowchart LR</span>
    <span class="chart-meta">last updated: 2026-05-03</span>
  </div>
  <div class="chart-body">
    <div class="mermaid">
flowchart LR
  SKILL["SKILL.md"]
  scripts["scripts/"]
  ...
    </div>
  </div>
</div>
```

---

## Mode 2: Refresh (`.flowmem/` exists, user wants updates)

1. Read `.flowmem/INDEX.md` to see what charts exist
2. Re-run all scripts: `bash .flowmem/scripts/refresh_all.sh`
3. For script-backed charts: regenerate from new script output
4. For AI-backed charts: only regenerate if user explicitly asks ("regenerate all") or if
   relevant source files have changed significantly (check git diff)
5. Update `last-updated` metadata in each regenerated chart
6. Rebuild `.flowmem/index.html` with updated charts
7. Update INDEX.md timestamps

---

## Mode 3: Traverse (answering questions using existing memory)

When `.flowmem/INDEX.md` exists and user asks about the codebase, use this protocol:

### Step 1 — Load INDEX.md
Always read `.flowmem/INDEX.md` first. This is your map.

### Step 2 — Identify relevant layers
Match the user's question to layers:
- "How does auth work?" → behavior layer (sequenceDiagram)
- "What classes exist?" → structure layer (classDiagram)
- "What's the data model?" → data layer (erDiagram)
- "What's planned next?" → project layer (gantt/kanban)
- "Where is the tech debt?" → quality layer (mindmap)

### Step 3 — Load selectively
Read only the charts in the relevant layer. Never load all charts at once.

### Step 4 — Refresh script-backed charts before reading
For any chart where `method=script`:
```bash
# Re-run its refresh script to get current data
python3 .flowmem/scripts/scan_ast.py  # if refreshing classDiagram
bash .flowmem/scripts/scan_git.sh     # if refreshing gitGraph
```
Then read the chart file. This ensures you answer with live data.

### Step 5 — Synthesize answer
Use the chart content as structured context. Name specific nodes/edges from the chart in your answer.

---

## Mode 4: View (open/rebuild HTML viewer)

When user says "open memory viewer", "show html", or "rebuild viewer":
1. Read all `.mmd` files in `.flowmem/charts/`
2. Regenerate `.flowmem/index.html` following Phase 5b spec above
3. Tell user: `open .flowmem/index.html` (macOS) or `start .flowmem/index.html` (Windows)

---

## Chart Format Reference

See `references/chart-selector.md` for the complete decision matrix.
See `references/mermaid-cheatsheet.md` for Mermaid syntax for all 26 types.
See `references/traversal-protocol.md` for the full traversal spec.
See `references/output-format.md` for the complete `.flowmem/` directory spec.

---

## Metadata Comment Format

Every `.mmd` file MUST start with these two comment lines:

```
%%{init: {'theme': 'default'}}%%
%% FlowMem | type=<TYPE> | layer=<LAYER> | method=<script|ai> | refresh=<path|none> | last-updated=<YYYY-MM-DD> %%
```

- `type` — Mermaid diagram type keyword (e.g., `classDiagram`, `flowchart`, `sequenceDiagram`)
- `layer` — one of: `structure`, `behavior`, `data`, `project`, `quality`
- `method` — `script` (generated from script output, refresh before reading) or `ai` (semantic)
- `refresh` — path to the script that regenerates this chart, relative to project root; or `none`
- `last-updated` — ISO date of last generation

---

## Quality Rules

1. **Be specific** — Use real names from the codebase, not generic placeholders
2. **Keep charts focused** — One chart = one concept. Split if it gets large (>40 nodes)
3. **Valid Mermaid only** — Test syntax mentally before writing; prefer proven patterns
4. **No beta types in default output** — Skip `block-beta`, `packet-beta`, `treemap`, `venn`, `zenuml` unless user explicitly requests them (they may fail to render)
5. **Script-backed = always fresh** — Never trust a cached script-backed chart without running refresh first
6. **AI-backed = semantic truth** — These represent architectural understanding; only regenerate when architecture changes
7. **Standalone** — FlowMem never requires or depends on any external editor or app; all tooling is in `.flowmem/scripts/` and the generated HTML viewer
