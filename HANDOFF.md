# chip-kg: what was built, for the planning chat

Written 2026-09-13 at the end of the build session. Purpose: bring the chat that wrote PLAN.md and CLAUDE.md up to date so it can draft the Thai follower posts. Everything below is in the public repo at github.com/pakornpootranon/chip-kg on main, through commit 3a9ee60.

## 1. What it is, in one paragraph

A Neo4j knowledge graph of 171 listed chip-industry stocks, plus the layers, technologies, countries and chokepoints that connect them, built and maintained entirely with Claude. A follower creates a free Neo4j AuraDB instance, pastes one Cypher file into it, and the whole graph loads from the CSVs on GitHub. They then connect Claude to it through Neo4j's hosted MCP server (a custom connector, no software to install), ask questions in plain English or paste one of four saved prompts, and optionally run a daily Claude scheduled task that reads the news and adds it to the graph as NewsItem nodes with a short morning brief.

## 2. Final stack (what actually shipped)

- Neo4j AuraDB Free. Followers never install Neo4j.
- Loading: `cypher/load.cypher` pasted into the Aura Query editor, reading `data/nodes.csv` and `data/edges.csv` from raw GitHub main. All MERGE. Verified end to end from GitHub on the author's instance: 216 nodes, 869 edges, twice, identical.
- Claude connection: MCP for Aura, the hosted server at `https://<INSTANCE_ID>.mcp-instances.neo4j.io`. Added as a custom connector in claude.ai or Claude Desktop, OAuth login with the Aura account. The author tested this on 2026-09-13 and it works. Needs a paid Claude plan. Fallback for people without custom connectors: the open-source `mcp-neo4j-cypher` server run locally with uvx.
- Python only for the author's plumbing: `scripts/validate.py`, `scripts/load.py`, `scripts/counts.py`. Followers run no Python.
- Scheduling: one prompt, `prompts/daily-news.md`, for both a Cowork scheduled task (followers, runs in the cloud) and a Claude Code Desktop local scheduled task (author, writes `briefs/YYYY-MM-DD.md`). Neither schedule has been created yet; that is the author's next step.
- Hermes is gone. Every Hermes file was deleted; history stays in `data/GAPS.md` v4 and v5 notes only.

## 3. Repo layout as built

```
CLAUDE.md                 rules and ontology (the user's v2 file, unchanged)
PLAN.md                   seven tasks; opens with a "state on adoption" block and carries
                          dated notes on what was done, verified, or left for the author
HANDOFF.md                this file
source/guide.md           the Chip War Essential Guide docx converted to Markdown once
data/universe.csv         171 companies: id, name, ticker, exchange, country, layer, tier,
                          chokepoint, source
data/nodes.csv            216 nodes, all labels in one file, unused columns blank
data/edges.csv            869 edges: from_id, to_id, type, as_of, source, confidence
data/GAPS.md              every judgment call, newest section first
scripts/validate.py       v2 checks, exit 1 with a readable list; run before every commit
scripts/load.py           loader from local CSVs; --reset, --counts
scripts/counts.py         Company count and edges by type as JSON; --diff baseline.json
scripts/build_universe.py the curated universe list; edit and re-run to change it
scripts/build/            batch_a..d.py (rich text per company), assemble_nodes.py,
                          build_edges.py; regenerate both CSVs
cypher/constraints.cypher 12 constraints (id and name per label, NewsItem url)
cypher/reset.cypher       MATCH (n) DETACH DELETE n
cypher/load.cypher        the follower loader, ends with a count check
cypher/screens/01..06     six screens, each with the required comment header
prompts/daily-news.md     the scheduled task prompt
prompts/analysis/         four saved questions to paste into Claude Desktop
briefs/                   gitignored; baseline.json and daily briefs live here locally
docs/README.md            five steps, cost stated up front
docs/aura.md              create instance, paste loader, first query (screenshot placeholders)
docs/mcp.md               MCP for Aura first, uvx fallback, three worked examples
docs/analysis.md          one paragraph per screen and per prompt
docs/schedule.md          Cowork path, Desktop path, how to check nothing else changed
docs/img/                 empty; screenshots still to be taken
```

## 4. The data

Ontology as built (matches CLAUDE.md):

