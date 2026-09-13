#!/usr/bin/env python3
"""Validate data/nodes.csv and data/edges.csv against the CLAUDE.md ontology.

Exit 0 if clean, exit 1 with a readable list of failures otherwise.
"""

import csv
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NODES_CSV = REPO_ROOT / "data" / "nodes.csv"
EDGES_CSV = REPO_ROOT / "data" / "edges.csv"

ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_LABELS = {"Company", "Layer", "Technology", "Country", "Chokepoint"}


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    failures = []

    nodes = load_rows(NODES_CSV)
    edges = load_rows(EDGES_CSV)

    node_by_id = {}
    for i, n in enumerate(nodes, start=2):  # header is row 1
        node_id = n["id"]
        if node_id in node_by_id:
            failures.append(f"nodes.csv:{i}: duplicate node id '{node_id}'")
        node_by_id[node_id] = n
        if n["label"] not in ALLOWED_LABELS:
            failures.append(f"nodes.csv:{i}: unknown label '{n['label']}'")

    # name unique per label
    names_by_label = {}
    for n in nodes:
        names_by_label.setdefault(n["label"], Counter())[n["name"]] += 1
    for label, counter in names_by_label.items():
        for name, count in counter.items():
            if count > 1:
                failures.append(f"duplicate name '{name}' for label {label} ({count} nodes)")

    # tickers unique (blank tickers, i.e. unlisted/private companies, are exempt)
    tickers = Counter(n["ticker"] for n in nodes if n["label"] == "Company" and n["ticker"])
    for ticker, count in tickers.items():
        if count > 1:
            failures.append(f"duplicate ticker '{ticker}' ({count} companies)")

    companies = [n for n in nodes if n["label"] == "Company"]
    company_ids = {n["id"] for n in companies}

    operates_in = Counter()
    hq_in = Counter()
    competes_pairs = []

    for i, e in enumerate(edges, start=2):
        from_id, to_id, etype = e["from_id"], e["to_id"], e["type"]

        if from_id not in node_by_id:
            failures.append(f"edges.csv:{i}: from_id '{from_id}' does not exist in nodes.csv")
        if to_id not in node_by_id:
            failures.append(f"edges.csv:{i}: to_id '{to_id}' does not exist in nodes.csv")

        for field in ("as_of", "source", "confidence"):
            if not e.get(field):
                failures.append(f"edges.csv:{i}: missing '{field}' on {from_id}-[{etype}]->{to_id}")

        confidence = e.get("confidence")
        if confidence and confidence not in ALLOWED_CONFIDENCE:
            failures.append(
                f"edges.csv:{i}: confidence '{confidence}' not in {sorted(ALLOWED_CONFIDENCE)}"
            )

        if etype == "OPERATES_IN":
            operates_in[from_id] += 1
        elif etype == "HQ_IN":
            hq_in[from_id] += 1
        elif etype == "COMPETES_WITH":
            competes_pairs.append((from_id, to_id))

    for cid in company_ids:
        name = node_by_id[cid]["name"]
        if operates_in[cid] != 1:
            failures.append(
                f"Company '{name}' ({cid}) has {operates_in[cid]} OPERATES_IN edges, expected exactly 1"
            )
        if hq_in[cid] != 1:
            failures.append(
                f"Company '{name}' ({cid}) has {hq_in[cid]} HQ_IN edges, expected exactly 1"
            )

    # COMPETES_WITH pairs must not appear in both directions, and must not be duplicated
    seen_pairs = Counter()
    for from_id, to_id in competes_pairs:
        key = tuple(sorted((from_id, to_id)))
        seen_pairs[key] += 1
        from_name = node_by_id.get(from_id, {}).get("name", from_id)
        to_name = node_by_id.get(to_id, {}).get("name", to_id)
        if from_name.lower() > to_name.lower():
            failures.append(
                f"COMPETES_WITH '{from_name}'->'{to_name}': should be written lower name first "
                f"('{to_name}'->'{from_name}') per CLAUDE.md convention"
            )
    for (a, b), count in seen_pairs.items():
        if count > 1:
            failures.append(f"COMPETES_WITH pair ({a}, {b}) is duplicated {count} times")

    if failures:
        print(f"FAILED: {len(failures)} issue(s) found\n")
        for f in failures:
            print(f" - {f}")
        return 1

    print(f"OK: {len(nodes)} nodes, {len(edges)} edges, no issues found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
