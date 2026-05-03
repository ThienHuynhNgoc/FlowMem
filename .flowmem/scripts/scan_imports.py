#!/usr/bin/env python3
"""
FlowMem — scan_imports.py
Builds a module-level dependency graph from Python imports.
Output: JSON adjacency list to stdout. Used to generate flowchart LR (module graph).

Usage:
    python3 scan_imports.py [root_dir]
    python3 scan_imports.py > .flowmem/.cache/imports.json
"""
import ast
import json
import os
import sys
from pathlib import Path
from collections import defaultdict


def get_root(argv):
    if len(argv) > 1:
        return Path(argv[1])
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".flowmem").exists() or (parent / "src").exists():
            return parent
    return Path.cwd()


def module_name(filepath, root):
    rel = Path(filepath).relative_to(root)
    parts = list(rel.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def main():
    root = get_root(sys.argv)
    skip_dirs = {".venv", "venv", "node_modules", "__pycache__", ".git", "dist", "build"}

    # Map filepath -> module name
    file_to_module = {}
    for fp in sorted(root.rglob("*.py")):
        if any(part in skip_dirs for part in fp.parts):
            continue
        file_to_module[str(fp)] = module_name(fp, root)

    module_set = set(file_to_module.values())
    edges = defaultdict(set)

    for fp, mod in file_to_module.items():
        try:
            source = Path(fp).read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level > 0:
                # Relative import
                parts = mod.split(".")
                base = parts[:-(node.level)]
                target = ".".join(base + ([node.module] if node.module else []))
                if target in module_set and target != mod:
                    edges[mod].add(target)
            elif isinstance(node, ast.ImportFrom) and node.module:
                # Absolute import — only track internal modules
                target = node.module
                if target in module_set and target != mod:
                    edges[mod].add(target)
                # Check prefix match
                for internal_mod in module_set:
                    if target.startswith(internal_mod + ".") and internal_mod != mod:
                        edges[mod].add(internal_mod)

    result = {
        "root": str(root),
        "modules": sorted(module_set),
        "edges": {k: sorted(v) for k, v in edges.items()},
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
