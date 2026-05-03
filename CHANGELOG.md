# Changelog

All notable changes to FlowMem will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-05-03

### Added
- Initial release of FlowMem as a Claude Code skill
- SKILL.md with three operation modes: Generate, Refresh, Traverse
- Hybrid execution model: script-backed (7 scripts) + AI-backed charts
- 16 Mermaid chart types with `.mmd.tmpl` starter templates
- 7 extraction scripts: scan_ast.py, scan_imports.py, scan_todos.py, scan_metrics.py, scan_packages.js, scan_ts_exports.js, scan_git.sh, scan_files.sh, refresh_all.sh
- `.flowmem/` directory specification with layered chart organization
- INDEX.md and TRAVERSE.md generation for AI-guided traversal
- Full Mermaid cheatsheet for all 26 diagram types
- Chart selector decision matrix
- Traversal protocol with freshness heuristics
- Apache 2.0 license
- GitHub Pages landing site (docs/)

### Chart types supported in v1.0
- `flowchart LR` — module dependency graph (script)
- `classDiagram` — class/interface hierarchy (script)
- `sequenceDiagram` — API flows (AI)
- `stateDiagram-v2` — state machines (AI)
- `erDiagram` — database schemas (AI)
- `gantt` — feature roadmap (AI)
- `kanban` — task board (AI)
- `mindmap` — tech debt (script+AI)
- `gitGraph` — git history (script)
- `quadrantChart` — complexity metrics (script)
- `C4Context` — system architecture (AI)
- `sankey-beta` — data flows (AI)
- `timeline` — project history (AI)
- `radar` — coverage metrics (AI)
- `pie` — file distribution (script)
- `requirementDiagram` — requirements (AI)

---

## [Unreleased]

### Planned
- Go language support (scan_go.sh)
- Rust language support (scan_cargo.py)
- Java/Kotlin support
- `architecture-beta` diagram type integration
- CI/CD integration (GitHub Actions workflow to auto-refresh on push)
- MCP server mode for direct tool-call access to .flowmem/ memory
