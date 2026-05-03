#!/usr/bin/env python3
"""
FlowMem — scan_todos.py
Finds TODO, FIXME, HACK, NOTE, BUG annotations across source files.
Output: JSON to stdout. Used to generate mindmap (tech debt) and pie (distribution).

Usage:
    python3 scan_todos.py [root_dir]
    python3 scan_todos.py > .flowmem/.cache/todos.json
"""
import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

TAGS = ["TODO", "FIXME", "HACK", "NOTE", "BUG", "XXX", "OPTIMIZE", "REFACTOR"]
TAG_PATTERN = re.compile(r"\b(" + "|".join(TAGS) + r")\b[:\s]*(.*)", re.IGNORECASE)

SOURCE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".rb", ".cs", ".cpp", ".c"}
SKIP_DIRS = {".venv", "venv", "node_modules", "__pycache__", ".git", "dist", "build", ".flowmem"}


def get_root(argv):
    if len(argv) > 1:
        return Path(argv[1])
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".flowmem").exists() or (parent / "src").exists():
            return parent
    return Path.cwd()


def main():
    root = get_root(sys.argv)
    by_tag = defaultdict(list)
    by_file = defaultdict(list)
    total = 0

    for fp in sorted(root.rglob("*")):
        if fp.suffix not in SOURCE_EXTS:
            continue
        if any(part in SKIP_DIRS for part in fp.parts):
            continue
        try:
            lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue

        rel = str(fp.relative_to(root))
        for lineno, line in enumerate(lines, 1):
            m = TAG_PATTERN.search(line)
            if m:
                tag = m.group(1).upper()
                text = m.group(2).strip()[:120]
                item = {"tag": tag, "text": text, "file": rel, "line": lineno}
                by_tag[tag].append(item)
                by_file[rel].append(item)
                total += 1

    result = {
        "root": str(root),
        "total": total,
        "by_tag": {tag: items for tag, items in sorted(by_tag.items())},
        "by_file": {f: items for f, items in sorted(by_file.items()) if items},
        "summary": {tag: len(items) for tag, items in by_tag.items()},
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
