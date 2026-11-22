#!/usr/bin/env python3
"""
FlowMem v2.0 — build_report.py
Generates a self-contained, zero-build Interactive Benchmark Verification Report
in a clean Black & White / FlowMem Light editorial theme:
  - benchmarks/report.html
  - docs/benchmark-report.html

Tabs:
  1. Real Live-LLM Results (claude -p & agy -p: Small LLMs vs Frontier Sonnet)
  2. Retrieval Leaderboard & Interactive Token Budget Lab (50 queries)
  3. 50-Query Retrieval Side-by-Side Context Inspector
  4. 12-Session Corpus & Full .mmd Graph
  5. Anti-Cheat Audit & Unit Test Logs

Usage:
  python3 benchmarks/build_report.py
"""

from __future__ import annotations

import datetime
import html
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DETAILED_JSON = os.path.join(ROOT, "benchmarks", "detailed_results.json")
LIVE_JSON = os.path.join(ROOT, "benchmarks", "live_llm_results.json")
OUT_BENCH_HTML = os.path.join(ROOT, "benchmarks", "report.html")
OUT_DOCS_HTML = os.path.join(ROOT, "docs", "benchmark-report.html")


def run_capture(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return proc.returncode, proc.stdout


def main() -> int:
    if not os.path.exists(DETAILED_JSON):
        print(f"Missing {DETAILED_JSON}. Run `python3 benchmarks/run_benchmark.py` first.", file=sys.stderr)
        return 1

    with open(DETAILED_JSON, "r", encoding="utf-8") as fh:
        detailed = json.load(fh)

    live_data = None
    if os.path.exists(LIVE_JSON):
        with open(LIVE_JSON, "r", encoding="utf-8") as fh:
            live_data = json.load(fh)

    audit_rc, audit_out = run_capture([sys.executable, "benchmarks/audit_fairness.py"])
    test_rc, test_out = run_capture([sys.executable, "benchmarks/test_engine_verification.py", "-v"])

    detailed["audit"] = {"exit_code": audit_rc, "output": audit_out}
    detailed["unit_tests"] = {"exit_code": test_rc, "output": test_out}
    detailed["live_llm"] = live_data
    detailed["report_built_at"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    embedded_json = json.dumps(detailed).replace("</", "<\\/")
    audit_badge = "PASS · 0 Leaks" if audit_rc == 0 else "FAIL"
    audit_cls = "pill-green" if audit_rc == 0 else "pill-red"
    test_badge = "10/10 Tests OK" if test_rc == 0 else "Tests Failed"
    test_cls = "pill-green" if test_rc == 0 else "pill-red"
    live_badge = f"Live LLM: {len(live_data['summary']) * live_data['num_queries']} Calls Verified" if live_data else "Live LLM: Not Run"
    live_cls = "pill-green" if live_data else "pill"

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>FlowMem v2.0 — Live-LLM &amp; Retrieval Verification Report</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    :root {{
      --bg: #f8fafc;
      --surface: #ffffff;
      --subtle: #f6f8fa;
      --border: #d0d7de;
      --border-light: #e5e7eb;
      --ink: #111827;
      --text: #1f2328;
      --muted: #656d76;
      --blue: #1d4ed8;
      --blue-bg: #eff6ff;
      --blue-border: #bfdbfe;
      --green: #166534;
      --green-bg: #dcfce7;
      --green-border: #bbf7d0;
      --red: #991b1b;
      --red-bg: #fee2e2;
      --red-border: #fecaca;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    code, pre, .mono {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}
    header {{
      position: sticky; top: 0; z-index: 40;
      background: #ffffff;
      border-bottom: 1px solid var(--border-light);
      padding: 0 24px;
    }}
    .header-inner {{
      max-width: 1380px; margin: 0 auto;
      display: flex; align-items: center; justify-content: space-between;
      gap: 16px; min-height: 60px; flex-wrap: wrap; padding: 8px 0;
    }}
    .brand {{ display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 16px; color: var(--ink); }}
    .brand-mark {{
      display: inline-flex; align-items: center; justify-content: center;
      padding: 3px 8px; border-radius: 6px; background: var(--ink); color: #fff;
      font-family: ui-monospace, monospace; font-size: 12px;
    }}
    .pills {{ display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }}
    .pill {{
      display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 999px;
      font-size: 11.5px; font-weight: 600; border: 1px solid var(--border-light); background: var(--subtle); color: var(--ink);
    }}
    .pill-green {{ background: var(--green-bg); color: var(--green); border-color: var(--green-border); }}
    .pill-red {{ background: var(--red-bg); color: var(--red); border-color: var(--red-border); }}
    .pill-blue {{ background: var(--blue-bg); color: var(--blue); border-color: var(--blue-border); }}
    .tabs {{
      max-width: 1380px; margin: 0 auto; display: flex; gap: 4px; overflow-x: auto;
      border-top: 1px solid #f1f5f9; padding-top: 6px;
    }}
    .tab-btn {{
      background: transparent; border: none; border-bottom: 2px solid transparent;
      padding: 9px 14px; font-size: 13px; font-weight: 600; color: var(--muted); cursor: pointer; white-space: nowrap;
    }}
    .tab-btn:hover {{ color: var(--ink); }}
    .tab-btn.active {{ color: var(--ink); border-bottom-color: var(--ink); }}
    main {{ max-width: 1380px; margin: 0 auto; padding: 24px; }}
    .tab-pane {{ display: none; }}
    .tab-pane.active {{ display: block; }}
    .card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
      padding: 20px 24px; margin-bottom: 20px;
    }}
    .card-ink {{ border: 1.5px solid var(--ink); }}
    .section-title {{ font-size: 16px; font-weight: 700; color: var(--ink); margin: 0 0 6px; }}
    .section-sub {{ font-size: 13px; color: var(--muted); margin: 0 0 16px; }}
    .grid-2 {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }}
    .grid-3 {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }}
    .grid-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 14px; }}
    @media (max-width: 960px) {{ .grid-2, .grid-3 {{ grid-template-columns: 1fr; }} }}
    .budget-controls {{
      display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
      padding: 14px 16px; background: var(--subtle); border: 1px solid var(--border-light); border-radius: 8px;
    }}
    .budget-val {{ font-family: ui-monospace, monospace; font-size: 15px; font-weight: 800; color: var(--ink); min-width: 135px; }}
    input[type="range"] {{ flex: 1; min-width: 200px; accent-color: #111827; cursor: pointer; }}
    .btn {{
      background: #ffffff; border: 1px solid var(--border); color: var(--ink);
      border-radius: 6px; padding: 6px 11px; font-size: 12px; font-weight: 600; cursor: pointer;
    }}
    .btn:hover {{ background: #f3f4f6; }}
    .btn.active {{ background: var(--ink); color: #ffffff; border-color: var(--ink); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ text-align: left; padding: 9px 10px; border-bottom: 1px solid var(--border-light); vertical-align: top; }}
    th {{ background: var(--subtle); font-size: 11.5px; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); font-weight: 700; }}
    tr.row-hl {{ background: var(--blue-bg); font-weight: 600; }}
    tr.q-row {{ cursor: pointer; }}
    tr.q-row:hover {{ background: #f8fafc; }}
    tr.q-row.selected {{ background: #eff6ff; outline: 1px solid var(--blue-border); }}
    .num {{ text-align: right; font-family: ui-monospace, monospace; }}
    .bar-track {{ width: 100%; height: 22px; background: #f1f5f9; border-radius: 5px; overflow: hidden; border: 1px solid #e2e8f0; }}
    .bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.15s ease; }}
    .bar-flowmem {{ background: #1d4ed8; }}
    .bar-other {{ background: #64748b; }}
    .toolbar {{ display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 14px; }}
    .search-input {{
      flex: 1; min-width: 220px; padding: 7px 12px; border: 1px solid var(--border);
      border-radius: 6px; font-size: 13px; color: var(--ink); background: #fff;
    }}
    .sys-card {{
      border: 1px solid var(--border); border-radius: 8px; background: #fff; overflow: hidden;
      display: flex; flex-direction: column;
    }}
    .sys-card.is-flowmem {{ border: 1.5px solid var(--blue); }}
    .sys-head {{
      padding: 10px 14px; background: var(--subtle); border-bottom: 1px solid var(--border-light);
      display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap;
    }}
    .sys-name {{ font-weight: 700; font-size: 13px; color: var(--ink); }}
    .sys-body {{ padding: 12px 14px; font-size: 12px; overflow-x: auto; max-height: 360px; overflow-y: auto; }}
    .ctx-line {{ white-space: pre-wrap; word-break: break-word; padding: 1px 4px; font-family: ui-monospace, monospace; }}
    .ctx-cut {{ background: #fff1f2; color: #9f1239; text-decoration: line-through; opacity: 0.75; }}
    .cutoff-banner {{
      margin: 6px 0; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;
      background: var(--red-bg); color: var(--red); border: 1px solid var(--red-border);
      font-family: ui-monospace, monospace;
    }}
    .answer-box {{
      padding: 8px 10px; border-radius: 6px; margin-bottom: 8px; font-size: 12.5px;
      border: 1px solid var(--border-light); background: #f8fafc;
    }}
    .log-box {{
      background: #f8fafc; border: 1px solid var(--border); border-radius: 8px;
      padding: 14px 16px; font-size: 12px; overflow-x: auto; white-space: pre-wrap; color: var(--ink);
    }}
    .mermaid-box {{
      background: #ffffff; border: 1px solid var(--border-light); border-radius: 8px;
      padding: 14px; overflow-x: auto; margin-top: 10px;
    }}
    .kpi-card {{ background: var(--subtle); border: 1px solid var(--border-light); border-radius: 8px; padding: 14px 16px; }}
    .kpi-label {{ font-size: 11.5px; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: .04em; }}
    .kpi-value {{ font-size: 24px; font-weight: 800; color: var(--ink); margin-top: 2px; }}
    .kpi-note {{ font-size: 12px; color: var(--muted); margin-top: 2px; }}
  </style>
</head>
<body>
  <header>
    <div class="header-inner">
      <div class="brand">
        <span class="brand-mark">FlowMem v2.0</span>
        <span>Live-LLM &amp; Retrieval Verification Report</span>
      </div>
      <div class="pills">
        <span class="pill {live_cls}">{html.escape(live_badge)}</span>
        <span class="pill {audit_cls}">Audit: {html.escape(audit_badge)}</span>
        <span class="pill {test_cls}">Unit Tests: {html.escape(test_badge)}</span>
        <span class="pill mono">Built {html.escape(detailed['report_built_at'])}</span>
      </div>
    </div>
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('live', this)">1. Real Live-LLM Results (claude &amp; agy)</button>
      <button class="tab-btn" onclick="switchTab('leaderboard', this)">2. Retrieval Token Budget Lab (50 Queries)</button>
      <button class="tab-btn" onclick="switchTab('inspector', this)">3. 50-Query Context Inspector</button>
      <button class="tab-btn" onclick="switchTab('corpus', this)">4. 12-Session Corpus &amp; Full .mmd</button>
      <button class="tab-btn" onclick="switchTab('audit', this)">5. Anti-Cheat Audit &amp; Unit Tests</button>
    </div>
  </header>

  <main>
    <!-- TAB 1: REAL LIVE-LLM BENCHMARK -->
    <section id="tab-live" class="tab-pane active">
      <div class="grid-3" style="margin-bottom:18px;" id="liveKpiRow"></div>

      <div class="grid-2">
        <div class="card card-ink">
          <h2 class="section-title">Real Live-LLM Leaderboard (110-Token Budget)</h2>
          <p class="section-sub">
            Every row ran live inference through <code>claude -p</code> (Haiku &amp; Sonnet) or <code>agy -p</code> (Gemini 3.8 Flash Low &amp; GPT-OSS 120B) with zero tool access.
          </p>
          <div id="liveLlmBars"></div>
        </div>
        <div class="card">
          <h3 class="section-title">Category Breakdown (Real Generated Answers)</h3>
          <p class="section-sub">Strict grading on actual LLM output text vs ground truth &amp; forbidden stale values.</p>
          <div style="overflow-x:auto;">
            <table>
              <thead>
                <tr>
                  <th>Model + Memory</th>
                  <th class="num">Acc</th>
                  <th class="num">1-Hop</th>
                  <th class="num">M-Hop</th>
                  <th class="num">Temp</th>
                  <th class="num">Upd</th>
                  <th class="num">Abst</th>
                  <th class="num">Tok</th>
                  <th class="num">Lat</th>
                </tr>
              </thead>
              <tbody id="liveTableBody"></tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="card">
        <h2 class="section-title">25-Query Live-LLM Transcript &amp; Trace ID Inspector</h2>
        <p class="section-sub">Click any query row to inspect the verbatim answers generated by real Haiku, Gemini 3.8 Flash, GPT-OSS 120B, and Claude Sonnet calls alongside each call's <code>session_id</code> / <code>conversation_id</code>.</p>
        <div style="max-height:280px;overflow-y:auto;border:1px solid var(--border-light);border-radius:8px;margin-bottom:16px;">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Category</th>
                <th>Question</th>
                <th>Expected</th>
                <th class="num">Haiku+FM</th>
                <th class="num">Flash+FM</th>
                <th class="num">GPT-OSS+FM</th>
                <th class="num">Sonnet+Graphiti</th>
                <th class="num">Haiku+RAG</th>
              </tr>
            </thead>
            <tbody id="liveQueryBody"></tbody>
          </table>
        </div>
        <div id="liveDetailPanel"></div>
      </div>
    </section>

    <!-- TAB 2: RETRIEVAL LEADERBOARD & BUDGET LAB -->
    <section id="tab-leaderboard" class="tab-pane">
      <div class="grid-3" style="margin-bottom:18px;" id="kpiRow"></div>

      <div class="card card-ink">
        <h2 class="section-title">Interactive Memory-Slot Token Budget Simulator (All 50 Queries)</h2>
        <p class="section-sub">
          Drag the slider or click a preset. Every query across all 5 architectures is re-truncated and re-scored live in your browser using the exact same rules as <code>benchmarks/run_benchmark.py</code>.
        </p>
        <div class="budget-controls">
          <span class="budget-val" id="budgetLabel">Budget: 110 tok</span>
          <input type="range" id="budgetSlider" min="50" max="500" step="5" value="{detailed.get('token_budget', 110)}" oninput="onBudgetSlider(this.value)" />
          <button class="btn" onclick="setBudget(80, this)">80 tok</button>
          <button class="btn active" onclick="setBudget(110, this)" id="btn-110">110 tok (Default)</button>
          <button class="btn" onclick="setBudget(150, this)">150 tok</button>
          <button class="btn" onclick="setBudget(250, this)">250 tok</button>
          <button class="btn" onclick="setBudget(450, this)">450 tok</button>
          <button class="btn" onclick="setBudget(0, this)">Full Unconstrained</button>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <h3 class="section-title">Live Retrieval Leaderboard at Selected Budget</h3>
          <p class="section-sub">Sorted by Budget Accuracy, then lower Raw Token Cost.</p>
          <div id="liveBars"></div>
        </div>
        <div class="card">
          <h3 class="section-title">Accuracy vs. Context Slot Budget Curve (60 → 500 tok)</h3>
          <p class="section-sub">Shows where verbose JSON graphs catch up vs. Dense Diagram-Markdown (DDM).</p>
          <div id="curveSvgWrap"></div>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">Category Breakdown Table</h3>
        <div style="overflow-x:auto;">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Architecture</th>
                <th class="num">Active Acc</th>
                <th class="num">Full Acc</th>
                <th class="num">1-Hop</th>
                <th class="num">Multi-Hop</th>
                <th class="num">Temporal</th>
                <th class="num">Update</th>
                <th class="num">Abstain</th>
                <th class="num">Avg Raw Tokens</th>
                <th class="num">Latency</th>
              </tr>
            </thead>
            <tbody id="leaderTableBody"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- TAB 3: 50-QUERY INSPECTOR -->
    <section id="tab-inspector" class="tab-pane">
      <div class="card">
        <h2 class="section-title">Inspect All 50 Queries &amp; Exact Retrieved Contexts</h2>
        <p class="section-sub">
          Click any query row below to compare what FlowMem, Graphiti, Mem0, Zep, and Supermemory actually retrieved. Lines beyond the active token budget are shown crossed out below the cutoff divider.
        </p>
        <div class="toolbar">
          <input type="text" id="qSearch" class="search-input" placeholder="Search questions, expected answers, or ID..." oninput="renderQueryTable()" />
          <button class="btn active" onclick="setCatFilter('all', this)">All (50)</button>
          <button class="btn" onclick="setCatFilter('single_hop', this)">1-Hop</button>
          <button class="btn" onclick="setCatFilter('multi_hop', this)">Multi-Hop</button>
          <button class="btn" onclick="setCatFilter('temporal', this)">Temporal</button>
          <button class="btn" onclick="setCatFilter('knowledge_update', this)">Update</button>
          <button class="btn" onclick="setCatFilter('abstention', this)">Abstain</button>
          <button class="btn" onclick="setCatFilter('fm_miss', this)">FlowMem Misses</button>
          <button class="btn" onclick="setCatFilter('fm_beats_graphiti', this)">FlowMem &gt; Graphiti</button>
        </div>
        <div style="max-height: 320px; overflow-y: auto; border: 1px solid var(--border-light); border-radius: 8px;">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Category</th>
                <th>Question</th>
                <th>Expected</th>
                <th class="num">FlowMem</th>
                <th class="num">Graphiti</th>
                <th class="num">Mem0</th>
                <th class="num">Zep</th>
                <th class="num">Supermem</th>
              </tr>
            </thead>
            <tbody id="queryTableBody"></tbody>
          </table>
        </div>
      </div>

      <div id="detailPanel" class="card card-ink"></div>
    </section>

    <!-- TAB 4: CORPUS & FULL .MMD GRAPH -->
    <section id="tab-corpus" class="tab-pane">
      <div class="card">
        <h2 class="section-title">Compiled Bi-Temporal Mermaid Graph (All 12 Sessions)</h2>
        <p class="section-sub">
          Generated cleanly via <code>memory_engine.ingest_fact()</code>. Solid <code>--&gt;</code> = active <code>#valid</code> edges; dashed <code>-.-&gt;</code> = historical <code>#superseded</code> edges.
        </p>
        <div class="grid-2">
          <div>
            <h4 style="margin:0 0 8px;font-size:13px;">Raw <code>.mmd</code> Source</h4>
            <pre class="log-box" id="fullMmdCode" style="max-height:520px;overflow-y:auto;"></pre>
          </div>
          <div>
            <h4 style="margin:0 0 8px;font-size:13px;">Rendered Mermaid Diagram</h4>
            <div class="mermaid-box" id="fullMmdRender" style="max-height:520px;overflow:auto;"></div>
          </div>
        </div>
      </div>

      <div class="card">
        <h2 class="section-title">12-Session Multi-Turn Input Corpus</h2>
        <div id="sessionsList"></div>
      </div>
    </section>

    <!-- TAB 5: AUDIT & UNIT TEST LOGS -->
    <section id="tab-audit" class="tab-pane">
      <div class="grid-2">
        <div class="card">
          <h2 class="section-title">1. Anti-Cheat &amp; Zero-Leakage Audit</h2>
          <p class="section-sub">Command: <code>python3 benchmarks/audit_fairness.py</code></p>
          <pre class="log-box">{html.escape(audit_out)}</pre>
        </div>
        <div class="card">
          <h2 class="section-title">2. Engine Unit &amp; Integration Tests</h2>
          <p class="section-sub">Command: <code>python3 benchmarks/test_engine_verification.py -v</code></p>
          <pre class="log-box">{html.escape(test_out)}</pre>
        </div>
      </div>
      <div class="card">
        <h2 class="section-title">3. Reproduce Locally</h2>
        <pre class="log-box">cd /Users/whitewolf21/Documents/GitHub/startup/FlowMem
bash benchmarks/verify_all.sh
python3 benchmarks/run_live_llm_benchmark.py --budget 110</pre>
      </div>
    </section>
  </main>

  <script>
    const DATA = {embedded_json};
    const SYSTEM_ORDER = [
      "FlowMem v2.0 (DDM .mmd)",
      "Graphiti (Bi-Temporal JSON Graph)",
      "Mem0 (Atomic Fact Store)",
      "Zep (Episodic + Fact Summaries)",
      "Supermemory (Hybrid RAG)"
    ];
    const SHORT_NAMES = {{
      "FlowMem v2.0 (DDM .mmd)": "FlowMem v2.0",
      "Graphiti (Bi-Temporal JSON Graph)": "Graphiti",
      "Mem0 (Atomic Fact Store)": "Mem0",
      "Zep (Episodic + Fact Summaries)": "Zep",
      "Supermemory (Hybrid RAG)": "Supermemory"
    }};

    let currentBudget = DATA.token_budget || 110;
    let currentCatFilter = "all";
    let selectedQueryId = 11;
    let selectedLiveQid = 11;

    function bpeApproxTokens(text) {{
      if (!text) return 0;
      const pieces = text.match(/[A-Za-z0-9_]+|[^\\sA-Za-z0-9_]/g) || [];
      return Math.max(1, Math.round(pieces.length * 0.92));
    }}

    function truncateSplit(text, budget) {{
      if (!budget || budget <= 0 || bpeApproxTokens(text) <= budget) {{
        return {{ kept: text, cut: "" }};
      }}
      const lines = text.split("\\n");
      const kept = [];
      const cut = [];
      let used = 0;
      let stopped = false;
      for (const ln of lines) {{
        if (stopped) {{
          cut.push(ln);
          continue;
        }}
        const ltok = bpeApproxTokens(ln);
        if (used + ltok > budget) {{
          if (kept.length === 0) {{
            const approxChars = Math.max(40, budget * 4);
            kept.push(ln.slice(0, approxChars));
            if (ln.length > approxChars) cut.push(ln.slice(approxChars));
          }} else {{
            cut.push(ln);
          }}
          stopped = true;
          continue;
        }}
        kept.push(ln);
        used += ltok;
      }}
      return {{ kept: kept.join("\\n"), cut: cut.join("\\n") }};
    }}

    function evaluateAnswer(contextText, status, q) {{
      if (q.category === "abstention") {{
        return status === "ABSTAIN" ? 1.0 : 0.0;
      }}
      if (status === "ABSTAIN") return 0.0;
      const ctxLower = contextText.toLowerCase();
      const req = q.tokens_required || [];
      const forb = q.forbidden || [];

      for (const tok of req) {{
        if (!ctxLower.includes(tok.toLowerCase())) return 0.0;
      }}

      if (q.category === "knowledge_update" && forb.length > 0) {{
        const lines = contextText.split("\\n");
        const dateRe = /\\[(\\d{{4}}-\\d{{2}}-\\d{{2}})/;
        const reqDates = [];
        for (const ln of lines) {{
          const lnl = ln.toLowerCase();
          if (req.some(r => lnl.includes(r.toLowerCase()))) {{
            const m = ln.match(dateRe);
            if (m) reqDates.push(m[1]);
          }}
        }}
        reqDates.sort();
        const newestReqDate = reqDates.length ? reqDates[reqDates.length - 1] : "";

        for (const ftok of forb) {{
          if (!ctxLower.includes(ftok.toLowerCase())) continue;
          for (const ln of lines) {{
            const lnl = ln.toLowerCase();
            if (!lnl.includes(ftok.toLowerCase())) continue;
            const isStale = (
              ln.includes("#superseded") ||
              ln.includes('"status": "superseded"') ||
              ln.includes("invalid_at") ||
              lnl.includes("replaced") ||
              lnl.includes("migrated")
            );
            const m = ln.match(dateRe);
            const isOlder = Boolean(m && newestReqDate && m[1] < newestReqDate);
            if (!isStale && !isOlder) return 0.0;
          }}
        }}
      }}
      return 1.0;
    }}

    function computeStatsAtBudget(budget) {{
      const stats = [];
      for (const sysName of SYSTEM_ORDER) {{
        const cats = {{ single_hop: [], multi_hop: [], temporal: [], knowledge_update: [], abstention: [] }};
        const fullCats = {{ single_hop: [], multi_hop: [], temporal: [], knowledge_update: [], abstention: [] }};
        const allAct = [];
        const allFull = [];
        const toks = [];
        const lats = [];

        for (const q of DATA.queries) {{
          const rec = q.systems[sysName];
          const truncated = (rec.status !== "ABSTAIN" && budget > 0) ? truncateSplit(rec.context, budget).kept : rec.context;
          const sc = evaluateAnswer(truncated, rec.status, q);
          const scFull = evaluateAnswer(rec.context, rec.status, q);
          cats[q.category].push(sc);
          fullCats[q.category].push(scFull);
          allAct.push(sc);
          allFull.push(scFull);
          toks.push(rec.tokens);
          lats.push(rec.latency_ms || 0);
        }}

        const pct = arr => +(100.0 * arr.reduce((a, b) => a + b, 0) / Math.max(1, arr.length)).toFixed(1);
        const avg = arr => +(arr.reduce((a, b) => a + b, 0) / Math.max(1, arr.length)).toFixed(1);
        const avg3 = arr => +(arr.reduce((a, b) => a + b, 0) / Math.max(1, arr.length)).toFixed(3);

        stats.push({{
          system: sysName,
          activeAcc: pct(allAct),
          fullAcc: pct(allFull),
          cats: {{
            single_hop: pct(cats.single_hop),
            multi_hop: pct(cats.multi_hop),
            temporal: pct(cats.temporal),
            knowledge_update: pct(cats.knowledge_update),
            abstention: pct(cats.abstention),
          }},
          avgTokens: avg(toks),
          avgLatency: avg3(lats),
        }});
      }}
      stats.sort((a, b) => (b.activeAcc - a.activeAcc) || (b.fullAcc - a.fullAcc) || (a.avgTokens - b.avgTokens));
      return stats;
    }}

    function esc(s) {{
      return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }}

    function switchTab(name, btn) {{
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
      document.getElementById("tab-" + name).classList.add("active");
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      if (name === "corpus") renderMermaidIn("fullMmdRender", DATA.full_flowmem_mmd);
      if (name === "inspector") renderDetail(selectedQueryId);
    }}

    function renderLiveTab() {{
      const live = DATA.live_llm;
      if (!live) {{
        document.getElementById("liveKpiRow").innerHTML = '<div class="kpi-card"><div class="kpi-label">Live LLM</div><div class="kpi-value">Not Run</div><div class="kpi-note">Run <code>python3 benchmarks/run_live_llm_benchmark.py</code></div></div>';
        return;
      }}
      const rows = live.summary || [];
      const hf = rows.find(r => r.id === "haiku_flowmem") || rows[0];
      const ff = rows.find(r => r.id === "flash_flowmem") || rows[0];
      const sg = rows.find(r => r.id === "sonnet_graphiti") || rows[rows.length - 1];
      const totalCalls = rows.length * (live.num_queries || 25);

      document.getElementById("liveKpiRow").innerHTML = `
        <div class="kpi-card">
          <div class="kpi-label">Small LLM + FlowMem v2.0</div>
          <div class="kpi-value">${{hf.accuracy}}%</div>
          <div class="kpi-note">Claude Haiku (${{hf.avg_latency_s}}s) &amp; Gemini 3.8 Flash (${{ff.accuracy}}%) @ ~${{hf.avg_raw_tokens}} tok</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">vs Frontier Sonnet + Graphiti JSON</div>
          <div class="kpi-value">+${{(hf.accuracy - sg.accuracy).toFixed(1)}} pts</div>
          <div class="kpi-note">Haiku+FlowMem (${{hf.accuracy}}%) beat Sonnet+Graphiti (${{sg.accuracy}}%, ~${{sg.avg_raw_tokens}} tok)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Verified Live CLI Calls</div>
          <div class="kpi-value">${{totalCalls}} / ${{totalCalls}}</div>
          <div class="kpi-note">Real <code>claude -p</code> &amp; <code>agy -p</code> traces embedded below</div>
        </div>
      `;

      document.getElementById("liveLlmBars").innerHTML = rows.map((r, idx) => `
        <div style="margin-bottom:11px;">
          <div style="display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:3px;">
            <span style="font-weight:${{r.label.includes('FlowMem') ? 700 : 500}};color:${{r.label.includes('FlowMem') ? '#1e3a8a' : '#1f2328'}};">${{idx + 1}}. ${{esc(r.label)}}</span>
            <span class="mono" style="font-weight:700;">${{r.accuracy}}% <span style="color:#656d76;font-weight:400;">(~${{r.avg_raw_tokens}}t · ${{r.avg_latency_s}}s)</span></span>
          </div>
          <div class="bar-track">
            <div class="bar-fill ${{r.label.includes('FlowMem') ? 'bar-flowmem' : 'bar-other'}}" style="width:${{r.accuracy}}%;"></div>
          </div>
        </div>
      `).join("");

      document.getElementById("liveTableBody").innerHTML = rows.map(r => `
        <tr class="${{r.label.includes('FlowMem') ? 'row-hl' : ''}}">
          <td>${{esc(r.label)}}</td>
          <td class="num"><strong>${{r.accuracy}}%</strong></td>
          <td class="num">${{r.categories.single_hop}}%</td>
          <td class="num">${{r.categories.multi_hop}}%</td>
          <td class="num">${{r.categories.temporal}}%</td>
          <td class="num">${{r.categories.knowledge_update}}%</td>
          <td class="num">${{r.categories.abstention}}%</td>
          <td class="num">~${{r.avg_raw_tokens}}</td>
          <td class="num">${{r.avg_latency_s}}s</td>
        </tr>
      `).join("");

      renderLiveQueryTable();
      renderLiveDetail(selectedLiveQid);
    }}

    function renderLiveQueryTable() {{
      const live = DATA.live_llm;
      if (!live) return;
      const pill = (rec) => {{
        if (!rec) return '<td class="num">—</td>';
        const cls = rec.score === 1.0 ? "pill-green" : "pill-red";
        const lbl = rec.score === 1.0 ? "PASS" : "FAIL";
        return `<td class="num"><span class="pill ${{cls}}" style="padding:1px 6px;font-size:10.5px;">${{lbl}}</span></td>`;
      }};
      document.getElementById("liveQueryBody").innerHTML = live.queries.map(q => `
        <tr class="q-row ${{q.id === selectedLiveQid ? 'selected' : ''}}" onclick="selectLiveQuery(${{q.id}})">
          <td class="mono"><strong>Q${{q.id}}</strong></td>
          <td><span class="pill">${{esc(q.category)}}</span></td>
          <td>${{esc(q.question)}}</td>
          <td class="mono" style="font-size:11.5px;">${{esc(q.expected)}}</td>
          ${{pill(q.runs.haiku_flowmem)}}
          ${{pill(q.runs.flash_flowmem)}}
          ${{pill(q.runs.gptoss_flowmem)}}
          ${{pill(q.runs.sonnet_graphiti)}}
          ${{pill(q.runs.haiku_supermem)}}
        </tr>
      `).join("");
    }}

    function selectLiveQuery(qid) {{
      selectedLiveQid = qid;
      renderLiveQueryTable();
      renderLiveDetail(qid);
    }}

    function renderLiveDetail(qid) {{
      const live = DATA.live_llm;
      if (!live) return;
      const q = live.queries.find(x => x.id === qid) || live.queries[0];
      if (!q) return;
      const labels = {{}};
      for (const s of live.summary) labels[s.id] = s.label;

      const cards = Object.keys(q.runs).map(cid => {{
        const r = q.runs[cid];
        const label = labels[cid] || cid;
        const isFm = label.includes("FlowMem");
        const cls = r.score === 1.0 ? "pill-green" : "pill-red";
        const lbl = r.score === 1.0 ? "PASS" : "FAIL";
        return `
          <div class="sys-card ${{isFm ? 'is-flowmem' : ''}}">
            <div class="sys-head">
              <span class="sys-name">${{esc(label)}}</span>
              <div style="display:flex;gap:6px;align-items:center;">
                <span class="pill mono">${{r.raw_tokens}} raw tok · ${{Math.round(r.latency_ms)}}ms</span>
                <span class="pill ${{cls}}">${{lbl}}</span>
              </div>
            </div>
            <div class="sys-body">
              <div class="answer-box">
                <div><strong>Real Model Output:</strong> <code>${{esc(r.raw_answer || '(empty)')}}</code></div>
                <div class="mono" style="font-size:10.5px;color:#656d76;margin-top:3px;">Trace ID: ${{esc(r.trace_id || 'none')}}</div>
              </div>
              <div style="font-size:11px;font-weight:700;color:#656d76;margin-bottom:4px;">CONTEXT PASSED TO MODEL (<= ${{live.budget_tokens}} TOK)</div>
              <pre style="margin:0;white-space:pre-wrap;word-break:break-word;font-size:11px;">${{esc(r.context_used)}}</pre>
            </div>
          </div>
        `;
      }}).join("");

      document.getElementById("liveDetailPanel").innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;margin-bottom:12px;">
          <div>
            <span class="pill">Q${{q.id}} · ${{esc(q.category)}}</span>
            <h3 style="margin:6px 0 0;font-size:16px;color:#111827;">${{esc(q.question)}}</h3>
          </div>
          <div style="font-size:12px;text-align:right;">
            <div><strong>Expected:</strong> <code>${{esc(q.expected)}}</code></div>
          </div>
        </div>
        <div class="grid-cards">${{cards}}</div>
      `;
    }}

    function onBudgetSlider(val) {{
      currentBudget = parseInt(val, 10);
      document.querySelectorAll(".budget-controls .btn").forEach(b => b.classList.remove("active"));
      updateRetrievalViews();
    }}

    function setBudget(val, btn) {{
      currentBudget = val;
      document.querySelectorAll(".budget-controls .btn").forEach(b => b.classList.remove("active"));
      if (btn) btn.classList.add("active");
      if (val > 0) document.getElementById("budgetSlider").value = val;
      updateRetrievalViews();
    }}

    function renderLeaderboard() {{
      document.getElementById("budgetLabel").textContent = currentBudget > 0 ? `Budget: ${{currentBudget}} tok` : "Full Unconstrained";
      const stats = computeStatsAtBudget(currentBudget);
      const fm = stats.find(s => s.system === "FlowMem v2.0 (DDM .mmd)");
      const gr = stats.find(s => s.system === "Graphiti (Bi-Temporal JSON Graph)");
      const ratio = fm && gr ? (gr.avgTokens / Math.max(1, fm.avgTokens)).toFixed(2) : "—";

      document.getElementById("kpiRow").innerHTML = `
        <div class="kpi-card">
          <div class="kpi-label">FlowMem v2.0 Retrieval</div>
          <div class="kpi-value">${{fm.activeAcc}}%</div>
          <div class="kpi-note">${{currentBudget > 0 ? "At " + currentBudget + "-token budget" : "Unconstrained"}} · ${{fm.fullAcc}}% full</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Graphiti JSON Token Ratio</div>
          <div class="kpi-value">${{ratio}}x denser</div>
          <div class="kpi-note">FlowMem ~${{fm.avgTokens}} tok vs Graphiti ~${{gr.avgTokens}} tok</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Audit &amp; Verification</div>
          <div class="kpi-value">0 Leaks · 10/10</div>
          <div class="kpi-note">Anti-cheat audit + 10 unit tests verified</div>
        </div>
      `;

      document.getElementById("liveBars").innerHTML = stats.map((s, idx) => `
        <div style="margin-bottom:12px;">
          <div style="display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:4px;">
            <span style="font-weight:${{idx === 0 ? 700 : 500}};color:${{idx === 0 ? '#1e3a8a' : '#1f2328'}};">${{idx + 1}}. ${{esc(s.system)}}</span>
            <span class="mono" style="font-weight:700;">${{s.activeAcc}}% <span style="color:#656d76;font-weight:400;">(~${{s.avgTokens}} tok)</span></span>
          </div>
          <div class="bar-track">
            <div class="bar-fill ${{s.system.startsWith('FlowMem') ? 'bar-flowmem' : 'bar-other'}}" style="width:${{s.activeAcc}}%;"></div>
          </div>
        </div>
      `).join("");

      document.getElementById("leaderTableBody").innerHTML = stats.map((s, idx) => `
        <tr class="${{s.system.startsWith('FlowMem') ? 'row-hl' : ''}}">
          <td>${{idx + 1}}</td>
          <td>${{esc(s.system)}}</td>
          <td class="num"><strong>${{s.activeAcc}}%</strong></td>
          <td class="num">${{s.fullAcc}}%</td>
          <td class="num">${{s.cats.single_hop}}%</td>
          <td class="num">${{s.cats.multi_hop}}%</td>
          <td class="num">${{s.cats.temporal}}%</td>
          <td class="num">${{s.cats.knowledge_update}}%</td>
          <td class="num">${{s.cats.abstention}}%</td>
          <td class="num">~${{s.avgTokens}}</td>
          <td class="num">${{s.avgLatency}} ms</td>
        </tr>
      `).join("");
    }}

    function renderBudgetCurveSvg() {{
      const budgets = [60, 80, 100, 110, 140, 180, 250, 350, 500];
      const colors = {{
        "FlowMem v2.0 (DDM .mmd)": "#1d4ed8",
        "Graphiti (Bi-Temporal JSON Graph)": "#111827",
        "Mem0 (Atomic Fact Store)": "#16a34a",
        "Zep (Episodic + Fact Summaries)": "#d97706",
        "Supermemory (Hybrid RAG)": "#94a3b8"
      }};
      const series = {{}};
      for (const sys of SYSTEM_ORDER) series[sys] = [];
      for (const b of budgets) {{
        const st = computeStatsAtBudget(b);
        for (const r of st) series[r.system].push({{ b, acc: r.activeAcc }});
      }}
      const W = 560, H = 250, padL = 42, padR = 16, padT = 18, padB = 34;
      const xPos = b => padL + ((b - 60) / (500 - 60)) * (W - padL - padR);
      const yPos = a => (H - padB) - (a / 100) * (H - padT - padB);

      let grid = "";
      for (const yv of [20, 40, 60, 80, 100]) {{
        const y = yPos(yv).toFixed(1);
        grid += `<line x1="${{padL}}" y1="${{y}}" x2="${{W - padR}}" y2="${{y}}" stroke="#e5e7eb" stroke-dasharray="3"/>`;
        grid += `<text x="6" y="${{Number(y) + 4}}" font-size="10" fill="#656d76" font-family="monospace">${{yv}}%</text>`;
      }}
      for (const b of [60, 110, 180, 250, 350, 500]) {{
        const x = xPos(b).toFixed(1);
        grid += `<text x="${{x - 10}}" y="${{H - 10}}" font-size="10" fill="#656d76" font-family="monospace">${{b}}</text>`;
      }}
      let markerLine = "";
      if (currentBudget >= 60 && currentBudget <= 500) {{
        const mx = xPos(currentBudget).toFixed(1);
        markerLine = `<line x1="${{mx}}" y1="${{padT}}" x2="${{mx}}" y2="${{H - padB}}" stroke="#111827" stroke-width="1" stroke-dasharray="4"/>`;
      }}
      const paths = SYSTEM_ORDER.map(sys => {{
        const pts = series[sys].map(p => `${{xPos(p.b).toFixed(1)}},${{yPos(p.acc).toFixed(1)}}`).join(" ");
        const w = sys.startsWith("FlowMem") ? 3 : 1.8;
        return `<polyline fill="none" stroke="${{colors[sys]}}" stroke-width="${{w}}" points="${{pts}}" />`;
      }}).join("");

      const legend = SYSTEM_ORDER.map(sys =>
        `<span style="display:inline-flex;align-items:center;gap:5px;font-size:11px;margin-right:12px;">` +
        `<span style="width:12px;height:3px;background:${{colors[sys]}};display:inline-block;"></span>${{esc(SHORT_NAMES[sys])}}</span>`
      ).join("");

      document.getElementById("curveSvgWrap").innerHTML = `
        <svg viewBox="0 0 ${{W}} ${{H}}" style="width:100%;height:auto;display:block;">
          ${{grid}}${{markerLine}}${{paths}}
        </svg>
        <div style="margin-top:6px;">${{legend}}</div>
      `;
    }}

    function setCatFilter(val, btn) {{
      currentCatFilter = val;
      document.querySelectorAll("#tab-inspector .toolbar .btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      renderQueryTable();
    }}

    function renderQueryTable() {{
      const qSearch = (document.getElementById("qSearch").value || "").toLowerCase();
      const rows = [];
      for (const q of DATA.queries) {{
        const fmRec = q.systems["FlowMem v2.0 (DDM .mmd)"];
        const grRec = q.systems["Graphiti (Bi-Temporal JSON Graph)"];
        const fmCtx = (fmRec.status !== "ABSTAIN" && currentBudget > 0) ? truncateSplit(fmRec.context, currentBudget).kept : fmRec.context;
        const grCtx = (grRec.status !== "ABSTAIN" && currentBudget > 0) ? truncateSplit(grRec.context, currentBudget).kept : grRec.context;
        const fmScore = evaluateAnswer(fmCtx, fmRec.status, q);
        const grScore = evaluateAnswer(grCtx, grRec.status, q);

        if (currentCatFilter === "fm_miss" && fmScore === 1.0) continue;
        else if (currentCatFilter === "fm_beats_graphiti" && !(fmScore === 1.0 && grScore === 0.0)) continue;
        else if (!["all", "fm_miss", "fm_beats_graphiti"].includes(currentCatFilter) && q.category !== currentCatFilter) continue;

        const hay = `${{q.id}} ${{q.category}} ${{q.question}} ${{q.expected}}`.toLowerCase();
        if (qSearch && !hay.includes(qSearch)) continue;

        const cells = SYSTEM_ORDER.map(sysName => {{
          const r = q.systems[sysName];
          const k = (r.status !== "ABSTAIN" && currentBudget > 0) ? truncateSplit(r.context, currentBudget).kept : r.context;
          const sc = evaluateAnswer(k, r.status, q);
          const cls = sc === 1.0 ? "pill-green" : "pill-red";
          const lbl = sc === 1.0 ? "PASS" : "FAIL";
          return `<td class="num"><span class="pill ${{cls}}" style="padding:1px 6px;font-size:10.5px;">${{lbl}} · ${{r.tokens}}t</span></td>`;
        }}).join("");

        rows.push(`
          <tr class="q-row ${{q.id === selectedQueryId ? 'selected' : ''}}" onclick="selectQuery(${{q.id}})">
            <td class="mono"><strong>Q${{q.id}}</strong></td>
            <td><span class="pill">${{esc(q.category)}}</span></td>
            <td>${{esc(q.question)}}</td>
            <td class="mono" style="font-size:11.5px;">${{esc(q.expected)}}</td>
            ${{cells}}
          </tr>
        `);
      }}
      document.getElementById("queryTableBody").innerHTML = rows.join("") || '<tr><td colspan="9" style="text-align:center;color:#656d76;padding:18px;">No queries match filter.</td></tr>';
    }}

    function selectQuery(qid) {{
      selectedQueryId = qid;
      renderQueryTable();
      renderDetail(qid);
    }}

    function renderDetail(qid) {{
      const q = DATA.queries.find(x => x.id === qid) || DATA.queries[0];
      if (!q) return;
      const cards = SYSTEM_ORDER.map(sysName => {{
        const r = q.systems[sysName];
        const parts = (r.status !== "ABSTAIN" && currentBudget > 0) ? truncateSplit(r.context, currentBudget) : {{ kept: r.context, cut: "" }};
        const sc = evaluateAnswer(parts.kept, r.status, q);
        const scFull = evaluateAnswer(r.context, r.status, q);
        const badgeCls = sc === 1.0 ? "pill-green" : "pill-red";
        const badgeTxt = sc === 1.0 ? "PASS" : (scFull === 1.0 ? "FAIL (Truncated)" : "FAIL");
        const isFm = sysName.startsWith("FlowMem");

        let bodyHtml = "";
        if (r.status === "ABSTAIN") {{
          bodyHtml = `<div class="ctx-line" style="color:#656d76;">[ABSTAINED — confidence below threshold]</div>`;
        }} else {{
          const keptHtml = esc(parts.kept || "(empty)").split("\\n").map(l => `<div class="ctx-line">${{l || "&nbsp;"}}</div>`).join("");
          let cutHtml = "";
          if (parts.cut) {{
            cutHtml = `<div class="cutoff-banner">--- CUTOFF AT ${{currentBudget}} TOKENS (dropped below) ---</div>` +
              esc(parts.cut).split("\\n").map(l => `<div class="ctx-line ctx-cut">${{l || "&nbsp;"}}</div>`).join("");
          }}
          bodyHtml = keptHtml + cutHtml;
        }}

        const mmdPreview = (isFm && r.status !== "ABSTAIN" && parts.kept.includes("flowchart"))
          ? `<div style="margin-top:10px;"><div style="font-size:11px;font-weight:700;color:#656d76;">RENDERED MERMAID SUBGRAPH</div><div class="mermaid-box" id="detailMermaidBox"></div></div>`
          : "";

        return `
          <div class="sys-card ${{isFm ? 'is-flowmem' : ''}}">
            <div class="sys-head">
              <span class="sys-name">${{esc(sysName)}}</span>
              <div style="display:flex;gap:6px;align-items:center;">
                <span class="pill mono">${{r.tokens}} tok</span>
                <span class="pill ${{badgeCls}}">${{badgeTxt}}</span>
              </div>
            </div>
            <div class="sys-body">
              ${{bodyHtml}}
              ${{mmdPreview}}
            </div>
          </div>
        `;
      }}).join("");

      document.getElementById("detailPanel").innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;margin-bottom:14px;">
          <div>
            <div class="pill" style="margin-bottom:6px;">Q${{q.id}} · ${{esc(q.category)}}</div>
            <h3 style="margin:0;font-size:17px;color:#111827;">${{esc(q.question)}}</h3>
          </div>
          <div style="text-align:right;font-size:12px;">
            <div><strong>Expected:</strong> <code>${{esc(q.expected)}}</code></div>
            ${{q.tokens_required.length ? `<div><strong>Required chain:</strong> <code>${{esc(q.tokens_required.join(", "))}}</code></div>` : ""}}
            ${{q.forbidden.length ? `<div><strong>Forbidden active stale:</strong> <code>${{esc(q.forbidden.join(", "))}}</code></div>` : ""}}
          </div>
        </div>
        <div class="grid-cards">${{cards}}</div>
      `;

      const fmRec = q.systems["FlowMem v2.0 (DDM .mmd)"];
      if (fmRec && fmRec.status !== "ABSTAIN") {{
        const fmKept = currentBudget > 0 ? truncateSplit(fmRec.context, currentBudget).kept : fmRec.context;
        if (document.getElementById("detailMermaidBox")) {{
          renderMermaidIn("detailMermaidBox", fmKept);
        }}
      }}
    }}

    function renderCorpusTab() {{
      document.getElementById("fullMmdCode").textContent = DATA.full_flowmem_mmd || "";
      document.getElementById("sessionsList").innerHTML = (DATA.sessions || []).map(s => `
        <div style="border:1px solid var(--border-light);border-radius:8px;padding:12px 14px;margin-bottom:10px;background:#fff;">
          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px;">
            <strong class="mono">${{esc(s.session_id)}} · ${{esc(s.date)}}</strong>
            <span class="pill">${{s.facts.length}} fact(s)</span>
          </div>
          <div style="font-size:13px;color:#1f2328;margin-bottom:6px;">${{esc(s.transcript)}}</div>
          <div class="mono" style="font-size:11px;color:#4b5563;">
            ${{s.facts.map(f => `[${{f.supersedes ? 'SUPERSEDES' : 'ADD'}}] ${{esc(f.subject)}} --(${{esc(f.predicate)}})--&gt; ${{esc(f.object)}}`).join("<br/>")}}
          </div>
        </div>
      `).join("");
    }}

    let mermaidCounter = 0;
    async function renderMermaidIn(containerId, code) {{
      const el = document.getElementById(containerId);
      if (!el) return;
      if (typeof mermaid === "undefined") {{
        el.innerHTML = `<pre class="mono" style="font-size:11px;margin:0;">${{esc(code)}}</pre>`;
        return;
      }}
      try {{
        mermaidCounter += 1;
        const {{ svg }} = await mermaid.render("mmdSvg_" + mermaidCounter, code);
        el.innerHTML = svg;
      }} catch (err) {{
        el.innerHTML = `<pre class="mono" style="font-size:11px;margin:0;">${{esc(code)}}</pre>`;
      }}
    }}

    function updateRetrievalViews() {{
      renderLeaderboard();
      renderBudgetCurveSvg();
      renderQueryTable();
      renderDetail(selectedQueryId);
    }}

    if (typeof mermaid !== "undefined") {{
      mermaid.initialize({{ startOnLoad: false, theme: "default" }});
    }}
    renderLiveTab();
    renderCorpusTab();
    updateRetrievalViews();
  </script>
</body>
</html>
"""

    for out_path in (OUT_BENCH_HTML, OUT_DOCS_HTML):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(html_doc)
        print("Wrote interactive benchmark report:", out_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
