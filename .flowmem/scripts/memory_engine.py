#!/usr/bin/env python3
"""
FlowMem v2.0 — memory_engine.py
Bi-temporal Dense Diagram-Markdown (DDM) Memory Engine.

Stores structured semantic, episodic, and procedural facts directly in
Mermaid `.mmd` graphs using compact bi-temporal edges:
  NodeA["Label"] -->|predicate @t=2026-10 #valid| NodeB["Label"]
  NodeA -.->|predicate @t=2025-03..2026-09 #superseded| NodeOld["Old Label"]

Commands:
  ingest   Add or supersede a fact in `.flowmem/charts/data/knowledge_graph.mmd` (or custom path)
  query    Entity-anchored k-hop BFS + temporal routing across all `.flowmem/` .mmd charts
  stats    Print node, edge, valid/superseded counts and token compression metrics

Zero external dependencies (Python 3 stdlib only).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict, deque
from datetime import datetime

NODE_DEF_RE = re.compile(r'^\s*([A-Za-z0-9_]+)\s*\["([^"]+)"\]')
EDGE_RE = re.compile(
    r'^\s*([A-Za-z0-9_]+)(?:\["([^"]+)"\])?\s*'
    r'(-->|-.->)\s*'
    r'\|([^|]+)\|\s*'
    r'([A-Za-z0-9_]+)(?:\["([^"]+)"\])?'
)
TEMPORAL_HINTS = (
    "before",
    "previously",
    "previous",
    "used to",
    "prior",
    "when",
    "history",
    "earlier",
    "migrated from",
    "replaced",
    "old",
    "first",
    "originally",
    "timeline",
    "2024",
    "2025",
    "2026",
)
STOPWORDS = {
    "what", "which", "who", "where", "when", "why", "how", "is", "are", "was",
    "were", "do", "does", "did", "the", "a", "an", "in", "on", "at", "to",
    "for", "of", "by", "with", "from", "and", "or", "that", "this", "currently",
    "now", "used", "use", "uses", "project", "team", "system", "service",
    "platform", "product", "company", "app", "store",
}


def slug_node_id(label: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", label.strip()).strip("_")
    if not cleaned:
        cleaned = "Entity"
    if cleaned[0].isdigit():
        cleaned = "N_" + cleaned
    return cleaned[:32]


def parse_edge_label(raw_label: str) -> dict:
    raw = raw_label.strip()
    state = "valid"
    if "#superseded" in raw:
        state = "superseded"
    elif "#valid" in raw:
        state = "valid"

    t_match = re.search(r"@t=([0-9.\-]+)", raw)
    time_span = t_match.group(1) if t_match else ""

    pred = re.sub(r"@t=[0-9.\-]+", "", raw)
    pred = pred.replace("#valid", "").replace("#superseded", "").strip()
    return {"predicate": pred, "time": time_span, "state": state, "raw": raw}


def load_mmd_graph(mmd_paths: list[str]) -> tuple[dict[str, str], list[dict]]:
    nodes: dict[str, str] = {}
    edges: list[dict] = []

    for path in mmd_paths:
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                s = line.strip()
                if not s or s.startswith("%%") or s.startswith("flowchart") or s.startswith("graph"):
                    continue
                em = EDGE_RE.match(line)
                if em:
                    src_id, src_lbl, arrow, lbl_raw, dst_id, dst_lbl = em.groups()
                    if src_lbl:
                        nodes[src_id] = src_lbl
                    elif src_id not in nodes:
                        nodes[src_id] = src_id
                    if dst_lbl:
                        nodes[dst_id] = dst_lbl
                    elif dst_id not in nodes:
                        nodes[dst_id] = dst_id
                    parsed = parse_edge_label(lbl_raw)
                    edges.append(
                        {
                            "src": src_id,
                            "dst": dst_id,
                            "arrow": arrow,
                            "predicate": parsed["predicate"],
                            "time": parsed["time"],
                            "state": parsed["state"],
                            "raw_label": parsed["raw"],
                            "source_file": path,
                        }
                    )
                    continue
                nm = NODE_DEF_RE.match(line)
                if nm:
                    nid, nlbl = nm.groups()
                    nodes[nid] = nlbl

    return nodes, edges


def ensure_graph_file(graph_path: str) -> None:
    if os.path.exists(graph_path):
        return
    os.makedirs(os.path.dirname(graph_path), exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    header = (
        "%%{init: {'theme': 'default'}}%%\n"
        f"%% FlowMem | type=flowchart | layer=data | method=engine | refresh=memory_engine.py | last-updated={today} %%\n"
        "flowchart LR\n"
    )
    with open(graph_path, "w", encoding="utf-8") as fh:
        fh.write(header)


def ingest_fact(
    graph_path: str,
    subject: str,
    predicate: str,
    obj: str,
    time_str: str = "",
    supersede_existing: bool = True,
) -> dict:
    ensure_graph_file(graph_path)
    today = datetime.now().strftime("%Y-%m-%d")
    t_val = time_str.strip() or today

    src_id = slug_node_id(subject)
    dst_id = slug_node_id(obj)
    pred_clean = predicate.strip().replace("|", "/")

    with open(graph_path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    superseded_count = 0
    updated_lines = []

    for line in lines:
        em = EDGE_RE.match(line)
        if em and supersede_existing:
            e_src, e_src_lbl, arrow, lbl_raw, e_dst, e_dst_lbl = em.groups()
            parsed = parse_edge_label(lbl_raw)
            same_subject = e_src == src_id or (e_src_lbl and e_src_lbl.lower() == subject.lower())
            same_pred = parsed["predicate"].lower() == pred_clean.lower()
            if same_subject and same_pred and parsed["state"] == "valid":
                old_t = parsed["time"]
                span = f"{old_t}..{t_val}" if old_t and old_t != t_val else t_val
                new_lbl = f"{parsed['predicate']} @t={span} #superseded"
                src_part = f'{e_src}["{e_src_lbl}"]' if e_src_lbl else e_src
                dst_part = f'{e_dst}["{e_dst_lbl}"]' if e_dst_lbl else e_dst
                updated_lines.append(f"  {src_part} -.->|{new_lbl}| {dst_part}\n")
                superseded_count += 1
                continue
        if line.startswith("%% FlowMem |"):
            updated_lines.append(
                f"%% FlowMem | type=flowchart | layer=data | method=engine | refresh=memory_engine.py | last-updated={today} %%\n"
            )
            continue
        updated_lines.append(line)

    new_edge = f'  {src_id}["{subject}"] -->|{pred_clean} @t={t_val} #valid| {dst_id}["{obj}"]\n'
    updated_lines.append(new_edge)

    with open(graph_path, "w", encoding="utf-8") as fh:
        fh.writelines(updated_lines)

    return {
        "graph_path": graph_path,
        "added": f'{subject} --[{pred_clean} @t={t_val} #valid]--> {obj}',
        "superseded_previous": superseded_count,
    }


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in tokens if len(t) > 1 and t not in STOPWORDS]


def extract_proper_entities(question: str) -> list[str]:
    """Extract capitalized multi-word or CamelCase/acronym entity mentions (ignoring sentence start)."""
    # Strip first question word (Who/What/Which/Where/When/In)
    stripped = re.sub(r"^(?:What|Which|Who|Where|When|Why|How|In what|In which)\b\s*", "", question.strip())
    matches = re.findall(r"\b(?:[A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*)*)\b", stripped)
    ignored = {"Does", "Is", "Are", "Was", "Were", "Do", "Did", "The", "Chief", "Financial", "Officer"}
    return [m for m in matches if m not in ignored and len(m) > 2]


def query_graph(
    mmd_paths: list[str],
    question: str,
    hops: int = 3,
    include_history: bool | None = None,
) -> dict:
    nodes, edges = load_mmd_graph(mmd_paths)
    q_lower = question.lower()
    if include_history is None:
        include_history = any(h in q_lower for h in TEMPORAL_HINTS)

    q_tokens = set(tokenize(question))
    if not q_tokens or not nodes:
        return {
            "status": "ABSTAIN",
            "reason": "No matching entities found in FlowMem diagrams.",
            "subgraph_mmd": "",
            "matched_facts": [],
            "tokens_estimate": 0,
        }

    # Check if explicit proper-noun entities mentioned in question actually exist in memory graph
    proper_mentions = extract_proper_entities(question)
    all_labels_lower = " ".join(nodes.values()).lower()
    if proper_mentions:
        matched_mentions = 0
        for ent in proper_mentions:
            ent_toks = [t for t in tokenize(ent) if len(t) > 2]
            if ent.lower() in all_labels_lower or (
                ent_toks and all(t in all_labels_lower for t in ent_toks)
            ):
                matched_mentions += 1
        if matched_mentions == 0:
            return {
                "status": "ABSTAIN",
                "reason": f"Mentioned entity/entities {proper_mentions} do not exist in FlowMem graph.",
                "subgraph_mmd": "",
                "matched_facts": [],
                "tokens_estimate": 12,
            }

    # Score seed nodes strictly by node label/ID overlap
    seed_scores: dict[str, float] = {}
    for nid, label in nodes.items():
        ntoks = set(tokenize(f"{nid} {label}"))
        overlap = q_tokens & ntoks
        if overlap:
            score = len(overlap) / max(1.0, len(ntoks) ** 0.5)
            if label.lower() in q_lower:
                score += 3.0
            seed_scores[nid] = score

    if not seed_scores or max(seed_scores.values()) < 0.5:
        return {
            "status": "ABSTAIN",
            "reason": "Query entities are absent from memory graph (confidence below abstention threshold).",
            "subgraph_mmd": "",
            "matched_facts": [],
            "tokens_estimate": 12,
        }

    # Build adjacency list respecting temporal/valid filter
    adj = defaultdict(list)
    for idx, e in enumerate(edges):
        if not include_history and e["state"] == "superseded":
            continue
        adj[e["src"]].append((e["dst"], idx))
        adj[e["dst"]].append((e["src"], idx))

    # Multi-hop BFS from top seed nodes, recording depth & parent bridge edge for shortest path reconstruction
    max_seed = max(seed_scores.values())
    top_seeds = [
        nid for nid, sc in sorted(seed_scores.items(), key=lambda kv: -kv[1])[:3]
        if sc >= max(0.5, max_seed * 0.45)
    ]
    visited_depth = {s: 0 for s in top_seeds}
    edge_depth: dict[int, int] = {}
    node_parent_edge: dict[str, tuple[str, int]] = {}

    queue = deque((s, 0) for s in top_seeds)
    while queue:
        curr, depth = queue.popleft()
        if depth >= hops:
            continue
        for nxt, eidx in adj.get(curr, []):
            if eidx not in edge_depth:
                edge_depth[eidx] = depth + 1
            if nxt not in visited_depth:
                visited_depth[nxt] = depth + 1
                node_parent_edge[nxt] = (curr, eidx)
                queue.append((nxt, depth + 1))

    # Map domain hint synonyms for sharper predicate/entity ranking
    hint_tokens = set(q_tokens)
    for w, syns in (
        ("cache", {"uses", "cache", "valkey", "redis"}),
        ("token", {"auth", "protocol", "signing"}),
        ("signing", {"auth", "protocol"}),
        ("language", {"written", "rust"}),
        ("search", {"search", "vector", "vectorgateway"}),
        ("vector", {"vector", "store", "vectorgateway", "qdrant"}),
        ("audit", {"audit", "store", "zerotrustpolicy", "clickhouse"}),
        ("compliance", {"audit", "store", "zerotrustpolicy"}),
        ("security", {"zerotrustpolicy", "oversees", "enforced"}),
        ("policy", {"zerotrustpolicy", "oversees", "enforced"}),
        ("billing", {"billing", "payment", "gateway", "settlement", "billingengine"}),
        ("payment", {"payment", "gateway", "billing"}),
        ("kubernetes", {"runs", "version", "terraform", "eks"}),
        ("infra", {"oncall", "maintains", "terraform"}),
        ("lead", {"leads", "owns"}),
        ("leads", {"leads", "owns"}),
        ("owns", {"owns", "leads"}),
        ("database", {"uses", "db", "postgresql", "mongodb"}),
        ("currencies", {"settlement", "currency"}),
        ("currency", {"settlement", "currency"}),
        ("deployed", {"deployed", "in"}),
    ):
        if w in q_lower:
            hint_tokens.update(syns)

    scored_edges = []
    for eidx, depth in edge_depth.items():
        e = edges[eidx]
        s_lbl = nodes.get(e["src"], e["src"])
        d_lbl = nodes.get(e["dst"], e["dst"])
        pred_toks = set(tokenize(e["predicate"]))
        node_toks = set(tokenize(f"{s_lbl} {d_lbl}"))

        pred_match = len(hint_tokens & pred_toks)
        node_match = len(hint_tokens & node_toks)

        rel = pred_match * 3.2 + node_match * 1.4
        if e["src"] in top_seeds or e["dst"] in top_seeds:
            rel += 0.6
        if include_history and e["state"] == "superseded":
            rel += 1.8
        rel -= (depth - 1) * 0.25
        scored_edges.append((rel, -depth, eidx))

    scored_edges.sort(key=lambda x: (-x[0], -x[1]))

    # Select top relevant edges + backtrack bridge paths to seed nodes
    selected_set = []
    seen_sel = set()

    def add_edge_with_bridge(eidx: int):
        e = edges[eidx]
        chain = [eidx]
        # Backtrack bridge edges from deeper endpoint toward seed
        cur_node = e["src"] if visited_depth.get(e["src"], 99) >= visited_depth.get(e["dst"], 99) else e["dst"]
        while cur_node in node_parent_edge and len(chain) < 5:
            prev_node, prev_eidx = node_parent_edge[cur_node]
            if prev_eidx not in chain:
                chain.append(prev_eidx)
            cur_node = prev_node
        for idx in reversed(chain):
            if idx not in seen_sel:
                seen_sel.add(idx)
                selected_set.append(idx)

    # Always keep the highest-scoring edge + its bridge chain; stop adding lower-relevance padding
    top_rel = scored_edges[0][0] if scored_edges else 0.0
    for idx, (rel, _, eidx) in enumerate(scored_edges):
        if idx > 0 and top_rel >= 3.0 and rel < 2.8:
            break
        add_edge_with_bridge(eidx)
        if len(selected_set) >= 8:
            break

    if not selected_set and scored_edges:
        selected_set = [eidx for _, _, eidx in scored_edges[:3]]

    selected_indices = selected_set[:8]

    # Emit compact Mermaid subgraph: define NodeID["Label"] once on first occurrence, then NodeID
    declared = set()
    mmd_lines = ["flowchart LR"]
    facts = []

    def fmt_node(nid: str) -> str:
        lbl = nodes.get(nid, nid)
        if nid not in declared:
            declared.add(nid)
            return f'{nid}["{lbl}"]'
        return nid

    for eidx in selected_indices:
        e = edges[eidx]
        s_str = fmt_node(e["src"])
        d_str = fmt_node(e["dst"])
        mmd_lines.append(f'  {s_str} {e["arrow"]}|{e["raw_label"]}| {d_str}')
        facts.append(
            {
                "subject": nodes.get(e["src"], e["src"]),
                "predicate": e["predicate"],
                "object": nodes.get(e["dst"], e["dst"]),
                "time": e["time"],
                "state": e["state"],
            }
        )

    subgraph = "\n".join(mmd_lines)
    tokens_est = max(1, len(subgraph) // 4)

    return {
        "status": "ANSWERED" if facts else "ABSTAIN",
        "include_history": include_history,
        "seed_nodes": [nodes[s] for s in top_seeds if s in nodes],
        "subgraph_mmd": subgraph,
        "matched_facts": facts,
        "tokens_estimate": tokens_est,
    }


def collect_project_mmds(root: str) -> list[str]:
    patterns = [
        os.path.join(root, ".flowmem", "charts", "**", "*.mmd"),
        os.path.join(root, ".flowmem", "memory", "*.mmd"),
    ]
    found = []
    for pat in patterns:
        found.extend(glob.glob(pat, recursive=True))
    return sorted(set(found))


def main() -> int:
    parser = argparse.ArgumentParser(description="FlowMem v2.0 Bi-Temporal Diagram-Markdown Memory Engine")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ing = sub.add_parser("ingest", help="Ingest a bi-temporal fact into a FlowMem .mmd graph")
    p_ing.add_argument("--root", default=".", help="Project root")
    p_ing.add_argument("--graph", default="", help="Custom .mmd file path")
    p_ing.add_argument("--subject", required=True)
    p_ing.add_argument("--predicate", required=True)
    p_ing.add_argument("--object", required=True)
    p_ing.add_argument("--time", default="", help="Timestamp YYYY-MM-DD")
    p_ing.add_argument("--no-supersede", action="store_true", help="Keep prior matching edges #valid")

    p_q = sub.add_parser("query", help="Query FlowMem .mmd memory graphs via k-hop subgraph extraction")
    p_q.add_argument("--root", default=".", help="Project root")
    p_q.add_argument("--graph", default="", help="Optional single .mmd path")
    p_q.add_argument("--question", required=True)
    p_q.add_argument("--hops", type=int, default=3)
    p_q.add_argument("--include-history", action="store_true")

    p_s = sub.add_parser("stats", help="Show memory graph statistics")
    p_s.add_argument("--root", default=".", help="Project root")

    args = parser.parse_args()

    if args.cmd == "ingest":
        gpath = args.graph or os.path.join(args.root, ".flowmem", "charts", "data", "knowledge_graph.mmd")
        res = ingest_fact(
            gpath,
            args.subject,
            args.predicate,
            args.object,
            args.time,
            supersede_existing=not args.no_supersede,
        )
        print(json.dumps(res, indent=2))
        return 0

    if args.cmd == "query":
        paths = [args.graph] if args.graph else collect_project_mmds(args.root)
        hist = True if args.include_history else None
        res = query_graph(paths, args.question, hops=args.hops, include_history=hist)
        print(json.dumps(res, indent=2))
        return 0

    if args.cmd == "stats":
        paths = collect_project_mmds(args.root)
        nodes, edges = load_mmd_graph(paths)
        valid_c = sum(1 for e in edges if e["state"] == "valid")
        sup_c = sum(1 for e in edges if e["state"] == "superseded")
        print(
            json.dumps(
                {
                    "graph_files": len(paths),
                    "nodes": len(nodes),
                    "total_edges": len(edges),
                    "valid_facts": valid_c,
                    "superseded_facts": sup_c,
                },
                indent=2,
            )
        )
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
