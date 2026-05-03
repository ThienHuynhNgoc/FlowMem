#!/usr/bin/env bash
# FlowMem — refresh_all.sh
# Runs all extraction scripts and updates the .flowmem/.cache/ directory.
# Run this before reading script-backed charts to ensure data is current.
#
# Usage:
#   bash .flowmem/scripts/refresh_all.sh
#   bash .flowmem/scripts/refresh_all.sh [project_root]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
CACHE="$ROOT/.flowmem/.cache"

mkdir -p "$CACHE"
cd "$ROOT"

echo "FlowMem Refresh — $(date)"
echo "Project root: $ROOT"
echo ""

run_script() {
  local name="$1"
  local cmd="$2"
  local output="$3"
  printf "  %-30s" "$name"
  if eval "$cmd" > "$output" 2>/dev/null; then
    echo "OK"
  else
    echo "SKIPPED (no relevant files or tool missing)"
  fi
}

echo "Running extraction scripts..."
run_script "scan_files.sh"      "bash \"$SCRIPT_DIR/scan_files.sh\" \"$ROOT\""    "$CACHE/files.txt"
run_script "scan_git.sh"        "bash \"$SCRIPT_DIR/scan_git.sh\" \"$ROOT\""     "$CACHE/git.txt"
run_script "scan_todos.py"      "python3 \"$SCRIPT_DIR/scan_todos.py\" \"$ROOT\"" "$CACHE/todos.json"
run_script "scan_ast.py"        "python3 \"$SCRIPT_DIR/scan_ast.py\" \"$ROOT\""  "$CACHE/ast.json"
run_script "scan_imports.py"    "python3 \"$SCRIPT_DIR/scan_imports.py\" \"$ROOT\""  "$CACHE/imports.json"
run_script "scan_metrics.py"    "python3 \"$SCRIPT_DIR/scan_metrics.py\" \"$ROOT\""  "$CACHE/metrics.json"
run_script "scan_packages.js"   "node \"$SCRIPT_DIR/scan_packages.js\" \"$ROOT\""    "$CACHE/packages.json"
run_script "scan_ts_exports.js" "node \"$SCRIPT_DIR/scan_ts_exports.js\" \"$ROOT\""  "$CACHE/ts_exports.json"

echo ""
echo "Cache updated: $CACHE"
echo ""
echo "Script-backed charts that may need regeneration:"
for mmd in "$ROOT/.flowmem/charts"/**/*.mmd; do
  [ -f "$mmd" ] || continue
  if grep -q "method=script" "$mmd" 2>/dev/null; then
    rel="${mmd#$ROOT/}"
    echo "  $rel"
  fi
done

echo ""
echo "Re-trigger FlowMem to regenerate charts from fresh cache data."