- Company (171): name, ticker, exchange, country, layer, sub_segment, tier, chokepoint, description (one to three sentences), key_products, key_customers, fab_or_ops_geography (lists), source. Ids `co:slug`.
- Layer (10, ordered): EDA, IP, Equipment, Materials, Foundry, IDM, Memory, Packaging, Fabless, EndDemand.
- Technology (10): EUV, DUV, HBM, DRAM, NAND, NOR Flash, CoWoS, GAA, Hybrid Bonding, Silicon Carbide.
- Country (15).
- Chokepoint (10): the guide's seven (EUV Lithography, Advanced Foundry, EDA Software, HBM Memory, Silicon Wafers, Photoresist, Advanced Packaging) plus EUV Mask Inspection, EUV Mask Blanks, ABF Substrate Film.
- NewsItem: url (unique), title, date (YYYY-MM-DD string), summary (two sentences), signal (positive, negative, neutral), ingested_at. Written only by the daily task.

Relationships: OPERATES_IN 171, HQ_IN 171, SUPPLIES 304, COMPETES_WITH 151 (once per pair, lower name first), DEPENDS_ON 53, CONTROLS 19, plus MENTIONS and AFFECTS from NewsItem.

Universe by layer: EDA 7, IP 6, Equipment 32, Materials 21, Foundry 10, IDM 19, Memory 8, Packaging 13, Fabless 37, EndDemand 18. By country: US 73, Taiwan 30, Japan 23, China 19, Germany 7, Netherlands 4, Korea 4, Israel 3, eight others. Tiers: 14 Tier 1, 41 Tier 2, 116 Tier 3. Sixteen companies carry the chokepoint flag.

Tickers are Yahoo style with the primary listing: 2330.TW not TSM, 3711.TW not ASX, 6758.T not SONY. ASML stays bare per the CLAUDE.md example.

How relationships were sourced, honestly: 111 edges come from the guide (source `guide`, confidence high). 40 keep the v1 Bigdata.com source strings. 718 carry source `claude-knowledge` at medium confidence: relationships Claude is confident about from public reporting but did not fetch a URL for. All are dated 2026-09-13, so screen 05 surfaces them as one block when they age. The upgrade path for any edge is a URL in `source` and a new `as_of`. Company nodes cite `guide` (37 of them) or their Yahoo Finance quote page.

Dropped because unlisted: Zeiss SMT, Cymer, JSR, YMTC, Huawei/HiSilicon, Imagination, SiFive, and not added for the same reason: CXMT, SK Siltron, Shinko, Ansys, Alphawave. Their relationships are described in prose in GAPS.md.

## 5. Results a follower will see (good material for posts)

Screen 01, single-source chokepoints: ASML on EUV Lithography (high), Lasertec on EUV Mask Inspection (medium), Ajinomoto on ABF Substrate Film (medium). Advanced Foundry and HBM no longer show because Samsung and Micron are recorded as second controllers.

Screen 02, upstream of NVIDIA, two hops: 53 companies in nine layers. Foundry is TSMC alone. Memory is SK Hynix and Micron. Equipment has nineteen names from ASML and Lasertec (Tier 1) to Camtek and FormFactor (Tier 3). Materials has sixteen including HOYA and Ajinomoto. Packaging shows ASE, Amkor and the substrate makers Ibiden, Unimicron, Nan Ya PCB.

Screen 03, country concentration by headquarters count: Packaging 62 percent Taiwan, Materials 43 percent Japan, EndDemand 83 percent US. The lesson in docs/mcp.md: headquarters count is not capacity share, and Claude will happily add LIMIT 1 to a question that deserves the whole table.

Screen 04, Tier 2 feeding Tier 1: Advantest leads with three (TSMC, SK Hynix, NVIDIA), then Lam Research, SUMCO and Shin-Etsu with two each.

The four prompts (holdings sharing a chokepoint; what breaks if X stops shipping; compare two names; what changed this week) were each executed by a fresh Claude session that saw only the prompt and the MCP tools. All four worked. Example from the first: a portfolio of NVIDIA, ASML, SK Hynix, Advantest and HOYA leans on EUV through four of the five names.

## 6. What is verified and what is not

Verified live on 2026-09-13:

