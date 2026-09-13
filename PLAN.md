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
- [x] Every Layer has at least three Companies; every Company has exactly one `OPERATES_IN` and one `HQ_IN` — **v2 (2026-09-13)**: expanded from 44→93 Companies (126 total nodes) via Bigdata.com, approved by the author as a second source alongside the guide (see `data/GAPS.md` v2 section for exactly what changed and why). Every layer now has 5+ companies, including `IP` which had zero. **150+ target itself was not pursued further** — 126 is the negotiated v2 baseline, not the original number; author signed off on this size rather than a further push. Live Aura counts reconfirmed via MCP (126 nodes / 264 edges, matches `validate.py`).
- [x] Write `data/GAPS.md` listing every relationship the guide implies but does not state clearly enough to give `confidence: high`
- [x] Present a summary table (nodes per label, edges per type, companies per layer, companies per tier) for Pootranon to review before Task 3 — presented in-session for the v1 74-node graph; Tasks 3-5 proceeded without a formal approval reply, and the v2 expansion above happened with direct author sign-off on the sourcing approach (Bigdata.com) rather than a separate summary-table approval step.

Done when: Pootranon has approved the summary and the tier assignments. Tier assignments are still the least-reviewed part of the file (see `data/GAPS.md` item 5) — flag if any need changing, especially the new EndDemand hyperscaler additions which got a placeholder tier.

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

- [x] `scripts/propose_updates.py`: takes a source URL + a JSON list of proposed edges (the calling agent decides *what* the edges are — this script only validates and renders them), output is `pending/<date>.cypher` containing only `MATCH` + `MERGE` statements that add new edges with inline `as_of`/`source`/`confidence`. Never emits DELETE or a bare SET — enforced by construction plus a self-check before writing. Validates every endpoint exists and matches the ontology's expected label pair, and normalizes `COMPETES_WITH` to lower-name-first automatically.
- [x] `scripts/apply_updates.py`: dry-runs by default; with `--confirm`, re-validates the file (rejects DELETE/SET and any statement not shaped exactly like propose_updates.py's output — a hand-edited file included in testing was correctly refused), applies to Aura, **appends the same rows to `data/edges.csv`** (not in the original task description, but required by CLAUDE.md's "never hand-edit Aura and forget to update the CSVs" rule, since `pending/` is gitignored and would otherwise leave zero permanent trace), then archives the file to `pending/applied/`.
- [x] `skills/kg-update/SKILL.md`: written in valid agentskills.io frontmatter (verified the spec live: only `name`+`description` required, avoid angle brackets) plus Hermes-recognized `metadata.hermes.*` and `required_environment_variables` fields (verified against Hermes's own docs, not assumed). Covers the ontology, the add-only rule, and propose → Telegram → wait for approval → apply → re-run screen 05 → report.
- [x] Hermes cron job text for the README: `hermes cron create "every monday 07:00" ... --skill kg-update`. Flagged honestly rather than guessed: Hermes's schedule strings have no timezone field, so "Asia/Bangkok" can't actually be encoded in the cron command — the README says so and tells the author to match their instance's local clock instead.
- [x] Fallback section: plain cron + the same two scripts, with a caveat that without an LLM doing the news-reading step, the fallback only really suits a manual run against one already-chosen article.

Done when: one full cycle has run on Hermes with a real news item, the diff arrived on Telegram, and the approved edges are visible in the graph via MCP. **Partially met**: no live Hermes account in this session, so the literal Hermes+Telegram round trip is untested — but the full underlying mechanism was proven end to end with two separate real, dated news items (Arm Holdings supplying IP for a Samsung 2nm SoC; ASML confirming TSMC and Samsung as High-NA EUV customers 2 and 3), sourced via live Bigdata.com search, run through propose → dry-run → --confirm → verified live in Aura via MCP → confirmed in `data/edges.csv`. Testing itself caught and fixed one real bug: `apply_updates.py` archived files by source filename only, so two same-day applies would silently clobber each other's archive entry (no data was lost — `edges.csv` already had both — but the audit trail would have been). Now numbers duplicates instead of overwriting.

## Task 8: Morning brief on Hermes (read-only)

Prerequisite: Task 6 done. Independent of Task 7 and may run before it.

- [ ] `skills/kg-morning-brief/SKILL.md`: read-only. Pull `listed = true` Companies and their Layers via MCP; web search the past 24 hours for those names plus chokepoint terms (EUV, HBM, CoWoS, export controls); map each hit to the nodes and relationships it touches; rank by graph impact (single-source Chokepoint > Tier 1 > Tier 2 > Tier 3); deliver five to eight lines; tag items that look like a relationship change as "candidate for kg-update". Never writes to the graph
- [ ] Hermes cron job text for the README: daily 07:00 Asia/Bangkok, deliver to the chat where the job was created
- [ ] `docs/telegram.md`: Path A (Create with QR button in Messaging > Telegram, one screenshot), Path B (BotFather /newbot, @userinfobot for the numeric user ID, setup wizard), keep-the-token-secret warning
- [ ] `docs/provider.md`: which model provider key Hermes needs, where to paste it, and a rough monthly cost estimate for one daily brief

Done when: the brief has arrived on Telegram three mornings in a row from a fresh Hermes profile set up using only `docs/telegram.md` and `docs/provider.md`.
