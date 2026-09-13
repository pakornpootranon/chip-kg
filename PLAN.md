# PLAN

One task per Claude Code session. Commit at the end of each. Stop at every "STOP" line and wait for Pootranon.

## State on adoption (2026-09-13)

This plan replaces the Hermes-based v1 plan. The v1 plan, CLAUDE.md and the last Hermes commit are preserved in git at `3b47111`. What v1 already built, and how it maps onto the tasks below:

- `data/nodes.csv`: 126 nodes (93 Company, 10 Layer, 6 Technology, 10 Country, 7 Chokepoint). Ids use `c_`, `l_`, `t_`, `co_`, `ch_` prefixes, not the `co:`, `ly:`, `te:`, `cn:`, `cp:` prefixes in CLAUDE.md. Company rows carry `listed` and `tier` but none of the rich fields; the `layer` column is filled only on Chokepoint rows. Decision for Pootranon before Task 3: migrate ids to the CLAUDE.md prefixes (edges.csv must change in step) or amend CLAUDE.md to the existing ones.
- `data/edges.csv`: 267 edges (93 OPERATES_IN, 93 HQ_IN, 40 COMPETES_WITH, 18 SUPPLIES, 13 CONTROLS, 10 DEPENDS_ON), every edge already has `as_of`, `source`, `confidence`. Source value is `essential-guide`, CLAUDE.md says `guide`.
- Task 2 universe: 93 listed companies exist, so at least 7 more are needed to reach 100. `data/universe.csv` does not exist yet; derive it from nodes.csv or supply it.
- `scripts/validate.py` exists and exits 0 on the v1 checks. Missing the new checks: id prefixes, `Company.country`/`Company.layer` matching HQ_IN and OPERATES_IN targets, list fields parsing.
- `cypher/constraints.cypher`, `reset.cypher`, `load.cypher`, `scripts/load.py` exist for the v1 schema. All must be regenerated for NewsItem, the new Company fields, and any id change.
- `cypher/screens/01` to `05` exist with the required comment headers. `06_news_heat` is new.
- `docs/README.md`, `docs/mcp.md` (uvx path only, no MCP for Aura), `docs/screens.md` (maps to the new `docs/analysis.md`) exist. `docs/aura.md`, `docs/schedule.md`, `prompts/`, `briefs/`, `source/` are new.
- The v1 Hermes files (`skills/`, `pending/`, `docs/hermes.md`, `docs/telegram.md`, `docs/provider.md`) were deleted on adoption. Hermes is out of this build entirely; do not reintroduce it.
- `.env.example` uses `NEO4J_USERNAME` (Aura's own credential file name); Task 1 says `NEO4J_USER`. Keep `NEO4J_USERNAME` so followers can paste the Aura file as is.
- The Essential Guide docx is outside the repo at `~/Downloads/Chip_War_Essential_Guide.docx` (2026-04-19, 35 KB). Task 1 converts it from there.

Live checks done on adoption, so later sessions do not repeat them:

- MCP for Aura: confirmed real and included on the Free tier (announced 2026-07-21). URL is `https://<INSTANCE_ID>.mcp-instances.neo4j.io`, also shown in the Aura console under Instances, the `[...]` menu, Inspect. Auth is a browser OAuth login with the Aura account, no stored credentials. Three tools: get schema, read (read-only Cypher), and a separate read-write tool that is off unless explicitly granted. That answers the Task 5 question: yes, a write tool exists, and the daily news task depends on the follower enabling it. Sources: neo4j.com/docs/mcp/current/mcp-for-aura/ and neo4j.com/blog/genai/introducing-mcp-for-aura/.
- Claude Code Desktop local schedules: the docs call them "Scheduled tasks" (Manual, Hourly, Daily, Weekdays, Weekly). They run only while the Desktop app is open and the machine is awake. A time missed during sleep is skipped, and on restart the app does exactly one catch-up run for the most recent miss within seven days. "Run now" is a button on the task's detail page. "Keep computer awake" is under Settings, Desktop app, General. Source: code.claude.com/docs/en/desktop-scheduled-tasks.
- Cowork scheduled tasks: confirmed to run remotely on a cadence with the machine off, with connectors, skills and plugins available. Paid plans only (Pro, Max, Team, Enterprise). Source: support.claude.com article 13854387.
- Not confirmed from docs: that Cowork scheduled tasks can use a custom (user-added) connector rather than a built-in one. Task 6 must test this with the MCP for Aura connector before `docs/schedule.md` promises it.

## Task 1: Scaffold and source conversion

- [ ] Layout from CLAUDE.md, `.gitignore` (briefs/*, .env, __pycache__), `requirements.txt` (neo4j), `.env.example` (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
- [ ] Convert the Essential Guide docx to `source/guide.md` (pandoc or python-docx). Delete nothing from it
- [ ] `cypher/constraints.cypher` and `cypher/reset.cypher`

Done when: tree matches CLAUDE.md and constraints run clean on Aura via MCP.

## Task 2: Company universe (100+)

- [ ] Read `data/universe.csv` if Pootranon has supplied it (preferred; built outside this session from his picks, the guide, and an S&P Global screen). If absent, extract every listed company from `source/guide.md` with layer and tier, then fill to 100 with at most one web search per missing company
- [ ] Ensure columns: `id, name, ticker, exchange, country, layer, tier, chokepoint, source`
- [ ] Print counts per layer, per country, per tier

STOP. Pootranon reviews the universe and tiers before any rich data is written.

## Task 3: Rich nodes and edges

- [ ] For each approved company write the rich properties into `data/nodes.csv`: `sub_segment, description, key_products, key_customers, fab_or_ops_geography`. Lists pipe-separated
- [ ] Add Layer, Technology, Country, Chokepoint rows
- [ ] `data/edges.csv`: `from_id, to_id, type, as_of, source, confidence`. Every Company gets exactly one OPERATES_IN and one HQ_IN. SUPPLIES and COMPETES_WITH from the guide first, then from the research URLs
- [ ] `data/GAPS.md`: every relationship you believed but could not source

Done when: `data/` complete and counts printed. Work in batches of 20 companies per session if context gets heavy; commit after each batch.

## Task 4: Validate and load

- [ ] `scripts/validate.py`: ids unique and correctly prefixed, edge endpoint ids exist, names unique per label, tickers unique, Company.country and Company.layer match HQ_IN and OPERATES_IN targets, every edge has as_of/source/confidence, COMPETES_WITH not duplicated reversed, every Company has one OPERATES_IN and one HQ_IN, list fields parse. Exit 1 with a readable failure list
- [ ] `cypher/load.cypher`: constraints, LOAD CSV from raw GitHub URLs on main, all MERGE
- [ ] `scripts/load.py`: same from local CSVs
- [ ] Reset Aura, load, confirm counts via MCP, load again, confirm identical (idempotent)
- [ ] `docs/aura.md`: create a Free instance, copy credentials, paste load.cypher, screenshot each step

STOP. Pootranon pastes load.cypher into a second fresh Aura instance himself, as a follower would.

## Task 5: Screens and analysis prompts

Screens in `cypher/screens/`, each with the required comment header:

- [ ] `01_single_source_chokepoints`
- [ ] `02_upstream_of` (two SUPPLIES hops upstream of a named company, listed only, grouped by layer)
- [ ] `03_country_concentration` per layer
- [ ] `04_tier2_feeding_tier1`
- [ ] `05_stale_edges` (as_of older than N months)
- [ ] `06_news_heat` (companies by count of NewsItem MENTIONS in the last N days, split by signal)

Analysis prompts in `prompts/analysis/`, one file each, written for a follower to paste into Claude Desktop with the MCP connected:

- [ ] `which-of-my-holdings-share-a-chokepoint.md`
- [ ] `what-breaks-if-X-stops-shipping.md`
- [ ] `compare-two-names-on-the-graph.md`
- [ ] `what-changed-this-week.md` (uses NewsItem nodes)

- [ ] `docs/mcp.md`: MCP for Aura path first (find the MCP URL in the Aura console under Inspect, add as custom connector in Claude, log in with Aura credentials, screenshots), then the uvx `mcp-neo4j-cypher` fallback. Confirm whether the hosted server exposes write tools; record the answer at the top of the doc. Three worked examples showing the question, the generated Cypher, and the answer
- [ ] `docs/analysis.md`: one paragraph per screen and per prompt

Done when: every screen returns a sensible result and every prompt works from a fresh Claude Desktop session using only docs/mcp.md.

## Task 6: Daily news task

- [ ] `prompts/daily-news.md`: the scheduled task prompt. Opens with: "Use the current time. Search the last 24 hours from now. Skip any item whose url already exists as a NewsItem." Pull all Company names via MCP; web search the last 24 hours for them plus chokepoint terms (EUV, HBM, CoWoS, export controls, advanced packaging); for each relevant item MERGE a NewsItem on url with title, date, two-sentence summary, signal, ingested_at, plus MENTIONS edges to the companies and AFFECTS edges to any Chokepoint or Technology; never touch existing Company nodes or edges; then run screen 06 and write `briefs/YYYY-MM-DD.md` with five to eight lines ranked by graph impact (chokepoint hit > Tier 1 > Tier 2 > Tier 3), each line naming the layer and the listed names it touches
- [ ] Run the prompt once manually in Claude Code. Inspect the NewsItem nodes and the brief. Tighten the prompt until the brief is short and the nodes are clean
- [ ] Create the builder routine in Claude Code Desktop (Code tab, Routines, New routine, Local, this repo folder, Daily 07:00, worktree off). Click Run now immediately and select "always allow" on every permission prompt so future runs do not stall. Enable Keep computer awake in Desktop settings
- [ ] `scripts/counts.py`: prints Company count and edge count by type. Save the output to `briefs/baseline.json` before the first scheduled run
- [ ] `docs/schedule.md`: follower path first: Cowork, Scheduled, New task, paste the same prompt, daily, with the MCP for Aura connector enabled; runs remotely with the machine off. Builder path second (Claude Code local routine) with the note that it only fires while Desktop is open and the machine is awake, and that a missed run fires once on wake

Done when: three consecutive mornings produce a brief and new NewsItem nodes, and `scripts/counts.py` shows Company count and every non-NewsItem edge type unchanged from baseline.

## Task 7: Follower test and release

- [ ] Fresh machine, fresh Aura, fresh Claude Desktop. Follow docs/ only. Note every point of confusion and fix the doc
- [ ] Tag v1.0

STOP. Thai posts get written after this, using thai-blog-voice, one post per docs page.
