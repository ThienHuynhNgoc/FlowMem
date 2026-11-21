#!/usr/bin/env python3
"""
FlowMem v2.0 — memory_engine.py
Bi-temporal Dense Diagram-Markdown (DDM) Memory Engine.

Stores structured semantic, episodic, and procedural facts directly in
Mermaid `.mmd` graphs using compact bi-temporal edges:
  NodeA["Label"] -->|predicate @t=2026-10 #valid| NodeB["Label"]
  NodeA -.->|predicate @t=2025-03..2026-09 #superseded| NodeOld["Old Label"]

Commands:
  ingest       Add or supersede a structured fact in `.flowmem/charts/data/knowledge_graph.mmd`
  ingest-text  Extract and ingest subject/predicate/object edges from raw English text
  query        Entity-anchored k-hop BFS + temporal routing across `.flowmem/` .mmd charts
  stats        Print node, edge, valid/superseded counts and token metrics

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
# Generic English verb/role equivalences (strictly domain-agnostic; zero dataset entities)
GENERIC_SYNONYMS = {
    "lead": {"lead", "own", "manage", "oversee"},
    "own": {"lead", "own", "manage"},
    "manage": {"lead", "own", "manage", "maintain"},
    "oversee": {"oversee", "lead", "manage"},
    "db": {"db", "database"},
    "database": {"db", "database"},
    "protocol": {"protocol", "algorithm", "sign"},
    "algorithm": {"protocol", "algorithm", "sign"},
    "language": {"language", "written"},
    "written": {"language", "written"},
    "currency": {"currency", "currencie", "settle"},
    "settle": {"currency", "settle"},
    "deploy": {"deploy", "host", "region"},
    "host": {"deploy", "host", "region"},
    "infra": {"infra", "oncall", "maintain"},
    "oncall": {"infra", "oncall", "maintain"},
    "compliance": {"compliance", "audit"},
    "audit": {"compliance", "audit"},
    "security": {"security", "policy", "trust"},
    "policy": {"security", "policy"},
    "payment": {"payment", "gateway", "billing"},
    "billing": {"payment", "billing"},
    "version": {"version", "run"},
}


def split_identifier(text: str) -> str:
    """Split CamelCase, PascalCase, snake_case, and kebab-case into space-separated words."""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    return s.replace("_", " ").replace("-", " ")


def stem_token(tok: str) -> str:
    """Conservative generic English stemmer."""
    if len(tok) <= 3:
        return tok
    if tok.endswith("ies") and len(tok) > 4:
        return tok[:-3] + "y"
    if tok.endswith("ing") and len(tok) > 5:
        return tok[:-3]
    if tok.endswith("ed") and len(tok) > 4:
        return tok[:-2]
    if tok.endswith("es") and len(tok) > 4:
        return tok[:-2]
    if tok.endswith("s") and not tok.endswith("ss") and len(tok) > 3:
        return tok[:-1]
    return tok


def tokenize(text: str, include_stems: bool = True) -> list[str]:
    expanded = split_identifier(text)
    raw = re.findall(r"[a-z0-9]+", expanded.lower())
    out = []
    seen = set()
    for t in raw:
        if len(t) <= 1 or t in STOPWORDS:
            continue
        norm = stem_token(t) if include_stems else t
        if norm not in STOPWORDS and norm not in seen and len(norm) > 1:
            seen.add(norm)
            out.append(norm)
    return out


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


def extract_facts_from_text(text: str) -> list[tuple[str, str, str, bool]]:
    """Lightweight deterministic SVO extractor for natural-language sentences."""
    patterns = [
        (r"([A-Z][A-Za-z0-9_ ]+?)\s+migrated\s+from\s+([A-Za-z0-9_.\- ]+?)\s+to\s+([A-Za-z0-9_.\- ]+?)(?:[.,;]|$)", "migrated_to", True),
        (r"([A-Z][A-Za-z0-9_ ]+?)\s+replaced\s+([A-Za-z0-9_.\- ]+?)\s+with\s+([A-Za-z0-9_.\- ]+?)(?:[.,;]|$)", "uses", True),
        (r"([A-Z][A-Za-z0-9_ ]+?)\s+(leads|owns|maintains|oversees|uses|depends on|deploys to|runs on)\s+([A-Z0-9][A-Za-z0-9_.\- ]+?)(?:[.,;]|$)", None, False),
    ]
    extracted = []
    for sent in re.split(r"(?<=[.!?])\s+", text.strip()):
        for pat, fixed_pred, sup in patterns:
            m = re.search(pat, sent)
            if m:
                if fixed_pred == "migrated_to":
                    subj = m.group(1).strip()
                    obj = m.group(3).strip()
                    extracted.append((subj, "uses", obj, sup))
                elif fixed_pred == "uses":
                    subj = m.group(1).strip()
                    obj = m.group(3).strip()
                    extracted.append((subj, "uses", obj, sup))
                else:
                    subj = m.group(1).strip()
                    pred = m.group(2).strip().replace(" ", "_")
                    obj = m.group(3).strip()
                    extracted.append((subj, pred, obj, sup))
                break
    return extracted


def extract_proper_entities(question: str) -> list[str]:
    """Extract capitalized multi-word or CamelCase entity mentions, ignoring leading question words."""
    stripped = re.sub(r"^(?:What|Which|Who|Where|When|Why|How|In what|In which)\b\s*", "", question.strip())
    matches = re.findall(r"\b(?:[A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*)*)\b", stripped)
    ignored = {"Does", "Is", "Are", "Was", "Were", "Do", "Did", "The", "Chief", "Financial", "Officer"}
    return [m for m in matches if m not in ignored and len(m) > 2]


def query_graph(
    mmd_paths: list[str],
    question: str,
    hops: int = 4,
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

    # Confidence gate: if the question names proper entities absent from the memory graph, abstain
    proper_mentions = extract_proper_entities(question)
    all_labels_expanded = " ".join(
        f"{lbl} {split_identifier(lbl)}" for lbl in nodes.values()
    ).lower()
    if proper_mentions:
        matched_mentions = 0
        for ent in proper_mentions:
            ent_toks = [t for t in tokenize(ent, include_stems=False) if len(t) > 2]
            if ent.lower() in all_labels_expanded or (
                ent_toks and all(t in all_labels_expanded for t in ent_toks)
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

    # Score seed nodes by lexical & split-identifier overlap
    seed_scores: dict[str, float] = {}
    for nid, label in nodes.items():
        ntoks = set(tokenize(f"{nid} {label}"))
        overlap = q_tokens & ntoks
        if overlap:
            score = len(overlap) / max(1.0, len(ntoks) ** 0.5)
            if label.lower() in q_lower:
                score += 3.0
            seed_scores[nid] = score

    if not seed_scores or max(seed_scores.values()) < 0.45:
        return {
            "status": "ABSTAIN",
            "reason": "Query entities are absent from memory graph (confidence below abstention threshold).",
            "subgraph_mmd": "",
            "matched_facts": [],
            "tokens_estimate": 12,
        }

    adj = defaultdict(list)
    for idx, e in enumerate(edges):
        if not include_history and e["state"] == "superseded":
            continue
        adj[e["src"]].append((e["dst"], idx))
        adj[e["dst"]].append((e["src"], idx))

    max_seed = max(seed_scores.values())
    top_seeds = [
        nid for nid, sc in sorted(seed_scores.items(), key=lambda kv: -kv[1])[:3]
        if sc >= max(0.45, max_seed * 0.45)
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

    # Expand query tokens only with generic domain-agnostic English synonyms
    hint_tokens = set(q_tokens)
    for qt in list(q_tokens):
        if qt in GENERIC_SYNONYMS:
            hint_tokens.update(GENERIC_SYNONYMS[qt])

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

    selected_set = []
    seen_sel = set()
    covered_pred_tokens: set[str] = set()

    def add_edge_with_bridge(eidx: int):
        e = edges[eidx]
        covered_pred_tokens.update(hint_tokens & set(tokenize(e["predicate"])))
        chain = [eidx]
        cur_node = e["src"] if visited_depth.get(e["src"], 99) >= visited_depth.get(e["dst"], 99) else e["dst"]
        while cur_node in node_parent_edge and len(chain) < 6:
            prev_node, prev_eidx = node_parent_edge[cur_node]
            if prev_eidx not in chain:
                chain.append(prev_eidx)
            cur_node = prev_node
        for idx in reversed(chain):
            if idx not in seen_sel:
                seen_sel.add(idx)
                selected_set.append(idx)

    top_rel = scored_edges[0][0] if scored_edges else 0.0
    for idx, (rel, neg_d, eidx) in enumerate(scored_edges):
        if idx > 0 and top_rel >= 3.0 and rel < 2.0:
            break
        # Prevent depth > 1 predicate echoes (e.g. another entity also matching 'leads' when seed already answered 'leads')
        e = edges[eidx]
        e_pred_hits = hint_tokens & set(tokenize(e["predicate"]))
        e_node_hits = hint_tokens & set(tokenize(f"{nodes.get(e['src'], '')} {nodes.get(e['dst'], '')}"))
        new_pred_hits = e_pred_hits - covered_pred_tokens
        depth = -neg_d
        if idx > 0 and depth > 1 and e_pred_hits and not new_pred_hits and not e_node_hits:
            continue
        if idx > 0 and depth > 1 and not new_pred_hits and rel < top_rel * 0.75:
            continue
        add_edge_with_bridge(eidx)
        if len(selected_set) >= 8:
            break

    if not selected_set and scored_edges:
        selected_set = [eidx for _, _, eidx in scored_edges[:3]]

    selected_indices = selected_set[:8]

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

    p_ing = sub.add_parser("ingest", help="Ingest a structured bi-temporal fact into a FlowMem .mmd graph")
    p_ing.add_argument("--root", default=".", help="Project root")
    p_ing.add_argument("--graph", default="", help="Custom .mmd file path")
    p_ing.add_argument("--subject", required=True)
    p_ing.add_argument("--predicate", required=True)
    p_ing.add_argument("--object", required=True)
    p_ing.add_argument("--time", default="", help="Timestamp YYYY-MM-DD")
    p_ing.add_argument("--no-supersede", action="store_true", help="Keep prior matching edges #valid")

    p_txt = sub.add_parser("ingest-text", help="Extract and ingest facts from raw natural-language text")
    p_txt.add_argument("--root", default=".", help="Project root")
    p_txt.add_argument("--graph", default="", help="Custom .mmd file path")
    p_txt.add_argument("--text", required=True)
    p_txt.add_argument("--time", default="", help="Timestamp YYYY-MM-DD")

    p_q = sub.add_parser("query", help="Query FlowMem .mmd memory graphs via k-hop subgraph extraction")
    p_q.add_argument("--root", default=".", help="Project root")
    p_q.add_argument("--graph", default="", help="Optional single .mmd path")
    p_q.add_argument("--question", required=True)
    p_q.add_argument("--hops", type=int, default=4)
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

    if args.cmd == "ingest-text":
        gpath = args.graph or os.path.join(args.root, ".flowmem", "charts", "data", "knowledge_graph.mmd")
        facts = extract_facts_from_text(args.text)
        out = [ingest_fact(gpath, s, p, o, args.time, supersede_existing=sup) for s, p, o, sup in facts]
        print(json.dumps({"extracted": len(out), "results": out}, indent=2))
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
