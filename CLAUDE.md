# chip-kg

A Neo4j knowledge graph of 100+ listed chip-industry stocks, built and maintained entirely with Claude. Followers of a Thai Ko-fi series load it into Neo4j AuraDB Free, connect Claude to it through the Neo4j MCP server, ask investment questions in plain language, and run a daily Claude scheduled task that feeds news into the graph.

Everything here is downloaded by non-engineers. One paste, it works.

## Stack (nothing else)

- Neo4j AuraDB Free. Followers never install Neo4j.
- MCP for Aura: Neo4j's hosted MCP server, one URL per instance (`https://<INSTANCE_ID>.mcp-instances.neo4j.io`), available on the Free tier, added to Claude as a custom connector with Aura login. This is the follower path. `mcp-neo4j-cypher` via uvx is the fallback only.
- Python 3.11 with the `neo4j` driver only, for deterministic plumbing (validate, load). No LangChain, no other agents, no messaging bots.
- Scheduling, two paths. Builder (Pootranon): Claude Code Desktop local routine in this repo, writes `briefs/`. Follower: Cowork scheduled task using the MCP for Aura connector, runs remotely with the machine off, brief appears as the task result. Same prompt for both.

## Token discipline for this repo

- Convert the Essential Guide docx to `source/guide.md` once in Task 1. Never read the docx again.
- One task per session. Commit at the end of every task. Start the next task in a fresh session.
- Deterministic work (CSV validation, loading, counting) is Python, not model reasoning.
- Do not re-read files you wrote in this session. Do not summarise progress unprompted.

## Ontology

Labels and required properties:

All nodes carry `id` (unique, prefixed: `co:`, `ly:`, `te:`, `cn:`, `cp:`, `nw:`). Edges reference ids, never names.

- `Company`: `name` (unique), `ticker`, `exchange`, `country`, `layer`, `sub_segment`, `tier` (1/2/3), `chokepoint` (bool), `description` (one to three sentences: what they sell, to whom, why it matters), `key_products` (list), `key_customers` (list), `fab_or_ops_geography` (list), `source` (URL or "guide")
- `Layer`: `name` (unique), `order` (int)
- `Technology`: `name` (unique), e.g. EUV, HBM, CoWoS, GAA, hybrid bonding
- `Country`: `name` (unique), `code` (ISO2)
- `Chokepoint`: `name` (unique), `layer`
- `NewsItem`: `url` (unique), `title`, `date`, `summary` (two sentences), `signal` (positive/negative/neutral), `ingested_at`

Relationships:

- `(Company)-[:OPERATES_IN]->(Layer)`
- `(Company)-[:SUPPLIES]->(Company)`
- `(Company)-[:COMPETES_WITH]->(Company)` (once per pair, lower name first)
- `(Company)-[:DEPENDS_ON]->(Technology)`
- `(Company)-[:HQ_IN]->(Country)`
- `(Company)-[:CONTROLS]->(Chokepoint)`
- `(NewsItem)-[:MENTIONS]->(Company)`
- `(NewsItem)-[:AFFECTS]->(Chokepoint|Technology)`

Every relationship carries `as_of` (ISO date), `source`, `confidence` (high/medium/low).

Layers in order: EDA, IP, Equipment, Materials, Foundry, IDM, Memory, Packaging, Fabless, EndDemand.

Tier is Pootranon's picks-and-shovels tier. Default: Tier 1 controls a chokepoint with one or two competitors worldwide; Tier 2 is a critical supplier with three to five credible competitors; Tier 3 is a commoditised layer. Flag ambiguous cases in `data/GAPS.md` instead of guessing.

## Data rules

- `data/nodes.csv` and `data/edges.csv` are the source of truth. The graph is derived.
- Minimum 100 `Company` nodes, all listed. The universe comes from `data/universe.csv`, which Pootranon supplies or approves before Task 3. Claude Code does at most one web search per company that lacks a source. Never loop over the whole universe searching.
- `Company.country` and `Company.layer` must match the node's HQ_IN and OPERATES_IN targets. validate.py checks this.
- Tickers Yahoo style: US bare (ASML, NVDA), others with suffix (2330.TW, 8035.T, 000660.KS).
- No prices, market caps, or anything that goes stale in a week.
- All loads are `MERGE`. Automated jobs only add `NewsItem` nodes and their edges. They never `DELETE` and never `SET` on existing Company nodes or edges. Stale edges are surfaced by a screen, not removed.
- Follower-facing prose: plain English, no em dashes, no horizontal rules, currency as `$100 m` / `$100 b`.

## Layout

```
source/     guide.md (converted once)
data/       nodes.csv, edges.csv, GAPS.md
cypher/     constraints.cypher, load.cypher, reset.cypher, screens/*.cypher
scripts/    validate.py, load.py
prompts/    daily-news.md (the scheduled task prompt), analysis/*.md (saved questions)
briefs/     YYYY-MM-DD.md written by the daily task (gitignored)
docs/       README.md, aura.md, mcp.md, schedule.md, analysis.md
```

## Working rules

- Follow PLAN.md in order. Stop where it says stop.
- `python scripts/validate.py` must exit 0 before any commit.
- After changing `load.cypher`, reset a fresh Aura instance, reload, and confirm counts through the MCP connection match `validate.py` totals.
- Every screen file opens with a comment: what it finds, why an investor cares, what a hit does and does not mean.
- The daily news prompt must search "the last 24 hours from now" and MERGE on `url`. Scheduled tasks can fire hours late after a missed run; never assume the run time.
- Ask before adding a label, relationship type, layer, or dependency.
