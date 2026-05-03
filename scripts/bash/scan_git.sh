#!/usr/bin/env bash
# FlowMem — scan_git.sh
# Extracts git history, branch structure, and contributor info.
# Output: structured text to stdout. Used to generate gitGraph and timeline charts.
#
# Usage:
#   bash scan_git.sh [repo_path]
#   bash scan_git.sh > .flowmem/.cache/git.txt

set -euo pipefail

REPO="${1:-.}"
cd "$REPO"

if ! git -C . rev-parse --git-dir > /dev/null 2>&1; then
  echo '{"error": "Not a git repository"}'
  exit 0
fi

echo "=== RECENT_COMMITS ==="
git log --oneline --decorate --no-walk --tags 2>/dev/null | head -5 || true
git log --oneline -30 --no-merges 2>/dev/null

echo ""
echo "=== BRANCHES ==="
git branch -a --sort=-committerdate 2>/dev/null | head -20

echo ""
echo "=== TAGS ==="
git tag --sort=-version:refname 2>/dev/null | head -10

echo ""
echo "=== CONTRIBUTORS ==="
git shortlog -sn --no-merges 2>/dev/null | head -10

echo ""
echo "=== MONTHLY_ACTIVITY ==="
git log --pretty=format:"%ad" --date=format:"%Y-%m" 2>/dev/null | sort | uniq -c | tail -12

echo ""
echo "=== FIRST_COMMIT ==="
git log --oneline --reverse 2>/dev/null | head -1

echo ""
echo "=== CURRENT_BRANCH ==="
git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD 2>/dev/null
