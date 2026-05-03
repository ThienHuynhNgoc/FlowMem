# FlowMem Output Format Specification

This document defines the exact structure of the `.flowmem/` directory that FlowMem
creates in a project root.

---

## Directory Layout

```
.flowmem/
├── INDEX.md              # Master index — always load first
├── TRAVERSE.md           # Traversal guide specific to this project
├── .gitignore            # Ignores .cache/
├── charts/
│   ├── structure/        # Code organization charts
│   │   ├── modules.mmd   # Import/module dependency graph
│   │   ├── classes.mmd   # Class/interface hierarchy
│   │   └── overview.mmd  # High-level system overview (C4)
│   ├── behavior/         # Dynamic execution charts
│   │   ├── *.mmd         # One per major API flow or state machine
│   ├── data/             # Data model charts
│   │   └── schema.mmd    # ER diagram
│   ├── project/          # Planning charts
│   │   ├── roadmap.mmd   # Gantt or kanban
│   │   └── timeline.mmd  # Project history
│   └── quality/          # Health metrics
│       ├── debt.mmd      # Tech debt mindmap
│       ├── history.mmd   # Git graph
│       └── coverage.mmd  # Radar chart
├── scripts/              # Refresh scripts (copied from skill)
│   ├── refresh_all.sh
│   ├── scan_ast.py
│   ├── scan_imports.py
│   ├── scan_todos.py
│   ├── scan_metrics.py
│   ├── scan_packages.js
│   ├── scan_ts_exports.js
│   ├── scan_git.sh
│   └── scan_files.sh
└── .cache/               # Script output cache (gitignored)
    ├── ast.json
    ├── imports.json
    ├── todos.json
    ├── git.txt
    └── files.txt
```

---

## `.mmd` File Format

Every chart file MUST follow this format:

```
%%{init: {'theme': 'default'}}%%
%% FlowMem | type=<TYPE> | layer=<LAYER> | method=<script|ai> | refresh=<PATH|none> | last-updated=<YYYY-MM-DD> %%
<DIAGRAM_TYPE>
    [diagram content]
```

### Metadata fields

| Field | Required | Values | Description |
|---|---|---|---|
| `type` | yes | Mermaid keyword | e.g. `classDiagram`, `flowchart`, `sequenceDiagram` |
| `layer` | yes | `structure` / `behavior` / `data` / `project` / `quality` | Organizational layer |
| `method` | yes | `script` / `ai` | How the chart was generated |
| `refresh` | yes | relative path or `none` | Script to run before re-reading |
| `last-updated` | yes | `YYYY-MM-DD` | Date of last regeneration |

---

## INDEX.md Format

```markdown
# FlowMem Index — <Project Name>
Generated: <YYYY-MM-DD> | Charts: <N>

## Structure Layer — Code Organization

| Chart | Type | Method | Description |
|-------|------|--------|-------------|
| [modules.mmd](charts/structure/modules.mmd) | flowchart LR | script | Module import dependencies |
| [classes.mmd](charts/structure/classes.mmd) | classDiagram | script | Class and interface hierarchy |
| [overview.mmd](charts/structure/overview.mmd) | C4Context | ai | System architecture overview |

## Behavior Layer — Dynamic Flows

| Chart | Type | Method | Description |
|-------|------|--------|-------------|
| [auth_flow.mmd](charts/behavior/auth_flow.mmd) | sequenceDiagram | ai | Authentication sequence |

## Data Layer — Models and Schemas

...

## Project Layer — Planning

...

## Quality Layer — Health Metrics

...

---

## Quick Start for AI Traversal

Load the relevant layer for your question:
- Architecture / structure → structure layer
- API flows → behavior layer
- Data models → data layer
- Features / roadmap → project layer
- Debt / history → quality layer

For script-backed charts (method=script): run refresh script before reading.
Full refresh: `bash .flowmem/scripts/refresh_all.sh`
```

---

## TRAVERSE.md Format

```markdown
# FlowMem Traversal Guide — <Project Name>

## Entry Points by Task

### Understanding <specific feature>
1. Load: `charts/behavior/<feature>.mmd`
2. Also load: `charts/structure/classes.mmd` (for implementing classes)

### Debugging <specific component>
1. Load: `charts/structure/modules.mmd` (find where it lives)
2. Load: `charts/behavior/<relevant_flow>.mmd` (trace the execution)

### Reviewing data models
1. Load: `charts/data/schema.mmd`

### Planning new feature
1. Load: `charts/project/roadmap.mmd` (see existing plan)
2. Load: `charts/quality/debt.mmd` (see constraints)

## Refresh Commands

Script-backed charts (run before reading):
\`\`\`bash
python3 .flowmem/scripts/scan_ast.py     # Refreshes: classes.mmd
python3 .flowmem/scripts/scan_imports.py # Refreshes: modules.mmd
python3 .flowmem/scripts/scan_todos.py   # Refreshes: debt.mmd
bash .flowmem/scripts/scan_git.sh        # Refreshes: history.mmd
\`\`\`

Full refresh: `bash .flowmem/scripts/refresh_all.sh`
```

---

## `.gitignore` Content

```
.cache/
```

---

## Naming Conventions

- Chart file names: `snake_case.mmd`
- Layer directories: lowercase, single word
- Keep chart file names short and descriptive (max 30 chars)
- Use `_` not `-` in filenames
- Suffix with type only if ambiguous: `auth_sequence.mmd`, not `auth_sequenceDiagram.mmd`
