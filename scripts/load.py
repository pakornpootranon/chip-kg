#!/usr/bin/env python3
"""Load data/nodes.csv and data/edges.csv into Neo4j from the local checkout.

Same result as pasting cypher/load.cypher into Neo4j Browser, which reads the
CSVs from GitHub. Use this one when the CSVs on your disk are newer than the
pushed ones, or when you prefer Python. Safe to re-run: everything is MERGE.

Usage:
    python scripts/load.py            # load
    python scripts/load.py --reset    # delete everything first, then load
    python scripts/load.py --counts   # only print node and edge counts

Reads NEO4J_URI, NEO4J_USERNAME (or NEO4J_USER), NEO4J_PASSWORD from the
environment or from a .env file in the repo root (Aura's credentials file
uses exactly these names, so you can copy it to .env as is).
"""

import csv
import os
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NODES_CSV = REPO_ROOT / "data" / "nodes.csv"
EDGES_CSV = REPO_ROOT / "data" / "edges.csv"
CONSTRAINTS_CYPHER = REPO_ROOT / "cypher" / "constraints.cypher"

LABEL_PROPS = {
    "Company": ["name", "ticker", "exchange", "country", "layer", "sub_segment", "tier", "chokepoint",
                "description", "key_products", "key_customers", "fab_or_ops_geography", "source"],
    "Layer": ["name", "order"],
    "Technology": ["name"],
    "Country": ["name", "code"],
    "Chokepoint": ["name", "layer"],
}
INT_PROPS = {"tier", "order"}
BOOL_PROPS = {"chokepoint"}
LIST_PROPS = {"key_products", "key_customers", "fab_or_ops_geography"}
EDGE_SHAPES = {
    "OPERATES_IN": ("Company", "Layer"), "HQ_IN": ("Company", "Country"),
    "CONTROLS": ("Company", "Chokepoint"), "DEPENDS_ON": ("Company", "Technology"),
    "SUPPLIES": ("Company", "Company"), "COMPETES_WITH": ("Company", "Company"),
}


def load_dotenv():
    p = REPO_ROOT / ".env"
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def coerce(key, value):
    if key in INT_PROPS:
        return int(value)
    if key in BOOL_PROPS:
        return value == "true"
    if key in LIST_PROPS:
        return value.split("|")
    return value


def counts(session):
    n = session.run("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS c ORDER BY label").data()
    e = session.run("MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS c ORDER BY type").data()
    return {r["label"]: r["c"] for r in n}, {r["type"]: r["c"] for r in e}


def main():
    load_dotenv()
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME") or os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")
    if not all([uri, user, password]):
        print("Set NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD (see .env.example)", file=sys.stderr)
        return 1
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        if "--counts" in sys.argv:
            n, e = counts(session)
            print("nodes:", n)
            print("edges:", e)
            return 0
        if "--reset" in sys.argv:
            print("Deleting everything...")
            session.run("MATCH (n) DETACH DELETE n")

        print("Applying constraints...")
        for stmt in CONSTRAINTS_CYPHER.read_text().split(";"):
            stmt = "\n".join(l for l in stmt.splitlines() if not l.strip().startswith("//")).strip()
            if stmt:
                session.run(stmt)

        nodes, edges = rows(NODES_CSV), rows(EDGES_CSV)
        print("Loading nodes...")
        by_label = {}
        for n in nodes:
            by_label.setdefault(n["label"], []).append(n)
        for label, props in LABEL_PROPS.items():
            batch = [{"id": r["id"], **{k: coerce(k, r[k]) for k in props}} for r in by_label.get(label, [])]
            session.run(f"UNWIND $batch AS row MERGE (n:{label} {{id: row.id}}) SET n += row", batch=batch)
            print(f"  {label}: {len(batch)}")

        print("Loading edges...")
        by_type = {}
        for e in edges:
            by_type.setdefault(e["type"], []).append(e)
        for typ, (fl, tl) in EDGE_SHAPES.items():
            batch = by_type.get(typ, [])
            session.run(
                f"UNWIND $batch AS row "
                f"MATCH (a:{fl} {{id: row.from_id}}), (b:{tl} {{id: row.to_id}}) "
                f"MERGE (a)-[r:{typ}]->(b) "
                f"SET r.as_of = row.as_of, r.source = row.source, r.confidence = row.confidence",
                batch=batch,
            )
            print(f"  {typ}: {len(batch)}")

        n, e = counts(session)
        want_n = Counter(x["label"] for x in nodes)
        want_e = Counter(x["type"] for x in edges)
        ok = dict(want_n) == {k: v for k, v in n.items() if k != "NewsItem"} and dict(want_e) == {
            k: v for k, v in e.items() if k not in ("MENTIONS", "AFFECTS")}
        print("nodes:", n)
        print("edges:", e)
        print("MATCHES CSV" if ok else "MISMATCH vs CSV: check the output above")
    driver.close()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
