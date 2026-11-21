#!/usr/bin/env bash
# FlowMem v2.0 — One-Command Verification Suite
# Runs:
#   1. Anti-cheat & zero-leakage audit (benchmarks/audit_fairness.py)
#   2. 10 unit & integration tests (benchmarks/test_engine_verification.py)
#   3. Full 50-query audited benchmark across 5 architectures (benchmarks/run_benchmark.py)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "============================================================"
echo "Step 1/3 — Anti-Cheat & Zero-Leakage Audit"
echo "============================================================"
python3 benchmarks/audit_fairness.py

echo ""
echo "============================================================"
echo "Step 2/3 — Memory Engine Unit & Integration Tests (10 tests)"
echo "============================================================"
python3 benchmarks/test_engine_verification.py -v

echo ""
echo "============================================================"
echo "Step 3/3 — FlowMem-LongMem-50 Benchmark (5 Architectures)"
echo "============================================================"
python3 benchmarks/run_benchmark.py --token-budget 110 --sample-output
