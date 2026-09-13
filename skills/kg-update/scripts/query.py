#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["neo4j>=5"]
# ///
"""Run a read-only Cypher query or one of the chip-kg screens and print the result.

Usage:
    uv run query.py --cypher "MATCH (c:Company {listed: true}) RETURN c.name ORDER BY c.name"
    uv run query.py --screen 05                       # stale edges, default months from the file
    uv run query.py --screen 05 --param months=3
    uv run query.py --screen 02 --param company_name=NVIDIA --format json

Screens:
    01  single source chokepoints
    02  upstream of a company        (param: company_name)
    03  country concentration
    04  tier 2 feeding tier 1
    05  stale edges                  (param: months)

Inside the chip-kg repo the screen files are read from cypher/screens/. Anywhere
else they are fetched from the public repo on GitHub (override the base with
CHIP_KG_RAW_BASE). Lines starting with :param in a screen file are Neo4j Browser
syntax; this script turns them into defaults that --param can override.

This tool is read-only. It refuses queries containing CREATE, MERGE, SET,
DELETE, REMOVE or DROP. Use propose_updates.py and apply_updates.py to change
the graph.

Needs NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD in the environment or in a
.env file (Hermes loads ~/.hermes/.env for you).
"""

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

SCREENS = {
    "01": "01_single_source_chokepoints",
    "02": "02_upstream_of",
    "03": "03_country_concentration",
    "04": "04_tier2_feeding_tier1",
    "05": "05_stale_edges",
}
DEFAULT_RAW_BASE = "https://raw.githubusercontent.com/pakornpootranon/chip-kg/main"
WRITE_WORDS = re.compile(r"\b(CREATE|MERGE|SET|DELETE|DETACH|REMOVE|DROP|CALL\s*\{)\b", re.IGNORECASE)
PARAM_LINE = re.compile(r"^\s*:param\s+(\w+)\s*=>\s*(.+?);?\s*$")


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


# ---------------------------------------------------------------- screens
def screen_text(name):
    key = name.strip().lower()
    full = SCREENS.get(key) or next((v for v in SCREENS.values() if v == key or v.endswith(key)), None)
    if not full:
        sys.exit(f"Unknown screen {name!r}. Known: " + ", ".join(f"{k} ({v})" for k, v in SCREENS.items()))
    root = repo_root()
    if root:
        return (root / "cypher" / "screens" / f"{full}.cypher").read_text()
    url = f"{os.environ.get('CHIP_KG_RAW_BASE', DEFAULT_RAW_BASE).rstrip('/')}/cypher/screens/{full}.cypher"
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            return resp.read().decode("utf-8")
    except Exception as exc:
        sys.exit(f"Could not fetch screen {full} from {url}: {exc}")


def parse_value(raw):
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"-?\d+\.\d+", raw):
        return float(raw)
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    return raw


def split_params(text):
    """Return (cypher without :param lines, defaults dict)."""
    defaults, kept = {}, []
    for line in text.splitlines():
        m = PARAM_LINE.match(line)
        if m:
            defaults[m.group(1)] = parse_value(m.group(2))
        else:
            kept.append(line)
    return "\n".join(kept).strip().rstrip(";"), defaults


# ---------------------------------------------------------------- output
def print_table(keys, rows, limit):
    if not rows:
        print("(no rows)")
        return
    shown = rows[:limit]
    cells = [[str(r.get(k, "")) for k in keys] for r in shown]
    widths = [max(len(k), *(len(c[i]) for c in cells)) for i, k in enumerate(keys)]
    print("  ".join(k.ljust(w) for k, w in zip(keys, widths)))
    print("  ".join("-" * w for w in widths))
    for c in cells:
        print("  ".join(v.ljust(w) for v, w in zip(c, widths)))
    if len(rows) > limit:
        print(f"... {len(rows) - limit} more row(s), raise --limit to see them")


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--cypher", help="a read-only Cypher query")
    group.add_argument("--screen", help="screen number or name, e.g. 05 or 05_stale_edges")
    parser.add_argument("--param", action="append", default=[], metavar="KEY=VALUE",
                        help="query parameter, repeatable")
    parser.add_argument("--format", choices=["table", "json"], default="table")
    parser.add_argument("--limit", type=int, default=50, help="rows to print in table mode")
    args = parser.parse_args()

    text = args.cypher if args.cypher else screen_text(args.screen)
    cypher, params = split_params(text)
    for p in args.param:
        if "=" not in p:
            sys.exit(f"--param expects KEY=VALUE, got {p!r}")
        k, v = p.split("=", 1)
        params[k.strip()] = parse_value(v)

    if WRITE_WORDS.search(re.sub(r"//.*", "", cypher)):
        sys.exit("query.py is read-only and this query contains a write keyword. "
                 "Use propose_updates.py and apply_updates.py to change the graph.")

    driver = connect()
    try:
        with driver.session() as session:
            result = session.run(cypher, **params)
            keys = list(result.keys())
            rows = [r.data() for r in result]
    except Exception as exc:
        sys.exit(explain_connection_error(exc))
    finally:
        driver.close()

    if args.format == "json":
        print(json.dumps(rows, indent=2, default=str))
    else:
        print_table(keys, rows, args.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
