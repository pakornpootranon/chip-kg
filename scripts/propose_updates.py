#!/usr/bin/env python3
"""Turn a structured list of proposed edges into an add-only Cypher diff.

This script does not read news itself and does not decide what the edges
should be — that interpretation is the calling agent's job (see
skills/kg-update/SKILL.md). This script's only job is to take edges the
agent has already decided on, validate them against the ontology and the
existing node list, and deterministically render them as a pending Cypher
file that only ever MERGEs a brand new relationship. It never emits DELETE
and never emits a bare SET on an existing relationship — every MERGE carries
its as_of/source/confidence inline, so re-running with a different as_of
always adds a new edge rather than overwriting one.

Usage:
    python scripts/propose_updates.py --source URL --edges-json edges.json [--as-of YYYY-MM-DD]

edges.json is a JSON list of objects, each with:
    from        name of the existing FROM node
    to          name of the existing TO node
    type        one of OPERATES_IN, SUPPLIES, COMPETES_WITH, DEPENDS_ON, HQ_IN, CONTROLS
    confidence  high | medium | low
    note        optional one-line human-readable rationale, shown in the diff

Output: pending/<as_of>.cypher (or pending/<as_of>-2.cypher etc. if that date
already has a file), with a plain-English header comment followed by one
MATCH+MERGE statement per edge. Exits 1 and writes nothing if any edge fails
validation.
"""

import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NODES_CSV = REPO_ROOT / "data" / "nodes.csv"
PENDING_DIR = REPO_ROOT / "pending"

ALLOWED_CONFIDENCE = {"high", "medium", "low"}

# type -> (from_label, to_label)
EDGE_LABELS = {
    "OPERATES_IN": ("Company", "Layer"),
    "SUPPLIES": ("Company", "Company"),
    "COMPETES_WITH": ("Company", "Company"),
    "DEPENDS_ON": ("Company", "Technology"),
    "HQ_IN": ("Company", "Country"),
    "CONTROLS": ("Company", "Chokepoint"),
}

FORBIDDEN_PATTERN = re.compile(r"\bDELETE\b|\bSET\b", re.IGNORECASE)


def load_nodes_by_name():
    """name -> label, for every node currently in data/nodes.csv."""
    by_name = {}
    with open(NODES_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            by_name[row["name"]] = row["label"]
    return by_name


def validate_and_normalize(edges, nodes_by_name):
    errors = []
    normalized = []

    for i, e in enumerate(edges):
        prefix = f"edge {i} ({e.get('from')!r} -{e.get('type')}-> {e.get('to')!r})"

        etype = e.get("type")
        if etype not in EDGE_LABELS:
            errors.append(f"{prefix}: unknown type {etype!r}, must be one of {sorted(EDGE_LABELS)}")
            continue

        confidence = e.get("confidence")
        if confidence not in ALLOWED_CONFIDENCE:
            errors.append(f"{prefix}: confidence must be one of {sorted(ALLOWED_CONFIDENCE)}, got {confidence!r}")
            continue

        from_name, to_name = e.get("from"), e.get("to")
        if not from_name or not to_name:
            errors.append(f"{prefix}: 'from' and 'to' are required")
            continue
        if from_name == to_name:
            errors.append(f"{prefix}: 'from' and 'to' are the same node")
            continue

        from_label_expected, to_label_expected = EDGE_LABELS[etype]

        if from_name not in nodes_by_name:
            errors.append(f"{prefix}: {from_name!r} is not an existing node — propose_updates.py only adds edges, never nodes")
            continue
        if to_name not in nodes_by_name:
            errors.append(f"{prefix}: {to_name!r} is not an existing node — propose_updates.py only adds edges, never nodes")
            continue

        if nodes_by_name[from_name] != from_label_expected:
            errors.append(f"{prefix}: {from_name!r} is a {nodes_by_name[from_name]}, expected {from_label_expected} for {etype}")
            continue
        if nodes_by_name[to_name] != to_label_expected:
            errors.append(f"{prefix}: {to_name!r} is a {nodes_by_name[to_name]}, expected {to_label_expected} for {etype}")
            continue

        # CLAUDE.md convention: COMPETES_WITH is written lower name first,
        # once per pair. Normalize rather than reject, since this is a
        # mechanical rule an agent shouldn't need to remember.
        if etype == "COMPETES_WITH" and from_name > to_name:
            from_name, to_name = to_name, from_name

        normalized.append(
            {
                "from": from_name,
                "to": to_name,
                "from_label": from_label_expected,
                "to_label": to_label_expected,
                "type": etype,
                "confidence": confidence,
                "note": e.get("note", ""),
            }
        )

    return normalized, errors


def render_cypher(edges, as_of, source):
    lines = [
        f"// Proposed update — {as_of}",
        f"// Source: {source}",
        "// Add-only: every statement below is MATCH existing nodes + MERGE a NEW",
        "// relationship carrying this as_of. Nothing here can DELETE or modify an",
        "// existing edge's properties — that's enforced by propose_updates.py, not",
        "// just a convention.",
        "//",
        "// Diff (plain English):",
    ]
    for e in edges:
        note = f" — {e['note']}" if e["note"] else ""
        lines.append(f"//   {e['type']}: {e['from']} -> {e['to']} (confidence: {e['confidence']}){note}")
    lines.append("")

    for e in edges:
        stmt = (
            f'MATCH (a:{e["from_label"]} {{name: "{e["from"]}"}}), '
            f'(b:{e["to_label"]} {{name: "{e["to"]}"}})\n'
            f"MERGE (a)-[:{e['type']} "
            f'{{as_of: "{as_of}", source: "{source}", confidence: "{e["confidence"]}"}}]->(b);'
        )
        lines.append(stmt)
        lines.append("")

    text = "\n".join(lines)
    executable_only = re.sub(r"//.*", "", text)
    if FORBIDDEN_PATTERN.search(executable_only):
        raise AssertionError("internal error: generated Cypher contains DELETE or SET — refusing to write it")
    return text


def next_available_path(as_of):
    PENDING_DIR.mkdir(exist_ok=True)
    candidate = PENDING_DIR / f"{as_of}.cypher"
    n = 2
    while candidate.exists():
        candidate = PENDING_DIR / f"{as_of}-{n}.cypher"
        n += 1
    return candidate


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True, help="News URL this proposal is based on")
    parser.add_argument("--edges-json", required=True, help="Path to a JSON file listing proposed edges")
    parser.add_argument("--as-of", default=None, help="ISO date for the new edges (default: today)")
    args = parser.parse_args()

    as_of = args.as_of or date.today().isoformat()

    try:
        edges_raw = json.loads(Path(args.edges_json).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read {args.edges_json}: {exc}", file=sys.stderr)
        return 1

    if not isinstance(edges_raw, list) or not edges_raw:
        print("edges-json must be a non-empty JSON list", file=sys.stderr)
        return 1

    nodes_by_name = load_nodes_by_name()
    edges, errors = validate_and_normalize(edges_raw, nodes_by_name)

    if errors:
        print(f"{len(errors)} edge(s) failed validation — writing nothing:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    cypher_text = render_cypher(edges, as_of, args.source)
    out_path = next_available_path(as_of)
    out_path.write_text(cypher_text)

    print(f"Wrote {out_path} ({len(edges)} edge(s))")
    print()
    print(cypher_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
