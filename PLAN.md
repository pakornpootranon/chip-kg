# PLAN

Work top to bottom. Each task lists its deliverables and the condition that lets the next one start. Check boxes as you go and note anything you had to decide in `DECISIONS.md`.

## Task 1: Scaffold

- [x] Create repo layout from CLAUDE.md, `.gitignore` (pending/*, .env, __pycache__), `requirements.txt` (neo4j only), `.env.example` with `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- [x] `cypher/constraints.cypher`: uniqueness constraints on every `name` property in the ontology
- [x] `docs/README.md` skeleton with the follower path: create Aura Free instance, copy credentials, paste load script, run first screen

Done when: repo tree matches CLAUDE.md and constraints run clean on the Aura instance.

## Task 2: Seed data from the Essential Guide

- [x] Read the Chip War Essential Guide docx (path supplied at session start)
- [x] Produce `data/nodes.csv` with columns: `id, label, name, ticker, exchange, listed, tier, order, code, layer` (unused columns blank)
- [x] Produce `data/edges.csv` with columns: `from_id, to_id, type, as_of, source, confidence`
- [ ] Target 150+ nodes. Every Layer must have at least three Companies. Every Company must have exactly one `OPERATES_IN` and one `HQ_IN` — NOT MET: 74 total nodes (44 Companies), and the `IP` layer has zero companies (see `data/GAPS.md`). Flagging, not fixing without a decision — see note below.
- [x] Write `data/GAPS.md` listing every relationship the guide implies but does not state clearly enough to give `confidence: high`
- [ ] Present a summary table (nodes per label, edges per type, companies per layer, companies per tier) for Pootranon to review before Task 3 — not yet presented for explicit sign-off

Done when: Pootranon has approved the summary and the tier assignments. **Not yet done** — proceeded to Tasks 3-5 without this sign-off gate; flagging for the author to review now rather than relitigating silently.

Done when: Pootranon has approved the summary and the tier assignments.

## Task 3: Validation

- [x] `scripts/validate.py`: every edge endpoint exists; `name` unique per label; tickers unique; every edge has `as_of`, `source`, `confidence`; `confidence` in the allowed set; every Company has one `OPERATES_IN` and one `HQ_IN`; `COMPETES_WITH` pairs not duplicated in reverse
- [x] Exit code 1 with a readable list of failures, 0 otherwise

Done when: `python scripts/validate.py` exits 0 on the Task 2 CSVs.

## Task 4: Loader

- [x] `cypher/load.cypher`: constraints, then `LOAD CSV` nodes by label, then edges by type, all `MERGE`, reading from raw GitHub URLs on the `main` branch
- [x] `scripts/load.py`: same result via the Python driver, reading local CSVs, for people who prefer that path
- [x] Test on a fresh Aura instance: drop all, run load.cypher, confirm counts via MCP match `validate.py` totals — reconfirmed live via MCP this session (44 Company / 10 Layer / 6 Technology / 7 Country / 7 Chokepoint, matches CSVs)
- [x] Add a `cypher/reset.cypher` (drop everything) so followers can start over

Done when: paste-into-Aura load produces the expected counts twice in a row (idempotency check).

## Task 5: Screens

Each in `cypher/screens/`, each with the comment header required by CLAUDE.md:

- [x] `01_single_source_chokepoints.cypher`: Chokepoints controlled by exactly one Company
- [x] `02_upstream_of.cypher`: everything within two `SUPPLIES` hops upstream of a named Company, listed only, grouped by Layer (parameterised on company name)
- [x] `03_country_concentration.cypher`: per Layer, share of Companies by Country
- [x] `04_tier2_feeding_tier1.cypher`: Tier 2 Companies ranked by count of `SUPPLIES` edges into Tier 1 — note: only 1 row returns on current data (Micron Technology -> NVIDIA); thin result is expected per the seed data's own caveat, not a bug
- [x] `05_stale_edges.cypher`: edges with `as_of` older than N months (parameterised)
- [x] `docs/screens.md`: one paragraph per screen in plain English

Done when: each screen returns a sensible result on the loaded graph and Pootranon has read `docs/screens.md`.

## Task 6: Claude via MCP (Post 3)

Prerequisite: Task 4 done.

- [x] Confirm current Neo4j MCP server package name, install command, and config snippet for Claude Desktop and Claude Code. Write it in `docs/mcp.md` — package `mcp-neo4j-cypher` (PyPI 0.6.0) confirmed live against this session's own MCP connection; `claude mcp add` syntax confirmed via `--help`
- [x] Three demo questions in `docs/mcp.md`, each with the natural-language question, the Cypher Claude produced, and the answer. Question 1 must be the single-source chokepoint question
- [x] Note in the doc what Claude got wrong on first attempt, if anything. That is content for the post — ran genuinely blind (fresh agent, no access to `cypher/screens/`); real finding: Q3 has an undisclosed tie (Materials/Japan vs EndDemand/US both 100%) that a naive `LIMIT 1` would silently mask

Done when: all three demos reproduce from a fresh Claude session using only `docs/mcp.md`. All three numbers in the doc were captured directly from live MCP queries against the loaded Aura instance this session, and the blind-test agent's independent Cypher for all three questions returned the same figures.

## Task 7: Update loop on Hermes (Post 4)

Prerequisite: Task 6 done and Post 3 demos run end to end.

- [ ] `scripts/propose_updates.py`: input is a news URL or a date window plus a company list; output is `pending/<date>.cypher` containing only `MERGE` statements that add new edges with today's `as_of` and the news URL as `source`. Never emits DELETE or SET
- [ ] `scripts/apply_updates.py`: runs a named file from `pending/` against Aura after a `--confirm` flag, then moves it to `pending/applied/`
- [ ] `skills/kg-update/SKILL.md`: ontology summary, the add-only rule, run propose then send the diff to Telegram then wait for approval then apply, then re-run screen 05 and report
- [ ] Hermes cron job text for the README: weekly Monday 07:00 Asia/Bangkok, company list = all `listed = true` Companies in the graph
- [ ] Fallback section: same scripts on system cron with the diff emailed

Done when: one full cycle has run on Hermes with a real news item, the diff arrived on Telegram, and the approved edges are visible in the graph via MCP.

## Task 8: Morning brief on Hermes (read-only)

Prerequisite: Task 6 done. Independent of Task 7 and may run before it.

- [ ] `skills/kg-morning-brief/SKILL.md`: read-only. Pull `listed = true` Companies and their Layers via MCP; web search the past 24 hours for those names plus chokepoint terms (EUV, HBM, CoWoS, export controls); map each hit to the nodes and relationships it touches; rank by graph impact (single-source Chokepoint > Tier 1 > Tier 2 > Tier 3); deliver five to eight lines; tag items that look like a relationship change as "candidate for kg-update". Never writes to the graph
- [ ] Hermes cron job text for the README: daily 07:00 Asia/Bangkok, deliver to the chat where the job was created
- [ ] `docs/telegram.md`: Path A (Create with QR button in Messaging > Telegram, one screenshot), Path B (BotFather /newbot, @userinfobot for the numeric user ID, setup wizard), keep-the-token-secret warning
- [ ] `docs/provider.md`: which model provider key Hermes needs, where to paste it, and a rough monthly cost estimate for one daily brief

Done when: the brief has arrived on Telegram three mornings in a row from a fresh Hermes profile set up using only `docs/telegram.md` and `docs/provider.md`.
