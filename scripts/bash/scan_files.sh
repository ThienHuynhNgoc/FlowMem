#!/usr/bin/env bash
# FlowMem — scan_files.sh
# Builds a file tree summary with extension breakdown and size info.
# Output: structured text to stdout. Used to generate pie charts and treemaps.
#
# Usage:
#   bash scan_files.sh [root_dir]
#   bash scan_files.sh > .flowmem/.cache/files.txt

set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"

echo "=== FILE_TREE ==="
find . -not \( -path "./.git/*" -o -path "./node_modules/*" -o -path "./.venv/*" \
              -o -path "./dist/*" -o -path "./build/*" -o -path "./.flowmem/.cache/*" \) \
     -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \
     -o -name "*.go" -o -name "*.rs" -o -name "*.java" -o -name "*.md" -o -name "*.json" \
     2>/dev/null | grep -v "^\./node_modules" | sort | head -100

echo ""
echo "=== EXTENSION_COUNTS ==="
find . -not \( -path "./.git/*" -o -path "./node_modules/*" -o -path "./.venv/*" -o -path "./dist/*" \) \
     -type f 2>/dev/null | sed "s/.*\.//" | sort | uniq -c | sort -rn | head -20

echo ""
echo "=== LARGEST_FILES ==="
find . -not \( -path "./.git/*" -o -path "./node_modules/*" \) \
     -type f -name "*.py" -o -name "*.ts" -o -name "*.tsx" \
     2>/dev/null | xargs wc -l 2>/dev/null | sort -rn | head -20 || true

echo ""
echo "=== DIR_SUMMARY ==="
for d in src lib app backend frontend; do
  if [ -d "$d" ]; then
    count=$(find "$d" -type f 2>/dev/null | wc -l | tr -d " ")
    echo "$count files in $d/"
  fi
done
