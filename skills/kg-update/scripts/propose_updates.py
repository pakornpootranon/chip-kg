#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["neo4j>=5"]
# ///
"""Turn a list of proposed edges into an add-only Cypher file waiting for approval.

This script does not read news and does not decide what the edges should be.
The agent running the kg-update skill decides; this script only checks the
proposal against the ontology and the live graph, then renders it as Cypher
that can only ever MERGE a brand new relationship. It never emits DELETE and
never emits SET, so nothing it produces can change or remove an existing edge.

Usage:
    uv run propose_updates.py --source URL --edges-json edges.json [--as-of YYYY-MM-DD]

edges.json is a JSON list of objects:
    {"from": "Arm Holdings", "to": "Samsung Electronics", "type": "SUPPLIES",
     "confidence": "low", "note": "one line of plain English, shown in the diff"}

type must be one of OPERATES_IN, SUPPLIES, COMPETES_WITH, DEPENDS_ON, HQ_IN, CONTROLS.
confidence must be high, medium or low. Both endpoints must already exist in
the graph; this script adds edges, never nodes.

Output goes to <pending dir>/<as_of>.cypher. Inside the chip-kg repo that is
./pending/; anywhere else it is ~/.chip-kg/pending/ (override with CHIP_KG_HOME).
Exits 1 and writes nothing if any edge fails validation.

Needs NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD in the environment. Hermes
provides them; for a manual run use `uv run --env-file <your file> ...`.
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

ALLOWED_CONFIDENCE = {"high", "medium", "low"}
EDGE_LABELS = {
    "OPERATES_IN": ("Company", "Layer"),
    "SUPPLIES": ("Company", "Company"),
    "COMPETES_WITH": ("Company", "Company"),
    "DEPENDS_ON": ("Company", "Technology"),
    "HQ_IN": ("Company", "Country"),
    "CONTROLS": ("Company", "Chokepoint"),
}
FORBIDDEN = re.compile(r"\bDELETE\b|\bSET\b", re.IGNORECASE)


# ---------------------------------------------------------------- shared setup
def repo_root():
    """The chip-kg checkout when this script runs from inside it, else None."""
    candidate = Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents) > 3 else None
    if candidate and (candidate / "data" / "edges.csv").exists() and (candidate / "CLAUDE.md").exists():
        return candidate
    return None


def home_dir():
    root = repo_root()
    if root:
        return root
    return Path(os.environ.get("CHIP_KG_HOME", Path.home() / ".chip-kg")).expanduser()


def connect():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME") or os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")
    if not all([uri, user, password]):
        sys.exit("Set NEO4J_URI, NEO4J_USERNAME and NEO4J_PASSWORD (from your Aura credentials file).")
    try:
        from neo4j import GraphDatabase
    except ImportError:
        sys.exit("The neo4j package is missing. Run this script with uv run, which installs it.")
    return GraphDatabase.driver(uri, auth=(user, password))


def explain_connection_error(exc):
    text = str(exc)
    if "CERTIFICATE_VERIFY_FAILED" in text or "SSLCertVerificationError" in text:
        return ("Could not verify Aura's TLS certificate. This usually means something on your network "
                "inspects TLS. As a workaround, change neo4j+s:// to neo4j+ssc:// in NEO4J_URI "
                "(still encrypted, skips chain verification).")
    return f"Could not connect to Neo4j: {text}"


# ---------------------------------------------------------------- validation
def live_nodes(driver):
    """name -> label for every node currently in the graph."""
    with driver.session() as session:
        rows = session.run("MATCH (n) WHERE n.name IS NOT NULL RETURN labels(n)[0] AS label, n.name AS name")
        return {r["name"]: r["label"] for r in rows}


def validate(edges, nodes_by_name):
    errors, normalized = [], []
    for i, e in enumerate(edges):
        prefix = f"edge {i} ({e.get('from')!r} -{e.get('type')}-> {e.get('to')!r})"
        etype, confidence = e.get("type"), e.get("confidence")
        from_name, to_name = e.get("from"), e.get("to")

        if etype not in EDGE_LABELS:
            errors.append(f"{prefix}: unknown type {etype!r}, must be one of {sorted(EDGE_LABELS)}")
            continue
        if confidence not in ALLOWED_CONFIDENCE:
            errors.append(f"{prefix}: confidence must be high, medium or low, got {confidence!r}")
            continue
        if not from_name or not to_name:
            errors.append(f"{prefix}: 'from' and 'to' are required")
            continue
        if from_name == to_name:
            errors.append(f"{prefix}: 'from' and 'to' are the same node")
            continue
        from_label, to_label = EDGE_LABELS[etype]
        for name, want in ((from_name, from_label), (to_name, to_label)):
            if name not in nodes_by_name:
                errors.append(f"{prefix}: {name!r} is not in the graph. This skill adds edges, never nodes.")
                break
            if nodes_by_name[name] != want:
                errors.append(f"{prefix}: {name!r} is a {nodes_by_name[name]}, expected {want} for {etype}")
                break
        else:
            if etype == "COMPETES_WITH" and from_name > to_name:
                from_name, to_name = to_name, from_name
            normalized.append({"from": from_name, "to": to_name, "from_label": from_label,
                               "to_label": to_label, "type": etype, "confidence": confidence,
                               "note": str(e.get("note", "")).strip()})
    return normalized, errors


# ---------------------------------------------------------------- rendering
def render(edges, as_of, source):
    lines = [f"// Proposed update {as_of}", f"// Source: {source}",
             "// Add-only: each statement matches existing nodes and merges a NEW relationship",
             "// with this as_of. Existing edges are never changed or removed.", "//",
             "// Diff:"]
    for e in edges:
        note = f" | {e['note']}" if e["note"] else ""
        lines.append(f"//   {e['type']}: {e['from']} -> {e['to']} (confidence: {e['confidence']}){note}")
    lines.append("")
    for e in edges:
        lines.append(f'MATCH (a:{e["from_label"]} {{name: "{e["from"]}"}}), (b:{e["to_label"]} {{name: "{e["to"]}"}})\n'
                     f'MERGE (a)-[:{e["type"]} {{as_of: "{as_of}", source: "{source}", '
                     f'confidence: "{e["confidence"]}"}}]->(b);')
        lines.append("")
    text = "\n".join(lines)
    if FORBIDDEN.search(re.sub(r"//.*", "", text)):
        raise AssertionError("generated Cypher contains DELETE or SET; refusing to write it")
    return text


def next_path(pending, as_of):
    pending.mkdir(parents=True, exist_ok=True)
    out, n = pending / f"{as_of}.cypher", 2
    while out.exists():
        out, n = pending / f"{as_of}-{n}.cypher", n + 1
    return out


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True, help="news URL this proposal is based on")
    parser.add_argument("--edges-json", required=True, help="JSON file listing proposed edges")
    parser.add_argument("--as-of", default=None, help="ISO date for the new edges (default: today)")
    args = parser.parse_args()

    as_of = args.as_of or date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", as_of):
        sys.exit(f"--as-of must be YYYY-MM-DD, got {as_of!r}")
    if '"' in args.source:
        sys.exit("--source must not contain double quotes")

    try:
        raw = json.loads(Path(args.edges_json).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"Could not read {args.edges_json}: {exc}")
    if not isinstance(raw, list) or not raw:
        sys.exit("edges.json must be a non-empty JSON list")

    driver = connect()
    try:
        try:
            nodes = live_nodes(driver)
        except Exception as exc:  # connection or auth problems surface here
            sys.exit(explain_connection_error(exc))
    finally:
        driver.close()

    edges, errors = validate(raw, nodes)
    if errors:
        print(f"{len(errors)} edge(s) failed validation, writing nothing:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    text = render(edges, as_of, args.source)
    out = next_path(home_dir() / "pending", as_of)
    out.write_text(text)
    print(f"Wrote {out} ({len(edges)} edge(s))\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
