#!/usr/bin/env python3
"""Load data/nodes.csv and data/edges.csv into Neo4j via the official driver.

Secondary load path (primary is cypher/load.cypher pasted into Neo4j Browser,
which reads the same CSVs from raw GitHub URLs). This script reads the local
CSVs instead, for people who prefer running Python over pasting Cypher.

Usage:
    python scripts/load.py

Reads NEO4J_URI, NEO4J_USER (or NEO4J_USERNAME), NEO4J_PASSWORD from the
environment (a .env file next to this repo is picked up automatically if
python-dotenv is installed; otherwise export them yourself).
"""

import csv
import os
import sys
from pathlib import Path

from neo4j import GraphDatabase

REPO_ROOT = Path(__file__).resolve().parent.parent
NODES_CSV = REPO_ROOT / "data" / "nodes.csv"
EDGES_CSV = REPO_ROOT / "data" / "edges.csv"
CONSTRAINTS_CYPHER = REPO_ROOT / "cypher" / "constraints.cypher"

# label -> node property columns to set (besides id, which is always stored as elementId key)
LABEL_PROPS = {
    "Company": ["name", "ticker", "exchange", "listed", "tier"],
    "Layer": ["name", "order"],
    "Technology": ["name"],
    "Country": ["name", "code"],
    "Chokepoint": ["name", "layer"],
}


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def coerce(label, key, value):
    if value == "":
        return None
    if label == "Company" and key == "listed":
        return value.strip().lower() == "true"
    if label == "Company" and key == "tier":
        return int(value)
    if label == "Layer" and key == "order":
        return int(value)
    return value


def run_constraints(session):
    text = CONSTRAINTS_CYPHER.read_text()
    for stmt in [s.strip() for s in text.split(";") if s.strip()]:
        session.run(stmt)


def load_nodes(session, nodes):
    by_label = {}
    for n in nodes:
        by_label.setdefault(n["label"], []).append(n)

    for label, rows in by_label.items():
        props = LABEL_PROPS[label]
        batch = [{k: coerce(label, k, r[k]) for k in props} for r in rows]
        query = f"""
        UNWIND $batch AS row
        MERGE (n:{label} {{name: row.name}})
        SET n += row
        """
        session.run(query, batch=batch)
        print(f"  {label}: merged {len(batch)}")


def load_edges(session, edges, nodes):
    id_to_name_label = {n["id"]: (n["name"], n["label"]) for n in nodes}

    by_type = {}
    for e in edges:
        by_type.setdefault(e["type"], []).append(e)

    for etype, rows in by_type.items():
        batch = []
        for r in rows:
            from_name, from_label = id_to_name_label[r["from_id"]]
            to_name, to_label = id_to_name_label[r["to_id"]]
            batch.append(
                {
                    "from_name": from_name,
                    "from_label": from_label,
                    "to_name": to_name,
                    "to_label": to_label,
                    "as_of": r["as_of"],
                    "source": r["source"],
                    "confidence": r["confidence"],
                }
            )
        # label is fixed per batch in this dataset's edge types, so a single
        # CALL apoc-free query per (from_label, to_label) pair is enough
        by_label_pair = {}
        for b in batch:
            by_label_pair.setdefault((b["from_label"], b["to_label"]), []).append(b)

        for (from_label, to_label), sub_batch in by_label_pair.items():
            query = f"""
            UNWIND $batch AS row
            MATCH (a:{from_label} {{name: row.from_name}})
            MATCH (b:{to_label} {{name: row.to_name}})
            MERGE (a)-[r:{etype}]->(b)
            SET r.as_of = row.as_of, r.source = row.source, r.confidence = row.confidence
            """
            session.run(query, batch=sub_batch)
        print(f"  {etype}: merged {len(batch)}")


def main():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USER") or os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")

    if not all([uri, user, password]):
        print("Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD (see .env.example)", file=sys.stderr)
        return 1

    nodes = load_rows(NODES_CSV)
    edges = load_rows(EDGES_CSV)

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        print("Applying constraints...")
        run_constraints(session)
        print("Loading nodes...")
        load_nodes(session, nodes)
        print("Loading edges...")
        load_edges(session, edges, nodes)
    driver.close()
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
