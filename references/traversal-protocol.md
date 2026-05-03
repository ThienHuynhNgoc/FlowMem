# FlowMem Traversal Protocol

This document defines how an AI coding assistant should navigate `.flowmem/` memory
to answer questions, make decisions, and provide context-aware help.

---

## Core Principle

**Load only what you need.** FlowMem charts are organized by layer precisely so you
can load a small, relevant subset rather than the entire memory at once.

---

## Session Start Protocol

At the beginning of any session in a repo that has `.flowmem/`:

1. **Check for existence:**
   ```bash
   ls .flowmem/INDEX.md 2>/dev/null && echo "FlowMem present"
   ```

2. **Load INDEX.md** — Always read this first. It's your map. (~50 lines)

3. **Note staleness** — Check `last-updated` dates in INDEX.md. If any script-backed
   chart is older than 24 hours, offer to refresh before using it.

4. **Do not preload** — Do not read any `.mmd` files until a question requires them.

---

## Question → Layer Mapping

| User asks about... | Load layer | Charts to read |
|---|---|---|
| Code structure, architecture | `structure` | modules.mmd, classes.mmd |
| How a feature works | `behavior` | Find relevant sequence/state chart |
| Database, data models | `data` | schema.mmd, er diagrams |
| Roadmap, features, what's next | `project` | roadmap.mmd, tasks.mmd |
| Technical debt, code health | `quality` | debt.mmd, coverage.mmd |
| Recent changes, who changed what | `quality` | history.mmd (gitGraph) |
| Performance, complexity | `quality` | complexity.mmd (quadrant) |
| Everything / overview | `structure` + `project` | overview.mmd + roadmap.mmd |

---

## Reading Script-Backed Charts

For charts where `method=script` in the metadata comment:

```
%% FlowMem | type=classDiagram | layer=structure | method=script | refresh=.flowmem/scripts/scan_ast.py | last-updated=2026-05-03 %%
```

**Always refresh before reading:**
```bash
# Run the refresh script to get current data
python3 .flowmem/scripts/scan_ast.py > /tmp/ast_fresh.json
```

Then read the chart (it shows the last-generated version) AND cross-reference with
the fresh script output. If they differ significantly, regenerate the chart.

**Why:** Script-backed charts reflect code that changes every commit. A 3-day-old
`classDiagram` may be missing new classes added since then.

---

## Reading AI-Backed Charts

For charts where `method=ai`:

```
%% FlowMem | type=C4Context | layer=structure | method=ai | refresh=none | last-updated=2026-05-03 %%
```

Read the `.mmd` file directly. These represent semantic/architectural understanding
that doesn't change with every commit.

**When to suggest regeneration:**
- A major architectural change has been made (new service, new database, new auth system)
- The user explicitly says "the architecture has changed"
- The chart's `last-updated` is more than 30 days old in an active project

---

## Traversal Example: "How does authentication work?"

1. Load `.flowmem/INDEX.md` → scan for auth-related charts
2. Find: `behavior/auth_sequence.mmd` (method=ai) and `structure/classes.mmd` (method=script)
3. Refresh `classes.mmd`:
   ```bash
   python3 .flowmem/scripts/scan_ast.py > /tmp/ast.json
   ```
4. Read `behavior/auth_sequence.mmd` → get the full auth flow
5. Read `structure/classes.mmd` → identify which classes implement it
6. Answer: Reference specific nodes from the sequence diagram, name specific classes

---

## Traversal Example: "What's the tech debt situation?"

1. Load `.flowmem/INDEX.md` → find `quality/debt.mmd`
2. `method=script` → refresh first:
   ```bash
   python3 .flowmem/scripts/scan_todos.py
   ```
3. Read `quality/debt.mmd` (mindmap)
4. Answer: Name specific TODO clusters and their files from the mindmap

---

## Memory Freshness Heuristics

| Chart type | Refresh when... |
|---|---|
| `flowchart` (imports) | Any new file or import added |
| `classDiagram` | Any new class, method, or relationship |
| `mindmap` (TODOs) | Any TODO added or resolved |
| `gitGraph` | Any new commit |
| `sequenceDiagram` | API endpoint signature changes |
| `erDiagram` | Migration or schema change |
| `gantt` | Sprint planning update |
| `C4Context` | New system or major service added |

---

## Anti-Patterns to Avoid

- **Never load all charts at once** — you'll flood your context window unnecessarily
- **Never skip refreshing script-backed charts** — stale data causes wrong answers
- **Never guess node names** — use exact names from the chart content
- **Never trust a chart older than its refresh heuristic** — ask to refresh first
- **Never modify `.mmd` files by hand during traversal** — use the regeneration flow

---

## Partial Refresh

If only one chart needs updating:

```bash
# Refresh just the class diagram
python3 .flowmem/scripts/scan_ast.py > .flowmem/.cache/ast.json
# Then re-read the chart and update it
```

For a full refresh of everything:
```bash
bash .flowmem/scripts/refresh_all.sh
```

---

## Adding FlowMem to a New Session

When starting Claude Code in a repo that has `.flowmem/`, you can trigger traversal mode
automatically by including this in your `CLAUDE.md`:

```markdown
## Memory
This project uses FlowMem. When starting a session:
1. Read `.flowmem/INDEX.md` to load the memory map
2. Use the traversal protocol in `.flowmem/TRAVERSE.md` to load charts on demand
3. Run `bash .flowmem/scripts/refresh_all.sh` if charts seem stale
```
