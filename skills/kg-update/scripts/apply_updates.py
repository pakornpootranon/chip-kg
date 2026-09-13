#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["neo4j>=5"]
# ///
"""Apply one approved pending Cypher file to Neo4j, then archive it.

Only runs files shaped exactly like propose_updates.py writes them: MATCH two
existing nodes, MERGE one new relationship with inline as_of, source and
confidence. Before touching the database it re-checks every statement and
refuses the whole file if it contains DELETE or SET or any statement of a
different shape. So even a hand-edited file cannot change existing data.

Usage:
    uv run apply_updates.py 2026-09-20.cypher            # dry run, prints what would run
    uv run apply_updates.py 2026-09-20.cypher --confirm  # applies, then moves the file to applied/

The file is looked up in the pending dir: ./pending/ inside the chip-kg
repo, otherwise ~/.chip-kg/pending/ (override with CHIP_KG_HOME). A full
path works too as long as it points into that dir.

When run inside the chip-kg repo it also appends the applied edges to
data/edges.csv, because there the CSVs are the source of truth. Followers
running the installed skill have no repo, so that step is skipped.

Needs NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD in the environment or in a
.env file next to the pending dir (Hermes loads ~/.hermes/.env for you).
"""

import csv
import os
import re
import sys
from pathlib import Path

FORBIDDEN = re.compile(r"\bDELETE\b|\bSET\b", re.IGNORECASE)
STATEMENT = re.compile(
    r'^MATCH \(a:(?P<from_label>\w+) \{name: "(?P<from_name>[^"]*)"\}\), '
    r'\(b:(?P<to_label>\w+) \{name: "(?P<to_name>[^"]*)"\}\)\n'
    r'MERGE \(a\)-\[:(?P<type>\w+) \{as_of: "(?P<as_of>[^"]*)", source: "(?P<source>[^"]*)", '
    r'confidence: "(?P<confidence>[^"]*)"\}\]->\(b\);$')


# ---------------------------------------------------------------- shared setup
def repo_root():
    parents = Path(__file__).resolve().parents
    candidate = parents[3] if len(parents) > 3 else None
    if candidate and (candidate / "data" / "edges.csv").exists() and (candidate / "CLAUDE.md").exists():
        return candidate
    return None


def home_dir():
    return repo_root() or Path(os.environ.get("CHIP_KG_HOME", Path.home() / ".chip-kg")).expanduser()


def load_dotenv(path):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def connect():
    load_dotenv(home_dir() / ".env")
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME") or os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")
    if not all([uri, user, password]):
        sys.exit("Set NEO4J_URI, NEO4J_USERNAME and NEO4J_PASSWORD (from your Aura credentials file).")
    try:
        from neo4j import GraphDatabase
    except ImportError:
        sys.exit("The neo4j package is missing. Run this script with `uv run`, or `pip install neo4j`.")
    return GraphDatabase.driver(uri, auth=(user, password))


def explain_connection_error(exc):
    text = str(exc)
    if "CERTIFICATE_VERIFY_FAILED" in text or "SSLCertVerificationError" in text:
        return ("Could not verify Aura's TLS certificate. This usually means something on your network "
                "inspects TLS. As a workaround, change neo4j+s:// to neo4j+ssc:// in NEO4J_URI "
                "(still encrypted, skips chain verification).")
    return f"Could not connect to Neo4j: {text}"


# ---------------------------------------------------------------- file checks
def statements_of(text):
    body = "\n".join(l for l in text.splitlines() if not l.strip().startswith("//"))
    return [b.strip() for b in body.split("\n\n") if b.strip()]


def sync_repo_csv(root, parsed):
    """Author mode only: mirror applied edges into data/edges.csv by node id."""
    with open(root / "data" / "nodes.csv", newline="", encoding="utf-8") as f:
        name_to_id = {r["name"]: r["id"] for r in csv.DictReader(f)}
    with open(root / "data" / "edges.csv", newline="", encoding="utf-8") as f:
        existing = {tuple(r.values()) for r in csv.DictReader(f)}
    rows = []
    for e in parsed:
        if e["from_name"] not in name_to_id or e["to_name"] not in name_to_id:
            print(f"  note: {e['from_name']} or {e['to_name']} is not in data/nodes.csv, "
                  f"not mirrored to edges.csv", file=sys.stderr)
            continue
        row = (name_to_id[e["from_name"]], name_to_id[e["to_name"]], e["type"],
               e["as_of"], e["source"], e["confidence"])
        if row not in existing:
            rows.append(row)
    if rows:
        with open(root / "data" / "edges.csv", "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rows)
    return len(rows)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", help="pending file name or path")
    parser.add_argument("--confirm", action="store_true", help="actually apply (default: dry run)")
    args = parser.parse_args()

    pending = (home_dir() / "pending").resolve()
    path = Path(args.file)
    if not path.exists():
        path = pending / args.file
    if not path.exists():
        sys.exit(f"{args.file} not found (looked in {pending})")
    path = path.resolve()
    if path.parent != pending:
        sys.exit(f"{path} is not in {pending}; refusing to run a file from elsewhere")

    text = path.read_text()
    if FORBIDDEN.search(re.sub(r"//.*", "", text)):
        sys.exit("File contains DELETE or SET outside a comment; refusing to run it. "
                 "Regenerate it with propose_updates.py instead of editing by hand.")

    parsed, bad = [], []
    for s in statements_of(text):
        m = STATEMENT.match(s)
        (parsed.append(m.groupdict()) if m else bad.append(s))
    if not parsed and not bad:
        sys.exit("No statements found in file")
    if bad:
        print(f"{len(bad)} statement(s) do not match the expected MATCH+MERGE shape; refusing to run:",
              file=sys.stderr)
        for b in bad:
            print(f"  {b[:120]}", file=sys.stderr)
        return 1

    if not args.confirm:
        print(f"DRY RUN: {len(parsed)} statement(s) would run against Neo4j:\n")
        for s in statements_of(text):
            print(s, "\n")
        print("Re-run with --confirm to apply.")
        return 0

    driver = connect()
    created = 0
    try:
        with driver.session() as session:
            for s in statements_of(text):
                created += session.run(s).consume().counters.relationships_created
    except Exception as exc:
        sys.exit(explain_connection_error(exc))
    finally:
        driver.close()

    mirrored = sync_repo_csv(repo_root(), parsed) if repo_root() else None

    applied = pending / "applied"
    applied.mkdir(exist_ok=True)
    dest, n = applied / path.name, 2
    while dest.exists():
        dest, n = applied / f"{path.stem}-{n}{path.suffix}", n + 1
    path.rename(dest)

    print(f"Applied {len(parsed)} statement(s); {created} new relationship(s) created.")
    if mirrored is not None:
        print(f"Mirrored {mirrored} row(s) into data/edges.csv (commit it).")
    print(f"Archived to {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
