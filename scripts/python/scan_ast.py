#!/usr/bin/env python3
"""
FlowMem — scan_ast.py
Extracts classes, functions, and imports from Python source files using the AST module.
Output: JSON to stdout. Used to generate classDiagram and flowchart (import graph).

Usage:
    python3 scan_ast.py [root_dir]
    python3 scan_ast.py > .flowmem/.cache/ast.json
"""
import ast
import json
import os
import sys
from pathlib import Path


def get_root(argv):
    if len(argv) > 1:
        return Path(argv[1])
    # Walk up from .flowmem/scripts/ to project root
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".flowmem").exists() or (parent / "src").exists():
            return parent
    return Path.cwd()


def extract_file(filepath, root):
    rel = str(Path(filepath).relative_to(root))
    try:
        source = Path(filepath).read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
    except SyntaxError:
        return None

    classes = []
    functions = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            bases = [ast.unparse(b) for b in node.bases if hasattr(ast, "unparse")]
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    args = [a.arg for a in item.args.args if a.arg != "self"]
                    methods.append({
                        "name": item.name,
                        "args": args,
                        "line": item.lineno,
                    })
            classes.append({
                "name": node.name,
                "file": rel,
                "line": node.lineno,
                "bases": bases,
                "methods": methods,
            })

        elif isinstance(node, ast.FunctionDef) and not any(
            isinstance(parent, ast.ClassDef)
            for parent in ast.walk(tree)
            if hasattr(parent, "body") and node in getattr(parent, "body", [])
        ):
            args = [a.arg for a in node.args.args]
            functions.append({
                "name": node.name,
                "file": rel,
                "line": node.lineno,
                "args": args,
            })

        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({"type": "import", "module": alias.name, "file": rel})

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = [a.name for a in node.names]
            imports.append({
                "type": "from",
                "module": module,
                "names": names,
                "file": rel,
                "level": node.level,
            })

    return {"file": rel, "classes": classes, "functions": functions, "imports": imports}


def main():
    root = get_root(sys.argv)
    results = {"root": str(root), "files": [], "classes": [], "functions": [], "imports": []}

    py_files = sorted(root.rglob("*.py"))
    skip_dirs = {".venv", "venv", "node_modules", "__pycache__", ".git", "dist", "build"}

    for fp in py_files:
        if any(part in skip_dirs for part in fp.parts):
            continue
        data = extract_file(fp, root)
        if data:
            results["files"].append(data["file"])
            results["classes"].extend(data["classes"])
            results["functions"].extend(data["functions"])
            results["imports"].extend(data["imports"])

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
