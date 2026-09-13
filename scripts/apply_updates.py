#!/usr/bin/env python3
"""Apply one approved pending/*.cypher file to Aura, sync data/edges.csv, archive it.

Deliberately narrow: this script only ever executes files shaped exactly
like propose_updates.py produces (MATCH existing nodes, then MERGE a new
relationship with inline as_of/source/confidence). Before touching the
database it scans the file for DELETE or SET and refuses to run if either
appears — a defense-in-depth check in case a file was hand-edited after
being proposed, on top of propose_updates.py never generating them.

pending/ is gitignored (see .gitignore), so the .cypher file itself leaves
no permanent trace in the repo. Per CLAUDE.md ("data/nodes.csv and
data/edges.csv are the source of truth... never hand-edit Aura and forget to
update the CSVs"), every edge this script applies to Aura is also appended
as a row to data/edges.csv, by id (looked up from data/nodes.csv). This
script does NOT commit that change — the caller (you, or the agent running
this skill) still needs to `git add data/edges.csv && git commit`.

Usage:
    python scripts/apply_updates.py pending/2026-09-20.cypher            # dry run
    python scripts/apply_updates.py pending/2026-09-20.cypher --confirm  # actually applies

Without --confirm, prints the statements it would run and exits — no
connection is made, nothing is moved, data/edges.csv is untouched. Reads
NEO4J_URI, NEO4J_USER (or NEO4J_USERNAME), NEO4J_PASSWORD from the
environment, same as scripts/load.py.
"""

import csv
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PENDING_DIR = REPO_ROOT / "pending"
APPLIED_DIR = PENDING_DIR / "applied"
NODES_CSV = REPO_ROOT / "data" / "nodes.csv"
EDGES_CSV = REPO_ROOT / "data" / "edges.csv"

FORBIDDEN_PATTERN = re.compile(r"\bDELETE\b|\bSET\b", re.IGNORECASE)
STATEMENT_PATTERN = re.compile(
    r'^MATCH\s+\(a:\w+\s+\{name:\s*"(?P<from_name>[^"]*)"\}\),\s*'
    r'\(b:\w+\s+\{name:\s*"(?P<to_name>[^"]*)"\}\)\s*\n'
    r'MERGE\s+\(a\)-\[:(?P<type>\w+)\s+'
    r'\{as_of:\s*"(?P<as_of>[^"]*)",\s*source:\s*"(?P<source>[^"]*)",\s*confidence:\s*"(?P<confidence>[^"]*)"\}\]->\(b\);$',
    re.MULTILINE,
)


def extract_statements(text):
    """Pull out only the MATCH...MERGE...; statements, ignoring // comments and blank lines."""
    stripped = "\n".join(line for line in text.splitlines() if not line.strip().startswith("//"))
    blocks = [b.strip() for b in stripped.split("\n\n") if b.strip()]
    return blocks


def load_name_to_id():
    with open(NODES_CSV, newline="", encoding="utf-8") as f:
        return {row["name"]: row["id"] for row in csv.DictReader(f)}


def append_to_edges_csv(parsed_edges, name_to_id):
    """Append one row per applied edge to data/edges.csv, skipping exact duplicates."""
    with open(EDGES_CSV, newline="", encoding="utf-8") as f:
        existing = {tuple(row.values()) for row in csv.DictReader(f)}

    new_rows = []
    for e in parsed_edges:
        row = (
            name_to_id[e["from_name"]],
            name_to_id[e["to_name"]],
            e["type"],
            e["as_of"],
            e["source"],
            e["confidence"],
        )
        if row not in existing:
            new_rows.append(row)

    if new_rows:
        with open(EDGES_CSV, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(new_rows)

    return len(new_rows)


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", help="Path to a pending/*.cypher file")
    parser.add_argument("--confirm", action="store_true", help="Actually apply to Aura (default: dry run)")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"{path} does not exist", file=sys.stderr)
        return 1
    if path.resolve().parent != PENDING_DIR.resolve():
        print(f"{path} is not in pending/ — refusing to run a file from elsewhere", file=sys.stderr)
        return 1

    text = path.read_text()

    if FORBIDDEN_PATTERN.search(re.sub(r"//.*", "", text)):
        print("File contains DELETE or SET outside a comment — refusing to run it. "
              "This should never happen to a file propose_updates.py generated; "
              "if it was hand-edited, regenerate it instead.", file=sys.stderr)
        return 1

    statements = extract_statements(text)
    if not statements:
        print("No statements found in file", file=sys.stderr)
        return 1

    parsed = []
    bad = []
    for s in statements:
        m = STATEMENT_PATTERN.match(s)
        if m:
            parsed.append(m.groupdict())
        else:
            bad.append(s)
    if bad:
        print(f"{len(bad)} statement(s) don't match the expected MATCH+MERGE shape — refusing to run:", file=sys.stderr)
        for b in bad:
            print(f"  {b[:100]}...", file=sys.stderr)
        return 1

    name_to_id = load_name_to_id()
    unknown = sorted({e[k] for e in parsed for k in ("from_name", "to_name") if e[k] not in name_to_id})
    if unknown:
        print(f"These node names aren't in data/nodes.csv, can't sync to edges.csv: {unknown}", file=sys.stderr)
        print("(propose_updates.py should have caught this — was this file hand-edited?)", file=sys.stderr)
        return 1

    if not args.confirm:
        print(f"DRY RUN — {len(statements)} statement(s) would run against Aura:\n")
        for s in statements:
            print(s, "\n")
        print("Re-run with --confirm to actually apply.")
        return 0

    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USER") or os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    if not all([uri, user, password]):
        print("Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD (see .env.example)", file=sys.stderr)
        return 1

    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(uri, auth=(user, password))
    created = 0
    try:
        with driver.session() as session:
            for stmt in statements:
                result = session.run(stmt)
                summary = result.consume()
                created += summary.counters.relationships_created
    finally:
        driver.close()

    csv_rows_added = append_to_edges_csv(parsed, name_to_id)

    APPLIED_DIR.mkdir(exist_ok=True)
    dest = APPLIED_DIR / path.name
    n = 2
    while dest.exists():
        # Same-named file already archived today (e.g. an earlier on-demand
        # run applied before this scheduled one) — never silently overwrite
        # another applied file's audit trail.
        dest = APPLIED_DIR / f"{path.stem}-{n}{path.suffix}"
        n += 1
    path.rename(dest)

    print(f"Applied {len(statements)} statement(s), {created} new relationship(s) created in Aura.")
    print(f"Appended {csv_rows_added} row(s) to data/edges.csv — remember to commit it.")
    print(f"Moved {path} -> {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