- load.cypher from GitHub on the author's instance after a full reset, counts match the CSVs, second run identical.
- All six screens through MCP.
- All four analysis prompts through the uvx MCP server by fresh agents.
- The daily news prompt by hand (with a seven-day window because nothing verifiable fell inside 24 hours that day): three NewsItem nodes with correct MENTIONS and AFFECTS edges, duplicate MERGE is a no-op, counts.py --diff clean, four-line brief. Those test nodes were wiped in the reload; the graph has zero NewsItem nodes now.
- The MCP for Aura connector in claude.ai, by the author.

Not yet verified:

- The paste-into-Query-editor experience on a truly fresh Aura instance, and the screenshots for docs/aura.md, docs/mcp.md, docs/schedule.md (eleven placeholders, docs/img/ is empty). Needs a second Neo4j account or a paid instance.
- The four prompts through the MCP for Aura connector in Claude Desktop specifically.
- The daily task on a schedule: neither the Cowork task nor the Desktop task has been created. Whether a Cowork scheduled task can use a custom connector is unconfirmed in Anthropic's docs; docs/schedule.md says so and gives the by-hand fallback.
- The fresh-machine follower test and the v1.0 tag (Task 7).

## 7. Quirks worth telling followers

- Aura Free pauses after a few days idle; the connector fails until Resume is clicked in the console.
- On the uvx server the schema tool errors on its first bare call; asking Claude to retry with a sample size fixes it. Every prompt now says so. Not seen on MCP for Aura.
- MCP for Aura has three tools: schema, read, and a separate write tool that is off by default. Followers leave it off for questions and turn it on only for the daily task. Nothing in the repo deletes or edits existing Company nodes or edges.
- The daily task only adds NewsItem nodes. scripts/counts.py --diff (author) or the count query in docs/schedule.md (followers) proves it.
- Web search summaries carry unreliable dates, so the daily prompt requires opening the page to confirm the date and prefers the company's own newsroom.
- COMPETES_WITH is stored once per pair; queries must match it without direction.

## 8. Judgment calls the posts may want to explain

- Tier is the author's picks-and-shovels tier, not market cap. Lasertec, HOYA and Ajinomoto are Tier 1 with the chokepoint flag; DISCO is Tier 1 without it. Western Digital and Seagate kept v1's Tier 1, which looks generous.
- Micron sits in Memory, not IDM. Cirrus Logic, Silicon Labs, Silicon Motion, Phison and Montage are Fabless. Photronics, HOYA and AGC are Materials. Ibiden and Unimicron are Packaging.
- STMicro is CH, Silergy CN, Kulicke and Soffa SG, Linde IE, Wingtech CN.
- Samsung and Micron were added as second controllers of HBM, and Samsung of Advanced Foundry, at medium confidence, matching the guide's own tables where they appear as the second source.
- Foxconn both buys from and supplies NVIDIA; both directions are recorded.
- 171 names is above the 100 minimum on purpose; the author approved the size.

## 9. Suggested post mapping (one post per docs page, per PLAN.md)

1. docs/README.md: what the graph is, what it costs (Neo4j free, Claude paid for the connector), the five steps.
2. docs/aura.md: create the instance, paste the loader, run the first query. Show the 216 and 869.
3. docs/mcp.md: add the custom connector, ask the three worked questions, and the two lessons (check relationship direction and exact names; watch for LIMIT 1 collapsing a table).
4. docs/analysis.md: the six screens and four prompts, with the NVIDIA upstream result and the holdings example.
5. docs/schedule.md: the daily news task, the write switch, and how to check the task only added news.

## 10. How to resume in Claude Code

Open ~/chip-kg, read PLAN.md first (the adoption block and the dated notes), then data/GAPS.md. Run `python scripts/validate.py` before any commit. Regenerate CSVs with `python scripts/build_universe.py`, `python scripts/build/assemble_nodes.py`, `python scripts/build/build_edges.py`. Load with `uv run --with neo4j python scripts/load.py --reset` (reads .env, which exists locally and is gitignored). Check the graph with `scripts/counts.py --diff briefs/baseline.json`. The uvx MCP server `neo4j-cypher` is configured at user scope and points at instance e9b4d268.
