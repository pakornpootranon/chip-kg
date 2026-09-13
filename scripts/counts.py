#!/usr/bin/env python3
"""Print Company count and edge count by type from the live graph, as JSON.

Usage:
    python scripts/counts.py                      # print
    python scripts/counts.py > briefs/baseline.json   # save the baseline
    python scripts/counts.py --diff briefs/baseline.json   # compare to a saved baseline

The daily news task may only add NewsItem nodes and their MENTIONS / AFFECTS
edges. Everything else must stay equal to the baseline. --diff exits 1 if a
protected count changed.

Reads NEO4J_URI, NEO4J_USERNAME (or NEO4J_USER), NEO4J_PASSWORD from the
environment or from .env in the repo root.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NEWS_ONLY = {"MENTIONS", "AFFECTS"}


def load_dotenv():
    p = REPO_ROOT / ".env"
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main():
    load_dotenv()
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME") or os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")
    if not all([uri, user, password]):
        print("Set NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD (see .env.example)", file=sys.stderr)
        return 1
    from neo4j import GraphDatabase

    with GraphDatabase.driver(uri, auth=(user, password)) as driver, driver.session() as s:
        nodes = {r["label"]: r["c"] for r in s.run(
            "MATCH (n) RETURN labels(n)[0] AS label, count(*) AS c ORDER BY label")}
        edges = {r["type"]: r["c"] for r in s.run(
            "MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS c ORDER BY type")}
    now = {"taken_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "company_count": nodes.get("Company", 0), "nodes": nodes, "edges": edges}

    if "--diff" in sys.argv:
        base = json.loads(Path(sys.argv[sys.argv.index("--diff") + 1]).read_text())
        bad = []
        if now["company_count"] != base["company_count"]:
            bad.append(f"Company count {base['company_count']} -> {now['company_count']}")
        for t in set(base["edges"]) | set(now["edges"]):
            if t in NEWS_ONLY:
                continue
            if base["edges"].get(t, 0) != now["edges"].get(t, 0):
                bad.append(f"{t} {base['edges'].get(t, 0)} -> {now['edges'].get(t, 0)}")
        news = now["nodes"].get("NewsItem", 0) - base["nodes"].get("NewsItem", 0)
        print(f"NewsItem nodes since baseline: +{news}")
        if bad:
            print("PROTECTED COUNTS CHANGED:")
            for b in bad:
                print("  ", b)
            return 1
        print("OK: Company count and all non-news edge types unchanged from baseline")
        return 0

    print(json.dumps(now, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
