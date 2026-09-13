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

- [x] Layout from CLAUDE.md, `.gitignore` (briefs/*, .env, __pycache__), `requirements.txt` (neo4j), `.env.example` (kept `NEO4J_USERNAME`, Aura's own name, see adoption note)
- [x] Convert the Essential Guide docx to `source/guide.md` (python-docx via `uv run`, no pandoc on this Mac). 432 blocks, 44 tables, 17 chapters plus appendices. Word count checked against the docx: nothing dropped
- [x] `cypher/constraints.cypher` (id unique per label, name unique per label, NewsItem url unique, 12 constraints) and `cypher/reset.cypher`

Done when: tree matches CLAUDE.md and constraints run clean on Aura via MCP. Done 2026-09-13: all 12 constraints live on the author's Aura instance. Note for docs/mcp.md: the uvx `mcp-neo4j-cypher` server's write tool rejects schema commands ("Only write queries are allowed"), but its read tool runs `CREATE CONSTRAINT` fine. Remaining v1 leftovers to be replaced in Task 4: `load.cypher`, `load.py`, `validate.py` still target the v1 schema.

## Task 2: Company universe (100+)

- [x] Read `data/universe.csv` if Pootranon has supplied it (preferred; built outside this session from his picks, the guide, and an S&P Global screen). If absent, extract every listed company from `source/guide.md` with layer and tier, then fill to 100 with at most one web search per missing company. Done 2026-09-13: not supplied, so built by `scripts/build_universe.py` (the curated list lives in that script; re-run it after editing). 86 listed names carried over from v1 (7 unlisted v1 names dropped: Zeiss SMT, Cymer, JSR, YMTC, Huawei/HiSilicon, Imagination, SiFive) plus 85 additions. No web searches used; 21 less-certain tickers verified through Bigdata.com find_securities instead, the rest from the author's and Claude's knowledge. See `data/GAPS.md` Task 2 notes for every judgment call
- [x] Ensure columns: `id, name, ticker, exchange, country, layer, tier, chokepoint, source`. Ids use the CLAUDE.md `co:` prefix; v1 `c_` ids are migrated in Task 3 when nodes.csv and edges.csv are rewritten
- [x] Print counts per layer, per country, per tier: 171 companies. EDA 7, IP 6, Equipment 32, Materials 21, Foundry 10, IDM 19, Memory 8, Packaging 13, Fabless 37, EndDemand 18. US 73, TW 30, JP 23, CN 19, DE 7, NL 4, KR 4, IL 3, other 12. Tier 1 = 14, Tier 2 = 41, Tier 3 = 116. Chokepoint true = 15. Source "guide" = 37, the rest Yahoo Finance quote URLs

STOP. Pootranon reviews the universe and tiers before any rich data is written.

## Task 3: Rich nodes and edges

- [x] For each approved company write the rich properties into `data/nodes.csv`: `sub_segment, description, key_products, key_customers, fab_or_ops_geography`. Lists pipe-separated. Done 2026-09-13 for all 171 in one session (four batches by layer, assembled by a scratch script; the CSV is the source of truth). Columns: `id,label,name,ticker,exchange,country,layer,sub_segment,tier,chokepoint,description,key_products,key_customers,fab_or_ops_geography,source,order,code`, unused columns blank per label. All ids migrated to `co:` `ly:` `te:` `cn:` `cp:` prefixes
- [x] Add Layer, Technology, Country, Chokepoint rows: 10 layers, 10 technologies (v1's six plus CoWoS, GAA, Hybrid Bonding, Silicon Carbide), 15 countries, 10 chokepoints (guide's seven plus EUV Mask Inspection, EUV Mask Blanks, ABF Substrate Film). 216 nodes total
- [x] `data/edges.csv`: 869 edges. OPERATES_IN 171, HQ_IN 171, SUPPLIES 304, COMPETES_WITH 151, DEPENDS_ON 53, CONTROLS 19. Sources: guide 111, v1 Bigdata.com strings 40, `claude-knowledge` 718 (medium confidence, see GAPS). Four v1 edges dropped because an endpoint is unlisted
- [x] `data/GAPS.md`: every relationship you believed but could not source. Task 3 notes section

Done when: `data/` complete and counts printed. Work in batches of 20 companies per session if context gets heavy; commit after each batch. Done 2026-09-13; the v1 `validate.py` passes on the new files, the v2 checks come in Task 4.

## Task 4: Validate and load

- [x] `scripts/validate.py`: ids unique and correctly prefixed, edge endpoint ids exist, names unique per label, tickers unique, Company.country and Company.layer match HQ_IN and OPERATES_IN targets, every edge has as_of/source/confidence, COMPETES_WITH not duplicated reversed, every Company has one OPERATES_IN and one HQ_IN, list fields parse. Exit 1 with a readable failure list. Done 2026-09-13; also checks edge label shapes, as_of date format, required columns per label, no em dashes in descriptions
- [x] `cypher/load.cypher`: constraints, LOAD CSV from raw GitHub URLs on main, all MERGE. Rewritten for v2: nodes MERGE on `id`, edges MATCH on `id` (no more triple LOAD CSV joins), list fields split on `|`, ends with a count check. Pushed 2026-09-13; the Company node pass and the SUPPLIES edge pass were then run from raw GitHub against the author's instance through MCP and were no-ops on counts (properties re-set, nothing created), so the GitHub path works. The full paste on a second fresh instance is still the STOP test below
- [x] `scripts/load.py`: same from local CSVs. Reads `.env`, has `--reset` and `--counts`, compares live counts to the CSVs and exits 1 on mismatch
- [x] Reset Aura, load, confirm counts via MCP, load again, confirm identical (idempotent). Done 2026-09-13 with `load.py --reset` then `load.py`: 216 nodes, 869 edges both times, confirmed through the MCP connection
- [x] `docs/aura.md`: create a Free instance, copy credentials, paste load.cypher, screenshot each step. Written with five screenshot placeholders under `docs/img/`; Pootranon takes the screenshots during the STOP test below

STOP. Pootranon pastes load.cypher into a second fresh Aura instance himself, as a follower would. Requires `git push` first.

## Task 5: Screens and analysis prompts

Screens in `cypher/screens/`, each with the required comment header:

- [x] `01_single_source_chokepoints` (3 hits: ASML, Lasertec, Ajinomoto)
- [x] `02_upstream_of` (two SUPPLIES hops upstream of a named company, listed only, grouped by layer; NVIDIA gives 53 names in 9 layers)
- [x] `03_country_concentration` per layer
- [x] `04_tier2_feeding_tier1` (Advantest 3, then Lam, SUMCO, Shin-Etsu with 2)
- [x] `05_stale_edges` (as_of older than N months; at 3 months the 37 guide edges from April show)
- [x] `06_news_heat` (companies by count of NewsItem MENTIONS in the last N days, split by signal; runs clean, empty until Task 6)

Analysis prompts in `prompts/analysis/`, one file each, written for a follower to paste into Claude Desktop with the MCP connected:

- [x] `which-of-my-holdings-share-a-chokepoint.md`
- [x] `what-breaks-if-X-stops-shipping.md`
- [x] `compare-two-names-on-the-graph.md`
- [x] `what-changed-this-week.md` (uses NewsItem nodes)

- [x] `docs/mcp.md`: MCP for Aura path first (find the MCP URL in the Aura console under Inspect, add as custom connector in Claude, log in with Aura credentials, screenshots), then the uvx `mcp-neo4j-cypher` fallback. Confirm whether the hosted server exposes write tools; record the answer at the top of the doc. Three worked examples showing the question, the generated Cypher, and the answer. Written 2026-09-13 with three screenshot placeholders; the write-tool answer (yes, separate read-write tool, off by default) is from Neo4j's docs and blog, not yet exercised on this account
- [x] `docs/analysis.md`: one paragraph per screen and per prompt (replaces v1 `docs/screens.md`)

Done when: every screen returns a sensible result and every prompt works from a fresh Claude Desktop session using only docs/mcp.md. Screens verified live through MCP on 2026-09-13. **Not yet done:** the four prompts have not been run from a fresh Claude Desktop session with the MCP for Aura connector; that needs Pootranon's Claude Desktop and the connector set up per docs/mcp.md. Do it together with the Task 4 STOP test.

## Task 6: Daily news task

- [x] `prompts/daily-news.md`: the scheduled task prompt. Opens with: "Use the current time. Search the last 24 hours from now. Skip any item whose url already exists as a NewsItem." Pull all Company names via MCP; web search the last 24 hours for them plus chokepoint terms (EUV, HBM, CoWoS, export controls, advanced packaging); for each relevant item MERGE a NewsItem on url with title, date, two-sentence summary, signal, ingested_at, plus MENTIONS edges to the companies and AFFECTS edges to any Chokepoint or Technology; never touch existing Company nodes or edges; then run screen 06 and write `briefs/YYYY-MM-DD.md` with five to eight lines ranked by graph impact (chokepoint hit > Tier 1 > Tier 2 > Tier 3), each line naming the layer and the listed names it touches
- [x] Run the prompt once manually in Claude Code. Inspect the NewsItem nodes and the brief. Tighten the prompt until the brief is short and the nodes are clean. Done 2026-09-13 with a 7-day window instead of 24 hours (nothing verifiable inside 24 hours that day): three NewsItem nodes (ASML+TSMC 12-inch masks 09-08, NVIDIA Australia 09-09, TSMC August revenue 09-10), MENTIONS and AFFECTS edges correct, duplicate MERGE confirmed to change nothing, `counts.py --diff` clean, brief at `briefs/2026-09-13.md` is four lines. Tightened: date must be confirmed on the article page, primary source preferred, analyst and price stories excluded, duplicate detection wording fixed for both MCP servers
- [ ] Create the builder routine in Claude Code Desktop (Code tab, Scheduled tasks, New task, Local, this repo folder, Daily 07:00, worktree off). Click Run now immediately and select "always allow" on every permission prompt so future runs do not stall. Enable Keep computer awake in Desktop settings. **Pootranon does this in the Desktop app; steps are in docs/schedule.md Path B**
- [x] `scripts/counts.py`: prints Company count and edge count by type. Save the output to `briefs/baseline.json` before the first scheduled run. Done; also has `--diff` which fails if any protected count changed. Baseline saved 2026-09-13 (171 companies, 869 edges) before the manual run
- [x] `docs/schedule.md`: follower path first: Cowork, Scheduled, New task, paste the same prompt, daily, with the MCP for Aura connector enabled; runs remotely with the machine off. Builder path second (Claude Code local routine) with the note that it only fires while Desktop is open and the machine is awake, and that a missed run fires once on wake. Written; the Cowork custom-connector step is unverified until a follower or Pootranon tries it

Done when: three consecutive mornings produce a brief and new NewsItem nodes, and `scripts/counts.py` shows Company count and every non-NewsItem edge type unchanged from baseline.

## Task 7: Follower test and release

- [ ] Fresh machine, fresh Aura, fresh Claude Desktop. Follow docs/ only. Note every point of confusion and fix the doc
- [ ] Tag v1.0

STOP. Thai posts get written after this, using thai-blog-voice, one post per docs page.
