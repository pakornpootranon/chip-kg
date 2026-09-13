#!/usr/bin/env python3
"""Validate data/nodes.csv and data/edges.csv against the CLAUDE.md ontology.

Exit 0 if clean, exit 1 with a readable list of failures otherwise.
Run before every commit: python scripts/validate.py
"""

import csv
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NODES_CSV = REPO_ROOT / "data" / "nodes.csv"
EDGES_CSV = REPO_ROOT / "data" / "edges.csv"

PREFIX = {"Company": "co:", "Layer": "ly:", "Technology": "te:", "Country": "cn:",
          "Chokepoint": "cp:", "NewsItem": "nw:"}
CONFIDENCE = {"high", "medium", "low"}
TIERS = {"1", "2", "3"}
LAYERS = ["EDA", "IP", "Equipment", "Materials", "Foundry", "IDM", "Memory", "Packaging", "Fabless", "EndDemand"]
EDGE_SHAPES = {
    "OPERATES_IN": ("Company", "Layer"),
    "SUPPLIES": ("Company", "Company"),
    "COMPETES_WITH": ("Company", "Company"),
    "DEPENDS_ON": ("Company", "Technology"),
    "HQ_IN": ("Company", "Country"),
    "CONTROLS": ("Company", "Chokepoint"),
}
LIST_FIELDS = ("key_products", "key_customers", "fab_or_ops_geography")
REQUIRED = {
    "Company": ("name", "ticker", "exchange", "country", "layer", "sub_segment", "tier", "chokepoint",
                "description", "key_products", "key_customers", "fab_or_ops_geography", "source"),
    "Layer": ("name", "order"),
    "Technology": ("name",),
    "Country": ("name", "code"),
    "Chokepoint": ("name", "layer"),
}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    fails = []
    nodes, edges = rows(NODES_CSV), rows(EDGES_CSV)
    by_id = {}

    # ---- nodes ----
    for i, n in enumerate(nodes, 2):
        nid, label = n["id"], n["label"]
        if label not in PREFIX:
            fails.append(f"nodes.csv:{i}: unknown label '{label}'")
            continue
        if not nid.startswith(PREFIX[label]) or len(nid) <= len(PREFIX[label]):
            fails.append(f"nodes.csv:{i}: id '{nid}' must start with '{PREFIX[label]}' for {label}")
        if nid in by_id:
            fails.append(f"nodes.csv:{i}: duplicate id '{nid}'")
        by_id[nid] = n
        for col in REQUIRED.get(label, ()):
            if not n.get(col, "").strip():
                fails.append(f"nodes.csv:{i}: {label} '{n.get('name', nid)}' missing '{col}'")
        if label == "Company":
            if n["tier"] not in TIERS:
                fails.append(f"nodes.csv:{i}: '{n['name']}' tier '{n['tier']}' not in 1/2/3")
            if n["chokepoint"] not in ("true", "false"):
                fails.append(f"nodes.csv:{i}: '{n['name']}' chokepoint must be true or false")
            if n["layer"] not in LAYERS:
                fails.append(f"nodes.csv:{i}: '{n['name']}' layer '{n['layer']}' not one of {LAYERS}")
            for col in LIST_FIELDS:
                parts = [p.strip() for p in n[col].split("|")]
                if any(p == "" for p in parts):
                    fails.append(f"nodes.csv:{i}: '{n['name']}' {col} has an empty list item: {n[col]!r}")
            if "—" in n["description"]:
                fails.append(f"nodes.csv:{i}: '{n['name']}' description contains an em dash")
        if label == "Layer" and not n["order"].isdigit():
            fails.append(f"nodes.csv:{i}: Layer '{n['name']}' order must be an integer")
        if label == "Country" and not re.fullmatch(r"[A-Z]{2}", n["code"]):
            fails.append(f"nodes.csv:{i}: Country '{n['name']}' code must be ISO2")
        if label == "Chokepoint" and n["layer"] not in LAYERS:
            fails.append(f"nodes.csv:{i}: Chokepoint '{n['name']}' layer '{n['layer']}' unknown")

    names = Counter((n["label"], n["name"]) for n in nodes)
    for (label, name), c in names.items():
        if c > 1:
            fails.append(f"duplicate name '{name}' for label {label} ({c} nodes)")
    tickers = Counter(n["ticker"] for n in nodes if n["label"] == "Company" and n["ticker"])
    for t, c in tickers.items():
        if c > 1:
            fails.append(f"duplicate ticker '{t}' ({c} companies)")

    layer_name_by_id = {n["id"]: n["name"] for n in nodes if n["label"] == "Layer"}
    country_code_by_id = {n["id"]: n["code"] for n in nodes if n["label"] == "Country"}
    country_codes = set(country_code_by_id.values())
    for n in nodes:
        if n["label"] == "Company" and n["country"] not in country_codes:
            fails.append(f"Company '{n['name']}' country '{n['country']}' has no Country node")

    # ---- edges ----
    operates, hq = Counter(), Counter()
    operates_target, hq_target = {}, {}
    competes = Counter()
    for i, e in enumerate(edges, 2):
        f, t, typ = e["from_id"], e["to_id"], e["type"]
        if typ not in EDGE_SHAPES:
            fails.append(f"edges.csv:{i}: unknown relationship type '{typ}'")
            continue
        ok = True
        for side, nid in (("from_id", f), ("to_id", t)):
            if nid not in by_id:
                fails.append(f"edges.csv:{i}: {side} '{nid}' does not exist in nodes.csv")
                ok = False
        if not ok:
            continue
        want_f, want_t = EDGE_SHAPES[typ]
        if by_id[f]["label"] != want_f or by_id[t]["label"] != want_t:
            fails.append(f"edges.csv:{i}: {typ} must be {want_f}->{want_t}, got "
                         f"{by_id[f]['label']}->{by_id[t]['label']} ({f} -> {t})")
        for col in ("as_of", "source", "confidence"):
            if not e.get(col, "").strip():
                fails.append(f"edges.csv:{i}: missing '{col}' on {f}-[{typ}]->{t}")
        if e.get("as_of") and not DATE.match(e["as_of"]):
            fails.append(f"edges.csv:{i}: as_of '{e['as_of']}' is not YYYY-MM-DD")
        if e.get("confidence") and e["confidence"] not in CONFIDENCE:
            fails.append(f"edges.csv:{i}: confidence '{e['confidence']}' not in high/medium/low")
        if typ == "OPERATES_IN":
            operates[f] += 1
            operates_target[f] = t
        elif typ == "HQ_IN":
            hq[f] += 1
            hq_target[f] = t
        elif typ == "COMPETES_WITH":
            a, b = by_id[f]["name"], by_id[t]["name"]
            if a.lower() > b.lower():
                fails.append(f"COMPETES_WITH '{a}'->'{b}' must be written lower name first ('{b}'->'{a}')")
            competes[tuple(sorted((f, t)))] += 1
        if typ == "SUPPLIES" and f == t:
            fails.append(f"edges.csv:{i}: '{by_id[f]['name']}' supplies itself")

    for n in nodes:
        if n["label"] != "Company":
            continue
        nid, name = n["id"], n["name"]
        if operates[nid] != 1:
            fails.append(f"Company '{name}' has {operates[nid]} OPERATES_IN edges, expected exactly 1")
        elif layer_name_by_id.get(operates_target[nid]) != n["layer"]:
            fails.append(f"Company '{name}' layer '{n['layer']}' does not match OPERATES_IN target "
                         f"'{layer_name_by_id.get(operates_target[nid])}'")
        if hq[nid] != 1:
            fails.append(f"Company '{name}' has {hq[nid]} HQ_IN edges, expected exactly 1")
        elif country_code_by_id.get(hq_target[nid]) != n["country"]:
            fails.append(f"Company '{name}' country '{n['country']}' does not match HQ_IN target "
                         f"'{country_code_by_id.get(hq_target[nid])}'")
    for (a, b), c in competes.items():
        if c > 1:
            fails.append(f"COMPETES_WITH pair ({a}, {b}) appears {c} times (reversed duplicate?)")
    dup_edges = Counter((e["from_id"], e["to_id"], e["type"]) for e in edges)
    for k, c in dup_edges.items():
        if c > 1:
            fails.append(f"edge {k} appears {c} times")

    if fails:
        print(f"FAILED: {len(fails)} issue(s) found\n")
        for x in fails:
            print(f" - {x}")
        return 1
    labels = Counter(n["label"] for n in nodes)
    types = Counter(e["type"] for e in edges)
    print(f"OK: {len(nodes)} nodes, {len(edges)} edges, no issues found")
    print("  nodes:", ", ".join(f"{k} {v}" for k, v in labels.items()))
    print("  edges:", ", ".join(f"{k} {v}" for k, v in sorted(types.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
