#!/usr/bin/env python3
"""
FlowMem — scan_metrics.py
Collects file-level complexity metrics: line counts, function counts, nesting depth.
Output: JSON to stdout. Used to generate quadrantChart (complexity vs value) and xychart-beta.

Usage:
    python3 scan_metrics.py [root_dir]
    python3 scan_metrics.py > .flowmem/.cache/metrics.json
"""
import ast
import json
import os
import sys
from pathlib import Path

SOURCE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx"}
SKIP_DIRS = {".venv", "venv", "node_modules", "__pycache__", ".git", "dist", "build", ".flowmem"}


def get_root(argv):
    if len(argv) > 1:
        return Path(argv[1])
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".flowmem").exists() or (parent / "src").exists():
            return parent
    return Path.cwd()


def max_nesting(tree):
    """Estimate max nesting depth via AST walk."""
    max_depth = [0]
    NESTING = (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.FunctionDef, ast.AsyncFunctionDef)

    def walk(node, depth):
        if isinstance(node, NESTING):
            max_depth[0] = max(max_depth[0], depth)
            for child in ast.iter_child_nodes(node):
                walk(child, depth + 1)
        else:
            for child in ast.iter_child_nodes(node):
                walk(child, depth)

    walk(tree, 0)
    return max_depth[0]


def analyze_py(fp, root):
    rel = str(fp.relative_to(root))
    try:
        source = fp.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
    except SyntaxError:
        return None

    lines = source.splitlines()
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]
    func_count = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
    class_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
    nesting = max_nesting(tree)

    return {
        "file": rel,
        "total_lines": len(lines),
        "code_lines": len(code_lines),
        "functions": func_count,
        "classes": class_count,
        "max_nesting": nesting,
        "complexity_score": round(func_count * 2 + nesting * 3 + len(code_lines) / 50, 1),
    }


def analyze_generic(fp, root):
    rel = str(fp.relative_to(root))
    try:
        lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return None
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith("//")]
    return {
        "file": rel,
        "total_lines": len(lines),
        "code_lines": len(code_lines),
        "functions": None,
        "classes": None,
        "max_nesting": None,
        "complexity_score": round(len(code_lines) / 30, 1),
    }


def main():
    root = get_root(sys.argv)
    files = []

    for fp in sorted(root.rglob("*")):
        if fp.suffix not in SOURCE_EXTS:
            continue
        if any(part in SKIP_DIRS for part in fp.parts):
            continue
        if fp.suffix == ".py":
            data = analyze_py(fp, root)
        else:
            data = analyze_generic(fp, root)
        if data:
            files.append(data)

    # Sort by complexity score descending
    files.sort(key=lambda x: x["complexity_score"], reverse=True)

    result = {
        "root": str(root),
        "total_files": len(files),
        "top_complex": files[:20],
        "all_files": files,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
