# chip-kg

Public repo for a Thai Ko-fi series teaching individual investors to build a chip-industry knowledge graph in Neo4j and use it for stock screening. Followers download this repo, load it into Neo4j AuraDB Free, and query it by hand, through Claude (Neo4j MCP), and later through a scheduled Hermes Agent job.

Everything here is downloaded and run by non-engineers. Optimise for "paste one thing, it works" over cleverness.

## Stack

- Graph: Neo4j AuraDB Free (cloud). Followers never install Neo4j.
- Load path: `cypher/load.cypher` using `LOAD CSV WITH HEADERS FROM <raw GitHub URL>`. Python loader is the secondary path.
- Python: 3.11+, `neo4j` official driver only. No LangChain, no ORMs.
- Reads from AI: official Neo4j MCP server (`mcp-neo4j-cypher`). Verify the current package name and config format before writing docs; do not assume.
- Scheduled updates: Hermes Agent (Nous Research) cron + a SKILL.md in `skills/kg-update/`. Not OpenClaw.

## Ontology (do not change without asking)

Node labels and required properties:

- `Company` — `name` (unique), `ticker`, `exchange`, `listed` (bool), `tier` (1, 2, 3)
- `Layer` — `name` (unique), `order` (int, upstream to downstream)
- `Technology` — `name` (unique), e.g. EUV, HBM, CoWoS, GAA
- `Country` — `name` (unique), ISO2 `code`
- `Chokepoint` — `name` (unique), `layer` (name of the Layer it sits in)

Relationships:

- `(Company)-[:OPERATES_IN]->(Layer)`
- `(Company)-[:SUPPLIES]->(Company)`
- `(Company)-[:COMPETES_WITH]->(Company)` (write once per pair, lower name first)
- `(Company)-[:DEPENDS_ON]->(Technology)`
- `(Company)-[:HQ_IN]->(Country)`
- `(Company)-[:CONTROLS]->(Chokepoint)`

Every relationship carries three properties, no exceptions: `as_of` (ISO date), `source` (URL or "essential-guide"), `confidence` (high / medium / low).

Layers, in `order`: EDA, IP, Equipment, Materials, Foundry, IDM, Memory, Packaging, Fabless, EndDemand. Keep it at these ten.

Tier is Pootranon's picks-and-shovels tier, not market cap. Default rule until he overrides: Tier 1 = controls a chokepoint with one or two competitors worldwide; Tier 2 = critical supplier with three to five credible competitors; Tier 3 = commoditised layer. Flag any company where the guide is ambiguous rather than guessing.

## Data rules

- `data/nodes.csv` and `data/edges.csv` are the source of truth. The graph is a derived artifact. Never hand-edit Aura and forget to update the CSVs.
- Ticker convention: Yahoo Finance style with exchange suffix for non-US names (2330.TW, 8035.T, 000660.KS). US names bare (ASML, NVDA).
- No market cap, price, or any field that goes stale in a week. Those belong in a screener join, not in the graph.
- Loads use `MERGE`, never `CREATE`, so re-running is safe.
- Automated update flows may only add relationships with a new `as_of`. They never `DELETE`, never `SET` on an existing edge. Stale edges are surfaced by a screen, not removed.
- Source content for the seed graph is Pootranon's own Chip War Essential Guide docx. Do not scrape third-party sites to fill gaps; leave the gap and list it in `data/GAPS.md`.

## Repo layout

```
data/           nodes.csv, edges.csv, GAPS.md
cypher/         constraints.cypher, load.cypher, screens/*.cypher
scripts/        validate.py, load.py (author tools: need the repo checkout)
skills/         kg-update/SKILL.md + kg-update/scripts/{propose_updates,apply_updates,query}.py
                (Hermes, agentskills.io format; self-contained so `hermes skills install <raw URL>`
                works with no git clone — the scripts talk to the live graph, never to data/*.csv,
                except that when run from inside this repo they also sync data/edges.csv)
pending/        proposed update statements awaiting approval (gitignored contents; followers get
                ~/.chip-kg/pending/ instead, see skills/kg-update/SKILL.md)
docs/           follower-facing README in English; Thai posts live elsewhere
```

Credentials use Neo4j's own names everywhere (`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`) so a follower can paste the Aura credentials file as-is. Hermes talks to Neo4j only through the skill's scripts (one credential entry in `~/.hermes/.env`); the MCP server is for Claude Desktop/Code users (`docs/mcp.md`).

## Working rules for this session

- Follow `PLAN.md` in order. Do not start a task whose prerequisite is unchecked.
- Run `python scripts/validate.py` before every commit. It must exit 0.
- After any change to `cypher/load.cypher`, test it on a fresh Aura instance (drop all, reload) and confirm node and edge counts against the CSVs using the Neo4j MCP connection.
- Every `cypher/screens/*.cypher` file starts with a comment block: what the screen finds, why an investor cares, and what a hit does and does not mean.
- Ask before adding a label, relationship type, or layer. Ask before adding any dependency.
- Write follower-facing text in plain English. No em dashes, no horizontal rules. Currency as `$100 m` / `$100 b`.
