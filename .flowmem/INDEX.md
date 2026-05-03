# FlowMem Index — flowmem
Generated: 2026-05-03 | Charts: 10 | Skill version: 1.0

> AI Traversal: Read this file first. Load charts by layer based on your question.
> Full refresh: `bash .flowmem/scripts/refresh_all.sh`

---

## Structure Layer — Code Organization

| Chart | Type | Method | Description |
|-------|------|--------|-------------|
| [modules.mmd](charts/structure/modules.mmd) | flowchart LR | script | Project module/file dependency graph |
| [overview.mmd](charts/structure/overview.mmd) | C4Context | ai | System context — actors, systems, relationships |

## Behavior Layer — Dynamic Flows

| Chart | Type | Method | Description |
|-------|------|--------|-------------|
| [generate_flow.mmd](charts/behavior/generate_flow.mmd) | sequenceDiagram | ai | How FlowMem generates memory (5-phase flow) |
| [traverse_flow.mmd](charts/behavior/traverse_flow.mmd) | sequenceDiagram | ai | How AI traverses FlowMem memory on demand |

## Data Layer — Models & Schemas

| Chart | Type | Method | Description |
|-------|------|--------|-------------|
| [data_flow.mmd](charts/data/data_flow.mmd) | sankey-beta | ai | Data flow from codebase → extraction scripts → chart types |

## Project Layer — Planning & History

| Chart | Type | Method | Description |
|-------|------|--------|-------------|
| [roadmap.mmd](charts/project/roadmap.mmd) | gantt | ai | Development roadmap (v1.0 done, v1.1 and v2.0 planned) |
| [tasks.mmd](charts/project/tasks.mmd) | kanban | ai | Current task board (backlog, in-progress, done) |

## Quality Layer — Health Metrics

| Chart | Type | Method | Description |
|-------|------|--------|-------------|
| [debt.mmd](charts/quality/debt.mmd) | mindmap | script | Tech debt map (TODO/FIXME clusters) |
| [complexity.mmd](charts/quality/complexity.mmd) | quadrantChart | script | Script complexity vs file size |
| [distribution.mmd](charts/quality/distribution.mmd) | pie | script | File type distribution across project |

---

## AI Quick Reference

**For architecture questions** → structure layer, start with `overview.mmd`
**For understanding how FlowMem works** → behavior layer
**For data flow questions** → data layer, `data_flow.mmd`
**For planning context** → project layer (`roadmap.mmd` or `tasks.mmd`)
**For tech debt / code health** → quality layer

**Script-backed charts (method=script):** Run `.flowmem/scripts/refresh_all.sh` first.
**AI-backed charts (method=ai):** Read directly; regenerate only on major changes.

See `.flowmem/TRAVERSE.md` for project-specific traversal guidance.
